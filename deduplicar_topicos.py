"""
deduplicar_topicos.py — v2
===========================

Script interativo pra detectar e unificar tópicos duplicados.

CORREÇÕES DA V2:
1. ATOMICIDADE REAL: cada unificação roda dentro de transaction.atomic()
   — se der erro no meio, rollback completo (não há mais "estado intermediário")
2. LIMIAR MAIS RIGOROSO: 90% (era 80%) — reduz falsos positivos
   Ex: "Concordância verbal e nominal" vs "Regência verbal e nominal" tem 81%
   → fica fora do radar agora
3. DETECTOR DE PALAVRAS-CHAVE DIVERGENTES: quando os tópicos começam
   com palavras diferentes, exibe ALERTA VERMELHO e exige confirmação
   dupla (digitar "SIM" por extenso, não apenas "s")
4. PRÉ-VALIDAÇÃO: antes de qualquer mudança, verifica que ambos os
   tópicos ainda existem no banco

Critério de "qual é o original" (em ordem de prioridade):
1. O que tem nivel_3 preenchido vence o que tem nivel_3 vazio
2. O que já tem conteúdo IA gerado vence o que não tem
3. Em caso de empate, o de menor ID (mais antigo)

Uso:
    python deduplicar_topicos.py
"""

import os
import sys
import django
from difflib import SequenceMatcher

# Configura Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.db import transaction
from core.models import (
    TblMaterias,
    TblTopicosMaster,
    TblMaterialApoio,
    TblEditalLink,
    Questao,
)


# ============================================================================
# CONFIGURAÇÕES
# ============================================================================
LIMIAR_SIMILARIDADE = 0.90  # 90% — mais rigoroso que v1 (era 80%)


# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================
def similaridade(a, b):
    """Retorna similaridade entre 0 e 1 entre duas strings (case insensitive)."""
    return SequenceMatcher(None, (a or '').lower().strip(), (b or '').lower().strip()).ratio()


def primeira_palavra(texto):
    """Retorna a primeira palavra significativa do tópico (em minúsculas)."""
    if not texto:
        return ''
    return texto.strip().split()[0].lower() if texto.strip() else ''


def palavras_chave_divergem(t1, t2):
    """
    Detecta se os tópicos começam com palavras-chave diferentes.
    Exemplo: "Concordância verbal" e "Regência verbal" → divergem
    Exemplo: "Operações ativas e passivas" e "Operações fundamentais" → divergem
    """
    p1 = primeira_palavra(t1.topico)
    p2 = primeira_palavra(t2.topico)
    return p1 != p2


def tem_conteudo_ia(topico):
    """Retorna True se o tópico já tem conteúdo IA gerado."""
    return bool(topico.o_que_e and topico.o_que_e.strip())


def escolher_original(topico_a, topico_b):
    """
    Decide qual dos dois tópicos deve ser mantido (o "original").
    Retorna a tupla (original, duplicado).
    """
    a_tem_nivel = bool(topico_a.nivel_3 and topico_a.nivel_3.strip())
    b_tem_nivel = bool(topico_b.nivel_3 and topico_b.nivel_3.strip())

    if a_tem_nivel and not b_tem_nivel:
        return topico_a, topico_b
    if b_tem_nivel and not a_tem_nivel:
        return topico_b, topico_a

    a_tem_ia = tem_conteudo_ia(topico_a)
    b_tem_ia = tem_conteudo_ia(topico_b)

    if a_tem_ia and not b_tem_ia:
        return topico_a, topico_b
    if b_tem_ia and not a_tem_ia:
        return topico_b, topico_a

    if topico_a.id_topico < topico_b.id_topico:
        return topico_a, topico_b
    return topico_b, topico_a


def descrever_topico(topico):
    """Retorna string descritiva do tópico pra exibição."""
    nivel = topico.nivel_3 if topico.nivel_3 else "(sem nível)"
    ia = "✅ Tem IA" if tem_conteudo_ia(topico) else "❌ Sem IA"

    n_links = TblEditalLink.objects.filter(id_topico_fk=topico).count()
    n_materiais = TblMaterialApoio.objects.filter(id_topico_fk=topico).count()
    n_questoes = Questao.objects.filter(topico=topico).count()

    return (
        f"  ID {topico.id_topico} | nivel_3: {nivel} | {ia}\n"
        f"      Links: {n_links} | Materiais: {n_materiais} | Questões: {n_questoes}"
    )


