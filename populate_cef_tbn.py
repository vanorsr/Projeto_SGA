"""
populate_cef_tbn.py
====================

Popula o edital do concurso CEF — Técnico Bancário Novo (TBN) no SGA.

⚠️ AVISO IMPORTANTE:
Este script é baseado no padrão do edital CEF-TBN 2024 (banca Cesgranrio).
O edital de 2026 ainda não foi publicado oficialmente (previsão: 2º semestre 2026).
Quando o novo edital sair, atualize este script com os ajustes necessários:
  - Pesos das matérias (se houver mudanças)
  - Tópicos novos ou removidos
  - Tópicos específicos do edital novo (ex: novos programas sociais, novos produtos)

Estratégia de reaproveitamento:
- Tópicos já existentes (criados pelo populate_bb.py) são REUTILIZADOS
- Apenas tópicos específicos da CEF são CRIADOS novos
- Cada tópico é associado ao edital CEF via TblEditalLink (não duplica dados)

Uso:
    python populate_cef_tbn.py
"""

import os
import sys
import django

# Configura Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from core.models import (
    TblConcursos,
    TblMaterias,
    TblTopicosMaster,
    TblEditalLink,
)


# ============================================================================
# DADOS DO CONCURSO
# ============================================================================
DADOS_CONCURSO = {
    'nome': 'CEF TBN 2026',
    'nome_abrev': 'CEF',
    'banca': 'Cesgranrio',
    'ano': 2026,
}


