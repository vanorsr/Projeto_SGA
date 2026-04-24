"""
core/ai_utils.py
Módulo de geração de conteúdo via IA.

Arquitetura multi-provider: Gemini como padrão (gratuito), preparado para trocar
por Claude ou outros provedores em 3 linhas.

Para trocar o provider ativo, mude a constante PROVIDER_ATIVO abaixo.
"""
from django.conf import settings
import json
import logging
import re
import time

logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURAÇÃO: troque aqui para mudar de provider
# ============================================================================
PROVIDER_ATIVO = "claude"   # opções: "gemini" | "claude"
MAX_TENTATIVAS = 3          # nº máximo de tentativas em caso de erro transitório
BACKOFF_INICIAL = 2         # segundos — dobra a cada tentativa (2s, 4s, 8s)


# ============================================================================
# PROMPT PEDAGÓGICO (compartilhado entre providers)
# ============================================================================
def _montar_prompt(texto_contexto):
    return f"""
Atue como um professor sênior de cursinho para concursos (foco em concursos de nível superior para as áreas de Analista Administrativo ou similares).
Contexto do assunto: "{texto_contexto}".

REGRAS GERAIS:
- Proibido saudações ou introduções informais.
- PROIBIDO O USO DE LATEX.

FORMATAÇÃO POR CAMPO:
1. **o_que_e, para_que_serve, como_funciona (A TRÍADE):**
   - Use APENAS **negrito** para termos importantes.
   - PROIBIDO o uso de cores (HTML tags) nestes campos.

2. **resumo_curto (APROFUNDAMENTO TEÓRICO):**
   - Use **negrito** + Cores HTML para destacar:
     - VERMELHO (#dc3545): Proibições e Exceções.
     - AZUL (#0d6efd): Prazos e Competências.
     - VERDE (#198754): Requisitos e Deveres.
   - Crie siglas mnemônicas reais para listas, usando <blockquote>.
   - Mínimo de 5 parágrafos densos.
   - Use o prefixo "⚠️ **PEGADINHA:**" para alertas de banca.

3. **GERAÇÃO DE QUESTÕES (SIMULADO DE ELITE):**
   - Gere 3 questões de múltipla escolha (A a E) de nível Difícil.
   - **ESTILO:** Mimetize o estilo de cobrança da banca FGV ou FCC para Analista.
   - **FONTE:** As questões devem ser baseadas EXCLUSIVAMENTE nos detalhes, prazos e exceções descritos no seu campo 'resumo_curto'.
   - No campo 'justificativa', explique o erro das alternativas incorretas e confirme a correta.
   - **REGRA CRÍTICA DE FORMATAÇÃO:** Use APENAS texto puro (plain text) nos campos 'enunciado', 'a', 'b', 'c', 'd', 'e' e 'justificativa'.
   - É TERMINANTEMENTE PROIBIDO o uso de tags HTML (como <span>, <br>, <b>) ou cores dentro do objeto de questões.
   - As cores devem aparecer APENAS no campo 'resumo_curto'.

Responda ESTRITAMENTE no formato JSON abaixo:
{{
    "o_que_e": "...",
    "para_que_serve": "...",
    "como_funciona": "...",
    "resumo_curto": "...",
    "questoes": [
        {{
            "enunciado": "...",
            "a": "...", "b": "...", "c": "...", "d": "...", "e": "...",
            "correta": "A",
            "justificativa": "..."
        }}
    ]
}}
"""


# ============================================================================
# SANITIZAÇÃO DE JSON (compartilhada)
# ============================================================================
def sanitizar_json(texto_cru):
    """Remove blocos markdown ```json e escapa barras invertidas."""
    try:
        texto = texto_cru.strip()
        if texto.startswith("```"):
            linhas = texto.splitlines()
            if linhas[0].startswith("```"):
                linhas = linhas[1:]
            if linhas and linhas[-1].startswith("```"):
                linhas = linhas[:-1]
            texto = "\n".join(linhas).strip()
        texto = re.sub(r'\\(?![\\"/bfnrtu])', r'\\\\', texto)
        return texto
    except Exception as e:
        logger.error(f"Erro na sanitização: {e}")
        return texto_cru