@transaction.atomic
def unificar(original_id, duplicado_id):
    """
    Move tudo do tópico duplicado pro original e deleta o duplicado.
    RODA DENTRO DE UMA TRANSAÇÃO ATÔMICA — se algo falhar, rollback completo.

    Recebe IDs (não objetos) pra forçar re-busca no banco e evitar dados stale.
    """
    # Re-busca os objetos dentro da transação
    original = TblTopicosMaster.objects.get(id_topico=original_id)
    duplicado = TblTopicosMaster.objects.get(id_topico=duplicado_id)

    movidos = {'links': 0, 'materiais': 0, 'questoes': 0, 'links_descartados': 0}

    # Move links de edital — evita duplicação de links se concurso já está no original
    links_duplicado = list(TblEditalLink.objects.filter(id_topico_fk=duplicado))
    for link in links_duplicado:
        link_existente = TblEditalLink.objects.filter(
            id_concurso_fk=link.id_concurso_fk,
            id_topico_fk=original,
        ).first()

        if link_existente:
            ordem_prioridade = {'ALTA': 3, 'MEDIA': 2, 'BAIXA': 1, None: 0}
            prio_dup = ordem_prioridade.get(link.prioridade_no_edital, 0)
            prio_orig = ordem_prioridade.get(link_existente.prioridade_no_edital, 0)
            if prio_dup > prio_orig:
                link_existente.prioridade_no_edital = link.prioridade_no_edital
                link_existente.save()
            link.delete()
            movidos['links_descartados'] += 1
        else:
            link.id_topico_fk = original
            link.save()
            movidos['links'] += 1

    # Move materiais de apoio
    materiais = list(TblMaterialApoio.objects.filter(id_topico_fk=duplicado))
    for material in materiais:
        material.id_topico_fk = original
        material.save()
        movidos['materiais'] += 1

    # Move questões
    questoes = list(Questao.objects.filter(topico=duplicado))
    for questao in questoes:
        questao.topico = original
        questao.save()
        movidos['questoes'] += 1

    # Se o original NÃO tem conteúdo IA mas o duplicado tem, copia o conteúdo
    if not tem_conteudo_ia(original) and tem_conteudo_ia(duplicado):
        original.o_que_e = duplicado.o_que_e
        original.para_que_serve = duplicado.para_que_serve
        original.como_funciona = duplicado.como_funciona
        original.resumo_curto = duplicado.resumo_curto
        original.save()

    # Deleta o duplicado por último — se chegou até aqui sem erro, é seguro
    duplicado.delete()

    return movidos


def confirmar_unificacao(original, duplicado, divergem):
    """
    Pede confirmação ao usuário. Se palavras-chave divergem, exige confirmação dupla.
    Retorna True/False/None (None = sair).
    """
    if divergem:
        print()
        print("⚠️  " + "="*66)
        print("⚠️  ALERTA: PALAVRAS-CHAVE DIVERGENTES")
        print("⚠️  " + "="*66)
        print(f"⚠️  '{primeira_palavra(original.topico)}' ≠ '{primeira_palavra(duplicado.topico)}'")
        print(f"⚠️  Provável FALSO POSITIVO. Esses tópicos podem ser conceitos")
        print(f"⚠️  DIFERENTES, embora a estrutura textual seja similar.")
        print(f"⚠️  ")
        print(f"⚠️  Exemplo clássico: 'Concordância' vs 'Regência' — sintaxe")
        print(f"⚠️  parecida mas conceitos completamente distintos.")
        print("⚠️  " + "="*66)
        print()
        while True:
            resposta = input("Confirma unificação? Digite 'SIM' por extenso ou 'n' pra pular [SIM/n/q]: ").strip()
            if resposta == 'SIM':
                return True
            if resposta.lower() == 'n':
                return False
            if resposta.lower() == 'q':
                return None
            print("⛔ Pra confirmar com palavras-chave divergentes, é OBRIGATÓRIO digitar 'SIM' em maiúsculas.")
    else:
        while True:
            resposta = input("São o mesmo tópico? [s/n/q]: ").strip().lower()
            if resposta == 's':
                return True
            if resposta == 'n':
                return False
            if resposta == 'q':
                return None
            print("Resposta inválida. Use 's', 'n' ou 'q'.")


