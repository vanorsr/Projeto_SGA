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
            # Remove a linha inicial (ex: ```json) e a linha final (```)
            linhas = texto.splitlines()
            if linhas[0].startswith("```"):
                linhas = linhas[1:]
            if linhas[-1].startswith("```"):
                linhas = linhas[:-1]
            texto = "\n".join(linhas).strip()
        
        # 2. Tratamento de barras invertidas para não quebrar o JSON
        # Isso protege contra caracteres especiais que a IA possa enviar
        texto = re.sub(r'\\(?![\\"/bfnrtu])', r'\\\\', texto)
        
        return texto
    except Exception as e:
        return texto_cru

def gerar_conteudo_ia(texto_contexto):
    try:
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        
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
        
        Responda APENAS o objeto JSON:
        {{
            "o_que_e": "...",
            "para_que_serve": "...",
            "como_funciona": "...",
            "resumo_curto": "..."
        }}
        
        ESTRUTURA DO JSON:
        1. **o_que_e:** Definição técnica e concisa.
        2. **para_que_serve:** Aplicação prática em provas.
        3. **como_funciona:** Divisões ou funcionamento do tema.
        4. **resumo_curto:** APROFUNDAMENTO TEÓRICO denso (mínimo 5 parágrafos). 
           - Sempre que possível, inclua um mnemônico usando a tag <blockquote>.
           - Use o prefixo "⚠️ **PEGADINHA:**" para alertas de banca.
        
        Responda APENAS o objeto JSON:
        {{
            "o_que_e": "...",
            "para_que_serve": "...",
            "como_funciona": "...",
            "resumo_curto": "..."
        }}

        """
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        if response and response.text:
            print("\n--- RESPOSTA BRUTA DA IA ---")
            print(response.text) # <--- ISSO VAI NOS MOSTRAR O TEXTO NO TERMINAL
            print("----------------------------\n")
            
            texto_limpo = sanitizar_json(response.text)
            return json.loads(texto_limpo, strict=False)
        return None

    except Exception as e:
        print(f"❌ Erro ao processar JSON: {e}")
        return None