# ============================================================================
# CLASSIFICAÇÃO DE ERROS
# Separa o que vale retry do que não vale.
# ============================================================================
def _classificar_erro(exc):
    """
    Retorna dict com:
      - retry: bool (se vale tentar de novo)
      - codigo: str curto para logs
      - mensagem_usuario: str amigável para exibir ao usuário
    """
    mensagem = str(exc)
    mensagem_lower = mensagem.lower()

    # Sobrecarga temporária do servidor
    if "503" in mensagem or "unavailable" in mensagem_lower or "overloaded" in mensagem_lower:
        return {
            "retry": True,
            "codigo": "SERVIDOR_SOBRECARREGADO",
            "mensagem_usuario": "O serviço de IA está sobrecarregado agora. Tente novamente em alguns minutos.",
        }

    # Quota/rate limit
    if "429" in mensagem or "quota" in mensagem_lower or "rate" in mensagem_lower or "resource_exhausted" in mensagem_lower:
        return {
            "retry": False,
            "codigo": "COTA_EXCEDIDA",
            "mensagem_usuario": "A cota diária da IA foi atingida. Tente novamente mais tarde ou amanhã.",
        }

    # Conteúdo bloqueado por filtro de segurança
    if "safety" in mensagem_lower or "blocked" in mensagem_lower or "finish_reason" in mensagem_lower:
        return {
            "retry": False,
            "codigo": "CONTEUDO_BLOQUEADO",
            "mensagem_usuario": "O conteúdo deste tópico foi bloqueado pelos filtros da IA. Tente reformular ou pular este tópico.",
        }

    # Problemas de rede
    if "timeout" in mensagem_lower or "connection" in mensagem_lower or "network" in mensagem_lower:
        return {
            "retry": True,
            "codigo": "REDE",
            "mensagem_usuario": "Falha de conexão com a IA. Verifique sua internet e tente novamente.",
        }

    # JSON inválido na resposta
    if "json" in mensagem_lower or "expecting" in mensagem_lower:
        return {
            "retry": True,
            "codigo": "JSON_INVALIDO",
            "mensagem_usuario": "A IA retornou um formato inesperado. Tentando novamente costuma resolver.",
        }

    # Erro 400 / argumentos inválidos
    if "400" in mensagem or "invalid" in mensagem_lower:
        return {
            "retry": False,
            "codigo": "ARGUMENTO_INVALIDO",
            "mensagem_usuario": "Não foi possível processar este tópico. Verifique o cadastro do tópico no sistema.",
        }

    # Erro desconhecido — tenta retry por via das dúvidas
    return {
        "retry": True,
        "codigo": "DESCONHECIDO",
        "mensagem_usuario": f"Erro inesperado ao chamar a IA. Tente novamente em alguns instantes.",
    }


# ============================================================================
# PROVIDER: GEMINI
# ============================================================================
def _chamar_gemini(prompt):
    """Chama o Gemini. Lança exceção em caso de erro — retry é tratado fora."""
    from google import genai

    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )

    if not response or not response.text:
        raise ValueError("Resposta vazia do Gemini (possível bloqueio por filtro de segurança).")

    return response.text


# ============================================================================
# PROVIDER: CLAUDE (preparado, não ativo por padrão)
# ============================================================================
def _chamar_claude(prompt):
    """
    Placeholder para Claude (Anthropic).
    Para ativar: instalar `anthropic` no requirements, adicionar ANTHROPIC_API_KEY
    no .env, e trocar PROVIDER_ATIVO = "claude" no topo deste arquivo.
    """
    try:
        import anthropic
    except ImportError:
        raise RuntimeError(
            "Biblioteca 'anthropic' não instalada. Rode: pip install anthropic"
        )

    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )

    if not response.content or not response.content[0].text:
        raise ValueError("Resposta vazia do Claude.")

    return response.content[0].text