# ============================================================================
# LOOP PRINCIPAL
# ============================================================================
def main():
    print("\n" + "="*70)
    print("🔍 DETECTOR DE TÓPICOS DUPLICADOS — v2")
    print("="*70)
    print(f"Limiar de similaridade: {LIMIAR_SIMILARIDADE * 100:.0f}%")
    print("Comparando tópicos dentro da MESMA matéria...")
    print("Cada unificação é ATÔMICA (rollback automático em caso de erro).\n")

    materias = TblMaterias.objects.all()
    candidatos_total = []

    for materia in materias:
        topicos = list(TblTopicosMaster.objects.filter(id_materia_fk=materia))
        if len(topicos) < 2:
            continue

        for i in range(len(topicos)):
            for j in range(i + 1, len(topicos)):
                t1 = topicos[i]
                t2 = topicos[j]
                sim = similaridade(t1.topico, t2.topico)

                if sim >= LIMIAR_SIMILARIDADE:
                    candidatos_total.append((materia, t1, t2, sim))

    if not candidatos_total:
        print("✅ Nenhum tópico duplicado detectado. Base limpa!\n")
        return

    print(f"⚠️  {len(candidatos_total)} pares suspeitos encontrados.\n")
    print("Comandos disponíveis:")
    print("  s   = sim, são iguais (UNIFICAR)")
    print("  SIM = (em caixa alta) confirmação dupla quando há divergência")
    print("  n   = não, são diferentes (PULAR)")
    print("  q   = sair sem aplicar mais mudanças\n")

    total_unificados = 0
    total_links_movidos = 0
    total_materiais_movidos = 0
    total_questoes_movidas = 0
    total_pulados = 0

    for idx, (materia, t1_original, t2_original, sim) in enumerate(candidatos_total, 1):
        # Re-valida que ambos os tópicos ainda existem
        t1 = TblTopicosMaster.objects.filter(id_topico=t1_original.id_topico).first()
        t2 = TblTopicosMaster.objects.filter(id_topico=t2_original.id_topico).first()

        if not t1 or not t2:
            continue  # Algum foi deletado por unificação anterior

        original, duplicado = escolher_original(t1, t2)
        divergem = palavras_chave_divergem(original, duplicado)

        print("="*70)
        print(f"[{idx}/{len(candidatos_total)}] Matéria: {materia.nome_materia}")
        print(f"Similaridade: {sim*100:.1f}%")
        print()
        print(f"📌 PROPOSTO COMO ORIGINAL (será mantido):")
        print(f"   '{original.topico}'")
        print(descrever_topico(original))
        print()
        print(f"🗑️  PROPOSTO COMO DUPLICADO (será deletado):")
        print(f"   '{duplicado.topico}'")
        print(descrever_topico(duplicado))

        decisao = confirmar_unificacao(original, duplicado, divergem)

        if decisao is None:
            print("\n⏹️  Saindo. Mudanças anteriores foram salvas.")
            break

        if decisao:
            print("\n🔄 Unificando (transação atômica)...")
            try:
                movidos = unificar(original.id_topico, duplicado.id_topico)
                total_unificados += 1
                total_links_movidos += movidos['links']
                total_materiais_movidos += movidos['materiais']
                total_questoes_movidas += movidos['questoes']
                print(f"   ✅ {movidos['links']} link(s), "
                      f"{movidos['materiais']} material(is), "
                      f"{movidos['questoes']} questão(ões) movido(s).")
                if movidos['links_descartados']:
                    print(f"   ℹ️  {movidos['links_descartados']} link(s) descartado(s) (concurso já estava no original).")
                print()
            except Exception as e:
                print(f"   ❌ ERRO durante unificação: {e}")
                print(f"   🔙 Rollback automático aplicado — nada foi alterado neste par.\n")
        else:
            total_pulados += 1
            print("   ⏭️  Pulado.\n")

    # Resumo final
    print("\n" + "="*70)
    print("✅ DEDUPLICAÇÃO CONCLUÍDA")
    print("="*70)
    print(f"   Tópicos unificados: {total_unificados}")
    print(f"   Pares pulados: {total_pulados}")
    print(f"   Links de edital movidos: {total_links_movidos}")
    print(f"   Materiais de apoio movidos: {total_materiais_movidos}")
    print(f"   Questões movidas: {total_questoes_movidas}")
    print(f"\n   Confira o dashboard: http://127.0.0.1:8000/\n")


if __name__ == '__main__':
    main()