# ============================================================================
# ESTRUTURA DE MATÉRIAS E TÓPICOS
# Lista de tuplas: (nome_materia, lista de (topico, nivel_3, prioridade))
#
# Prioridade: ALTA / MEDIA / BAIXA
# ============================================================================
ESTRUTURA = [
    # =====================================================================
    # CONHECIMENTOS BÁSICOS
    # =====================================================================
    ('Língua Portuguesa', [
        ('Compreensão e interpretação de textos', 'Interpretação', 'ALTA'),
        ('Tipologia textual', 'Interpretação', 'MEDIA'),
        ('Ortografia oficial', 'Gramática', 'MEDIA'),
        ('Acentuação gráfica', 'Gramática', 'MEDIA'),
        ('Emprego das classes de palavras', 'Gramática', 'ALTA'),
        ('Emprego e correlação de tempos e modos verbais', 'Gramática', 'ALTA'),
        ('Concordância nominal e verbal', 'Sintaxe', 'ALTA'),
        ('Regência nominal e verbal', 'Sintaxe', 'ALTA'),
        ('Pontuação', 'Sintaxe', 'MEDIA'),
        ('Significação das palavras', 'Semântica', 'MEDIA'),
    ]),

    ('Matemática', [
        ('Operações fundamentais', 'Aritmética', 'MEDIA'),
        ('Razão e proporção', 'Aritmética', 'ALTA'),
        ('Regra de três simples e composta', 'Aritmética', 'ALTA'),
        ('Porcentagem', 'Aritmética', 'ALTA'),
        ('Equações de 1º e 2º grau', 'Álgebra', 'MEDIA'),
        ('Sistemas de equações', 'Álgebra', 'MEDIA'),
        ('Análise combinatória e probabilidade', 'Estatística', 'MEDIA'),
    ]),

    ('Atualidades do Mercado Financeiro', [
        ('Mercado financeiro nacional', 'Mercado', 'ALTA'),
        ('Sistema Financeiro Nacional (SFN)', 'Mercado', 'ALTA'),
        ('Conjuntura econômica brasileira', 'Mercado', 'MEDIA'),
        ('Open banking e Open finance', 'Tecnologia financeira', 'MEDIA'),
        ('PIX e meios de pagamento', 'Tecnologia financeira', 'ALTA'),
    ]),

    # =====================================================================
    # CONHECIMENTOS ESPECÍFICOS
    # =====================================================================
    ('Matemática Financeira', [
        ('Juros simples', 'Juros', 'ALTA'),
        ('Juros compostos', 'Juros', 'ALTA'),
        ('Capitalização e desconto', 'Operações', 'ALTA'),
        ('Taxas de juros (nominal, efetiva, equivalente)', 'Taxas', 'ALTA'),
        ('Sistemas de amortização (SAC, Price)', 'Amortização', 'ALTA'),
    ]),

    ('Conhecimentos Bancários', [
        ('Estrutura do Sistema Financeiro Nacional', 'SFN', 'ALTA'),
        ('Banco Central do Brasil (BACEN)', 'Órgãos', 'ALTA'),
        ('Conselho Monetário Nacional (CMN)', 'Órgãos', 'ALTA'),
        ('CVM, SUSEP e PREVIC', 'Órgãos', 'MEDIA'),
        ('Operações ativas e passivas', 'Operações', 'ALTA'),
        ('Produtos bancários (depósitos, empréstimos, financiamentos)', 'Produtos', 'ALTA'),
        ('Cartões de crédito e débito', 'Produtos', 'MEDIA'),
        ('Crédito imobiliário e SFH', 'Crédito imobiliário', 'ALTA'),
        ('Garantias do crédito (fiança, aval, alienação fiduciária)', 'Garantias', 'ALTA'),
        ('Cheque, ordem de pagamento e DOC/TED', 'Meios de pagamento', 'MEDIA'),
        ('Crime de lavagem de dinheiro (Lei 9.613/98)', 'Compliance', 'ALTA'),
        ('Sigilo bancário (LC 105/2001)', 'Compliance', 'ALTA'),
        ('Autorregulação bancária (FEBRABAN)', 'Compliance', 'MEDIA'),
    ]),

    ('Conhecimentos de Informática', [
        ('Conceitos básicos de hardware e software', 'Fundamentos', 'MEDIA'),
        ('Sistemas operacionais (Windows 10/11)', 'Fundamentos', 'MEDIA'),
        ('Pacote Office: Word', 'Aplicativos', 'ALTA'),
        ('Pacote Office: Excel', 'Aplicativos', 'ALTA'),
        ('Pacote Office: PowerPoint', 'Aplicativos', 'MEDIA'),
        ('Internet, navegadores e correio eletrônico', 'Internet', 'ALTA'),
        ('Conceitos de redes', 'Redes', 'MEDIA'),
        ('Segurança da informação (vírus, phishing, malware)', 'Segurança', 'ALTA'),
        ('Computação em nuvem', 'Tendências', 'MEDIA'),
    ]),

    # =====================================================================
    # MATÉRIAS ESPECÍFICAS DA CEF (não estavam no BB)
    # =====================================================================
    ('Vendas e Atendimento Bancário', [
        ('Técnicas de vendas no contexto bancário', 'Vendas', 'ALTA'),
        ('Atendimento ao cliente', 'Atendimento', 'ALTA'),
        ('Marketing de relacionamento', 'Vendas', 'MEDIA'),
        ('Código de Defesa do Consumidor (Lei 8.078/90)', 'Legislação', 'ALTA'),
        ('Resolução CMN 4.949/2021 (relacionamento com clientes)', 'Legislação', 'MEDIA'),
        ('Ética profissional bancária', 'Ética', 'MEDIA'),
    ]),

    ('Produtos e Serviços CAIXA', [
        ('Programa Casa Verde e Amarela / Minha Casa Minha Vida', 'Habitação', 'ALTA'),
        ('Sistema Financeiro de Habitação (SFH)', 'Habitação', 'ALTA'),
        ('FGTS — Fundo de Garantia do Tempo de Serviço', 'Programas sociais', 'ALTA'),
        ('Programa Bolsa Família', 'Programas sociais', 'MEDIA'),
        ('Auxílio Brasil e benefícios sociais', 'Programas sociais', 'MEDIA'),
        ('PIS-PASEP e abono salarial', 'Programas sociais', 'MEDIA'),
        ('Loterias federais', 'Produtos CAIXA', 'BAIXA'),
        ('Penhor da CAIXA', 'Produtos CAIXA', 'BAIXA'),
    ]),

    ('Legislação e LGPD', [
        ('Lei Geral de Proteção de Dados (LGPD - Lei 13.709/2018)', 'LGPD', 'ALTA'),
        ('Marco Civil da Internet (Lei 12.965/2014)', 'Legislação digital', 'MEDIA'),
        ('Lei de Acesso à Informação (Lei 12.527/2011)', 'Legislação', 'BAIXA'),
        ('Estatuto do Idoso e da Pessoa com Deficiência', 'Legislação', 'MEDIA'),
    ]),
]