# ============================================================================
# DISPATCHER COM RETRY
# ============================================================================
def _chamar_provider_com_retry(prompt):
    """Tenta chamar o provider até MAX_TENTATIVAS vezes em erros transitórios."""
    providers = {
        "gemini": _chamar_gemini,
        "claude": _chamar_claude,
    }

    chamar = providers.get(PROVIDER_ATIVO)
    if not chamar:
        raise RuntimeError(f"Provider desconhecido: {PROVIDER_ATIVO}")

    ultima_excecao = None

    for tentativa in range(1, MAX_TENTATIVAS + 1):
        try:
            logger.info(f"[IA] Tentativa {tentativa}/{MAX_TENTATIVAS} via {PROVIDER_ATIVO}")
            return chamar(prompt)
        except Exception as e:
            ultima_excecao = e
            info = _classificar_erro(e)

            logger.warning(
                f"[IA] Tentativa {tentativa} falhou — código={info['codigo']} — {str(e)[:150]}"
            )

            if not info["retry"] or tentativa == MAX_TENTATIVAS:
                raise

            tempo_espera = BACKOFF_INICIAL * (2 ** (tentativa - 1))
            logger.info(f"[IA] Aguardando {tempo_espera}s antes de nova tentativa...")
            time.sleep(tempo_espera)

    raise ultima_excecao


# ============================================================================
# FUNÇÃO PÚBLICA
# ============================================================================
def gerar_conteudo_ia(texto_contexto):
    """
    Gera conteúdo didático via IA.

    Retorna dict com:
      - success: bool
      - data: dict com o JSON da IA (se sucesso)
      - error_code: str curto (se falha)
      - error_message: str amigável (se falha)

    Faz até MAX_TENTATIVAS_JSON tentativas caso o JSON venha malformado.
    """
    MAX_TENTATIVAS_JSON = 2
    prompt = _montar_prompt(texto_contexto)

    ultimo_erro_json = None

    for tentativa_json in range(1, MAX_TENTATIVAS_JSON + 1):
        try:
            texto_bruto = _chamar_provider_com_retry(prompt)
            logger.info(
                f"[IA] Resposta recebida na tentativa-JSON {tentativa_json}/{MAX_TENTATIVAS_JSON} "
                f"({len(texto_bruto)} caracteres)"
            )

            texto_limpo = sanitizar_json(texto_bruto)
            dados = json.loads(texto_limpo, strict=False)

            return {
                "success": True,
                "data": dados,
            }

        except json.JSONDecodeError as e:
            ultimo_erro_json = e
            logger.warning(
                f"[IA] JSON inválido na tentativa {tentativa_json}/{MAX_TENTATIVAS_JSON}: {e}"
            )
            # Loga um trecho do texto bruto pra diagnóstico
            try:
                preview = texto_bruto[:300] if texto_bruto else "(vazio)"
                logger.warning(f"[IA] Preview do texto recebido: {preview!r}")
            except Exception:
                pass

            # Se ainda tem tentativa, continua o loop
            if tentativa_json < MAX_TENTATIVAS_JSON:
                time.sleep(1)
                continue

            # Última tentativa falhou — retorna erro
            logger.error(f"[IA] JSON inválido após {MAX_TENTATIVAS_JSON} tentativas: {e}")
            return {
                "success": False,
                "error_code": "JSON_INVALIDO",
                "error_message": "A IA retornou um formato inesperado. Tente gerar novamente.",
            }

        except Exception as e:
            info = _classificar_erro(e)
            logger.error(f"[IA] Falha definitiva — código={info['codigo']} — {e}")
            return {
                "success": False,
                "error_code": info["codigo"],
                "error_message": info["mensagem_usuario"],
            }

    # Safety net (não deveria chegar aqui)
    return {
        "success": False,
        "error_code": "JSON_INVALIDO",
        "error_message": "A IA retornou um formato inesperado. Tente gerar novamente.",
    }