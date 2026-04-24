from google import genai
from django.conf import settings
import json
import logging
import re

logger = logging.getLogger(__name__)

def sanitizar_json(texto_cru):
    try:
        # 1. Limpeza de blocos de código Markdown (as crases ```json ... ```)
        texto = texto_cru.strip()
        if texto.startswith("```"):
            linhas = texto.splitlines()
            if linhas[0].startswith("```"):
                linhas = linhas[1:]
            if linhas[-1].startswith("```"):
                linhas = linhas[:-1]
            texto = "\n".join(linhas).strip()
        
        # 2. Tratamento de barras invertidas para não quebrar o JSON
        texto = re.sub(r'\\(?![\\"/bfnrtu])', r'\\\\', texto)
        
        return texto
    except Exception as e:
        logger.error(f"Erro na sanitização: {e}")
        return texto_cru

def gerar_conteudo_ia(texto_contexto):
    try:
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        
        # PROMPT CONSOLIDADO: Tríade + Aprofundamento + Módulo de Questões
        prompt = f"""
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

        response = client.models.generate_content(
            model="gemini-2.5-flash", 
            contents=prompt
        )

        if response and response.text:
            print("\n--- RESPOSTA BRUTA DA IA ---")
            print(response.text)
            print("----------------------------\n")
            
            texto_limpo = sanitizar_json(response.text)
            return json.loads(texto_limpo, strict=False)
        return None

    except Exception as e:
        print(f"❌ Erro ao processar IA ou JSON: {e}")
        return None