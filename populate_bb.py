"""
populate_bb.py
Popula o banco com a estrutura do edital Banco do Brasil 2022 (Agente Comercial),
base para o concurso BB 2026. Idempotente: pode rodar várias vezes sem duplicar.

Uso (na raiz do projeto, com venv ativado):
    python populate_bb.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

from core.models import (
    TblConcursos,
    TblMaterias,
    TblTopicosMaster,
    TblEditalLink,
)

# ============================================================================
# ESTRUTURA DO EDITAL BB 2022 - AGENTE COMERCIAL
# Base para o próximo edital (2026). Ajustes serão feitos quando o edital sair.
# ============================================================================

ESTRUTURA = {
    # --- CONHECIMENTOS BÁSICOS ---
    'Língua Portuguesa': {
        'abrev': 'PORT',
        'tipo': 'Básicos',
        'prioridade': 'ALTA',  # 10 questões, eliminatória
        'topicos': [
            'Compreensão e interpretação de textos',
            'Tipologia textual',
            'Ortografia oficial',
            'Acentuação gráfica',
            'Emprego das classes de palavras',
            'Emprego e correlação de tempos e modos verbais',
            'Concordância verbal e nominal',
            'Regência verbal e nominal',
            'Pontuação',
            'Redação de correspondências oficiais',
        ],
    },
    'Língua Inglesa': {
        'abrev': 'ING',
        'tipo': 'Básicos',
        'prioridade': 'BAIXA',  # 5 questões, peso menor
        'topicos': [
            'Vocabulário essencial para compreensão de textos',
            'Aspectos gramaticais básicos',
            'Compreensão e interpretação de textos em inglês',
        ],
    },
    'Matemática': {
        'abrev': 'MAT',
        'tipo': 'Básicos',
        'prioridade': 'MEDIA',  # 5 questões × 1,5 pts
        'topicos': [
            'Operações fundamentais',
            'Razão e proporção',
            'Regra de três simples e composta',
            'Porcentagem',
            'Análise combinatória',
            'Probabilidade',
            'Equações do 1º e 2º grau',
            'Funções',
            'Progressão aritmética e geométrica',
        ],
    },
    'Atualidades do Mercado Financeiro': {
        'abrev': 'ATUAL',
        'tipo': 'Básicos',
        'prioridade': 'MEDIA',
        'topicos': [
            'Dinâmica do mercado financeiro brasileiro',
            'Indicadores econômicos (IPCA, Selic, PIB)',
            'Política monetária e Copom',
            'Inflação e taxa de juros',
            'Tendências do mercado bancário',
        ],
    },

    # --- CONHECIMENTOS ESPECÍFICOS (AGENTE COMERCIAL) ---
    'Matemática Financeira': {
        'abrev': 'MATFIN',
        'tipo': 'Específicos',
        'prioridade': 'ALTA',
        'topicos': [
            'Juros simples',
            'Juros compostos',
            'Capitalização e desconto',
            'Taxas de juros nominal, efetiva e equivalentes',
            'Séries uniformes de pagamentos',
            'Sistema de Amortização Constante (SAC)',
            'Sistema Price (Tabela Price)',
            'Fluxo de caixa e valor presente líquido',
        ],
    },
    'Conhecimentos Bancários': {
        'abrev': 'BANC',
        'tipo': 'Específicos',
        'prioridade': 'ALTA',
        'topicos': [
            'Estrutura do Sistema Financeiro Nacional',
            'Conselho Monetário Nacional (CMN)',
            'Banco Central do Brasil (BCB)',
            'Comissão de Valores Mobiliários (CVM)',
            'Moeda e política monetária',
            'Produtos de captação (CDB, LCI, LCA, LF, Poupança)',
            'Conta corrente e conta poupança',
            'Cartões de crédito e débito',
            'Crédito rural',
            'Câmbio',
            'Garantias do SFN: aval, fiança, penhor, alienação fiduciária, hipoteca',
            'Mercado bancário: tesouraria, varejo, recuperação de crédito',
            'Taxas de juros de curto prazo e curva de juros',
            'Crime de lavagem de dinheiro (Lei 9.613/98)',
            'Circular BCB 3.978/2020 (PLD-FT)',
            'Autorregulação bancária e Normativos SARB',
            'Sigilo bancário (LC 105/2001)',
            'LGPD (Lei 13.709/2018)',
            'Legislação anticorrupção (Lei 12.846/2013)',
        ],
    },
    'Conhecimentos de Informática': {
        'abrev': 'INFO',
        'tipo': 'Específicos',
        'prioridade': 'ALTA',
        'topicos': [
            'Sistemas operacionais — Windows 10',
            'Sistemas operacionais — Linux',
            'Edição de textos (MS Word e LibreOffice Writer)',
            'Planilhas (MS Excel e LibreOffice Calc)',
            'Apresentações (MS PowerPoint e LibreOffice Impress)',
            'Redes de computadores: conceitos',
            'Internet: navegadores, correio eletrônico, webconferência',
            'Segurança: malware, phishing, engenharia social',
            'Criptografia, certificação e assinatura digital',
            'Backup e políticas de cópia de segurança',
            'Computação na nuvem',
        ],
    },
    'Vendas e Negociação': {
        'abrev': 'VEND',
        'tipo': 'Específicos',
        'prioridade': 'ALTA',
        'topicos': [
            'Noções de estratégia empresarial',
            'Análise de mercado e forças competitivas',
            'Imagem institucional, identidade e posicionamento',
            'Segmentação de mercado',
            'Valor percebido pelo cliente',
            'Gestão da experiência do cliente',
            'Aprendizagem e sustentabilidade organizacional',
            'Características dos serviços (intangibilidade, inseparabilidade, variabilidade, perecibilidade)',
            'Gestão da qualidade em serviços',
            'Técnicas de vendas: da pré-abordagem ao pós-vendas',
            'Marketing digital: leads, copywriting, gatilhos mentais, inbound',
            'Ética e conduta profissional em vendas',
            'Padrões de qualidade no atendimento',
            'Canais remotos para vendas e telemarketing',
            'Comportamento do consumidor',
            'Política de Relacionamento com o Cliente (Resolução CMN 4.949/2021)',
            'Ouvidoria (Resolução CMN 4.860/2020)',
            'Lei Brasileira de Inclusão (Lei 13.146/2015)',
        ],
    },
}


def run():
    # 1. Garantir que o concurso BB 2026 existe.
    # Procura por qualquer concurso do BB de 2026; se não encontrar, cria.
    concurso = TblConcursos.objects.filter(ano=2026).filter(
        banca__icontains='Cesgranrio'
    ).first()

    if not concurso:
        # Fallback: qualquer concurso de 2026 criado manualmente pelo admin
        concurso = TblConcursos.objects.filter(ano=2026).first()

    if not concurso:
        concurso = TblConcursos.objects.create(
            nome_concurso='Banco do Brasil 2026 - Escriturário Agente Comercial',
            nomeconc_abrev='BB 2026',
            banca='Cesgranrio',
            ano=2026,
        )
        print(f'✨ Concurso criado: {concurso}')
    else:
        print(f'📌 Concurso existente identificado: {concurso}')

    total_m = total_t = total_l = 0

    # 2. Populando matérias, tópicos e ligações ao edital
    for nome_materia, dados in ESTRUTURA.items():
        materia, m_novo = TblMaterias.objects.get_or_create(
            nome_materia=nome_materia,
            defaults={
                'nomemat_abrev': dados['abrev'],
                'tipo_conhecimento': dados['tipo'],
            },
        )
        if m_novo:
            total_m += 1

        for topico_nome in dados['topicos']:
            topico, t_novo = TblTopicosMaster.objects.get_or_create(
                topico=topico_nome,
                id_materia_fk=materia,
            )
            if t_novo:
                total_t += 1

            _, l_novo = TblEditalLink.objects.get_or_create(
                id_concurso_fk=concurso,
                id_topico_fk=topico,
                defaults={
                    'prioridade_no_edital': dados['prioridade'],
                    'esta_no_edital': True,
                },
            )
            if l_novo:
                total_l += 1

    print()
    print('✅ Populamento concluído:')
    print(f'   • {total_m} matérias novas criadas')
    print(f'   • {total_t} tópicos novos criados')
    print(f'   • {total_l} ligações edital→tópico novas')
    print()
    print('Confira no admin: http://127.0.0.1:8000/admin/')


if __name__ == '__main__':
    run()