# ============================================================================
# FUNÇÃO PRINCIPAL
# ============================================================================
def popular():
    print("\n" + "="*70)
    print("📚 POPULANDO EDITAL: CEF — Técnico Bancário Novo 2026")
    print("="*70)
    print("⚠️  Baseado no padrão do edital CEF-TBN 2024 (Cesgranrio)")
    print("    Atualize quando o edital 2026 for publicado oficialmente.\n")

    # 1. Cria ou pega o concurso
    concurso, criado = TblConcursos.objects.get_or_create(
        nome_concurso=DADOS_CONCURSO['nome'],
        defaults={
            'nomeconc_abrev': DADOS_CONCURSO['nome_abrev'],
            'banca': DADOS_CONCURSO['banca'],
            'ano': DADOS_CONCURSO['ano'],
        }
    )
    if criado:
        print(f"✨ Concurso criado: {concurso.nome_concurso} ({concurso.ano})")
    else:
        print(f"♻️  Concurso já existia: {concurso.nome_concurso}")

    # Contadores
    materias_criadas = 0
    materias_existentes = 0
    topicos_criados = 0
    topicos_reutilizados = 0
    links_criados = 0
    links_existentes = 0

    # 2. Itera pela estrutura
    for nome_materia, topicos in ESTRUTURA:
        # Cria/pega a matéria
        materia, criada = TblMaterias.objects.get_or_create(nome_materia=nome_materia)
        if criada:
            materias_criadas += 1
        else:
            materias_existentes += 1

        for nome_topico, nivel_3, prioridade in topicos:
            # Tenta encontrar o tópico já existente (mesma matéria + mesmo nome)
            topico = TblTopicosMaster.objects.filter(
                id_materia_fk=materia,
                topico=nome_topico,
            ).first()

            if topico:
                topicos_reutilizados += 1
            else:
                topico = TblTopicosMaster.objects.create(
                    id_materia_fk=materia,
                    topico=nome_topico,
                    nivel_3=nivel_3,
                )
                topicos_criados += 1

            # Cria/pega o link entre concurso e tópico
            link, criado = TblEditalLink.objects.get_or_create(
                id_concurso_fk=concurso,
                id_topico_fk=topico,
                defaults={
                    'prioridade_no_edital': prioridade,
                    'esta_no_edital': True,
                }
            )
            if criado:
                links_criados += 1
            else:
                # Atualiza prioridade se já existia
                link.prioridade_no_edital = prioridade
                link.esta_no_edital = True
                link.save()
                links_existentes += 1

    # 3. Resumo final
    print("\n" + "="*70)
    print("✅ POPULAMENTO CONCLUÍDO")
    print("="*70)
    print(f"   Matérias criadas: {materias_criadas}")
    print(f"   Matérias já existentes (reutilizadas): {materias_existentes}")
    print(f"   Tópicos criados (específicos da CEF): {topicos_criados}")
    print(f"   Tópicos reutilizados (já existiam do BB ou outros): {topicos_reutilizados}")
    print(f"   Links de edital criados: {links_criados}")
    print(f"   Links de edital atualizados: {links_existentes}")
    print(f"   Total de tópicos no edital CEF: {links_criados + links_existentes}")
    print(f"\nConfira no admin: http://127.0.0.1:8000/admin/")
    print(f"Ou na home: http://127.0.0.1:8000/\n")


if __name__ == '__main__':
    popular()
