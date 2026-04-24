from .models import TblMaterias, TblTopicosMaster, TblSessaoEstudo, TblStatusEstudo, Questao # <--- ADICIONADO QUESTAO
from django.db.models import Sum, Count, F, Q
from django.core.serializers.json import DjangoJSONEncoder
import json
import markdown
import re
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from django.views.decorators.csrf import csrf_exempt
from .models import ResultadoQuestao 

# Importando seus models
from .models import (
    TblMaterias, 
    TblTopicosMaster, 
    TblMaterialApoio, 
    TblSessaoEstudo, 
    TblConcursos,
    ResultadoQuestao # <--- ADICIONADO AQUI TAMBÉM
)

# Importando a função da IA
from core.ai_utils import gerar_conteudo_ia

@login_required
def lista_materias(request):
    materiais = TblMaterias.objects.all()
    contexto = {'materias': materiais}
    return render(request, 'core/lista_materias.html', contexto)

@login_required
def lista_topicos(request, id):
    materia = get_object_or_404(TblMaterias, pk=id)
    topico = TblTopicosMaster.objects.filter(id_materia_fk=id)
    contexto = {
        'materia': materia,
        'topicos': topico
    }
    return render(request, 'core/lista_topicos.html', contexto)

@login_required
def detalhe_topico(request, id):
    # Busca o tópico pelo ID
    topico = get_object_or_404(TblTopicosMaster, id_topico=id)
    
    # Busca o STATUS ATUAL desse tópico (se existir)
    status_atual = TblStatusEstudo.objects.filter(id_topico_fk=topico).first()

    # Lógica dos botões Anterior/Próximo (Mantida igual)
    topico_anterior = TblTopicosMaster.objects.filter(
        id_materia_fk=topico.id_materia_fk, 
        id_topico__lt=topico.id_topico
    ).order_by('-id_topico').first()
    
    proximo_topico = TblTopicosMaster.objects.filter(
        id_materia_fk=topico.id_materia_fk, 
        id_topico__gt=topico.id_topico
    ).order_by('id_topico').first()

    contexto = {
        'topico': topico,
        'status_atual': status_atual,  # <--- AQUI ESTÁ A CHAVE DO SUCESSO! 🗝️
        'anterior': topico_anterior,
        'proximo': proximo_topico,
    }
    
    return render(request, 'core/detalhe_topico.html', contexto)

@login_required
def registrar_estudo(request):
    if request.method == 'POST':
        try:
            dados = json.loads(request.body)
            
            # 1. Captura dados
            id_topico = dados.get('id_topico')
            tempo = dados.get('tempo_segundos')
            questoes = dados.get('qtd_questoes')
            erros = dados.get('qtd_erros')
            novo_nivel = dados.get('nivel_confianca')
            novo_status = dados.get('status_estudo')

            print(f"\n--- 🏁 INICIANDO REGISTRO DO TÓPICO {id_topico} ---")
            print(f"Dados recebidos: Nível={novo_nivel}, Status={novo_status}")

            # 2. Busca o Tópico e Salva a Sessão (Histórico)
            topico = TblTopicosMaster.objects.get(id_topico=id_topico)
            
            sessao = TblSessaoEstudo(
                id_materia_fk=topico.id_materia_fk,
                hora_inicio=timezone.now() - timezone.timedelta(seconds=tempo),
                hora_fim=timezone.now(),
                qtd_questoes=questoes,
                qtd_erros=erros
            )
            sessao.save()
            print("✅ Sessão salva no histórico.")

            # 3. ATUALIZAÇÃO DO STATUS (LÓGICA EXPLÍCITA)
            # Vamos tentar buscar pelo ID_Topico_FK diretamente
            status_existente = TblStatusEstudo.objects.filter(id_topico_fk=topico).first()

            if status_existente:
                print(f"🔄 Registro de status encontrado (ID: {status_existente.id_status}). Atualizando...")
                status_existente.nivel_confianca = novo_nivel
                status_existente.status = novo_status
                status_existente.data_ultima_revisao = timezone.now()
                status_existente.save()
                print("✅ Status atualizado com sucesso!")
            else:
                print("✨ Nenhum status encontrado. Criando novo registro...")
                TblStatusEstudo.objects.create(
                    id_topico_fk=topico,
                    nivel_confianca=novo_nivel,
                    status=novo_status,
                    data_ultima_revisao=timezone.now()
                )
                print("✅ Novo status criado com sucesso!")

            return JsonResponse({'status': 'sucesso', 'mensagem': 'Dados salvos!'})
        
        except Exception as e:
            print(f"❌ ERRO CRÍTICO: {e}")
            return JsonResponse({'status': 'erro', 'mensagem': str(e)}, status=500)
            
    return JsonResponse({'status': 'erro', 'mensagem': 'Método inválido'}, status=400)

@login_required
def gerar_conteudo_topico(request, id_topico):
    if request.method != "POST":
        return JsonResponse({"status": "erro", "mensagem": "Método inválido"}, status=400)
 
    try:
        topico = get_object_or_404(TblTopicosMaster, id_topico=id_topico)
 
        # Monta o contexto hierárquico do tópico
        contexto_ia = f"Matéria: {topico.id_materia_fk} > "
        if topico.nivel_3:
            contexto_ia += f"{topico.nivel_3} > "
        if topico.nivel_4:
            contexto_ia += f"{topico.nivel_4} > "
        contexto_ia += f"Assunto: {topico.topico}"
 
        resultado = gerar_conteudo_ia(contexto_ia)
 
        # --- TRATAMENTO DE ERRO COM MENSAGEM ESPECÍFICA ---
        if not resultado["success"]:
            return JsonResponse(
                {
                    "status": "erro",
                    "codigo_erro": resultado["error_code"],
                    "mensagem": resultado["error_message"],
                },
                status=503 if resultado["error_code"] == "SERVIDOR_SOBRECARREGADO" else 500,
            )
 
        # --- SUCESSO: salva a tríade, aprofundamento e questões ---
        conteudo = resultado["data"]
 
        topico.o_que_e = conteudo.get("o_que_e")
        topico.para_que_serve = conteudo.get("para_que_serve")
        topico.como_funciona = conteudo.get("como_funciona")
        topico.resumo_curto = conteudo.get("resumo_curto")
        topico.save()
 
        # Remove questões antigas e recria com as novas
        Questao.objects.filter(topico=topico).delete()
 
        for q in conteudo.get("questoes", []):
            Questao.objects.create(
                topico=topico,
                enunciado=q.get("enunciado") or "Enunciado não gerado pela IA",
                opcao_a=q.get("a") or q.get("opcao_a") or "Opção A não disponível",
                opcao_b=q.get("b") or q.get("opcao_b") or "Opção B não disponível",
                opcao_c=q.get("c") or q.get("opcao_c") or "Opção C não disponível",
                opcao_d=q.get("d") or q.get("opcao_d") or "Opção D não disponível",
                opcao_e=q.get("e") or q.get("opcao_e") or "Opção E não disponível",
                alternativa_correta=q.get("correta") or q.get("alternativa_correta") or "A",
                justificativa=q.get("justificativa") or "Sem justificativa disponível.",
            )
 
        print(f"✅ Tópico {id_topico} e Simulado salvos com sucesso!")
        return JsonResponse(
            {"status": "sucesso", "mensagem": "Conteúdo e questões gerados!"}
        )
 
    except Exception as e:
        # Erro inesperado (fora do fluxo da IA — ex: DB, permissões)
        print(f"❌ Erro inesperado em gerar_conteudo_topico: {str(e)}")
        return JsonResponse(
            {
                "status": "erro",
                "codigo_erro": "ERRO_INTERNO",
                "mensagem": "Ocorreu um erro inesperado. Tente novamente.",
            },
            status=500,
        )
@login_required
def home(request):
    # --- 1. GRÁFICO: HORAS POR MATÉRIA (Mantido) ---
    horas_por_materia = TblSessaoEstudo.objects.values(
        nome=F('id_materia_fk__nome_materia')
    ).annotate(
        total_tempo=Sum(F('hora_fim') - F('hora_inicio'))
    ).order_by('-total_tempo')

    labels_horas = []
    data_horas = []
    for item in horas_por_materia:
        if item['total_tempo']:
            total_horas = round(item['total_tempo'].total_seconds() / 3600, 2)
            labels_horas.append(item['nome'])
            data_horas.append(total_horas)

    # --- 2. GRÁFICO: STATUS DO ANDAMENTO (CORRIGIDO) ---
    status_query = TblStatusEstudo.objects.values('status').annotate(qtd=Count('id_status'))
    
    labels_status = []
    data_status = []
    card_topicos_iniciados = 0 

    for item in status_query:
        label = item['status'] 
        if not label: label = "Não Classificado"
        
        qtd = item['qtd']
        labels_status.append(label)
        data_status.append(qtd)
        
        if label.strip().lower() != "não iniciado": 
             card_topicos_iniciados += qtd

    # --- 3. GRÁFICO: NÍVEL DE CONHECIMENTO (Mantido) ---
    conhecimento_query = TblStatusEstudo.objects.values('nivel_confianca').annotate(qtd=Count('id_status'))
    
    labels_conhecimento = []
    data_conhecimento = []
    for item in conhecimento_query:
        label = item['nivel_confianca'] or "Não Classificado"
        labels_conhecimento.append(label)
        data_conhecimento.append(item['qtd'])

    # --- 4. NOVAS MÉTRICAS: DESEMPENHO EM QUESTÕES (PASSO 1) ---
    # Buscamos os dados da nova tabela ResultadoQuestao
    total_respostas = ResultadoQuestao.objects.count()
    total_acertos = ResultadoQuestao.objects.filter(foi_acerto=True).count()
    total_erros = ResultadoQuestao.objects.filter(foi_acerto=False).count()

    precisao_geral = 0
    if total_respostas > 0:
        precisao_geral = round((total_acertos / total_respostas) * 100, 1)

    # Preparação para o gráfico de Rosca (Donut)
    chart_simulado_labels = ['Acertos', 'Erros']
    chart_simulado_data = [total_acertos, total_erros]

    # --- 5. TOTAIS GERAIS (Cards) ---
    total_topicos = TblTopicosMaster.objects.count()
    
    total_tempo_geral = TblSessaoEstudo.objects.aggregate(
        tempo=Sum(F('hora_fim') - F('hora_inicio'))
    )['tempo']
    
    horas_gerais = "0h"
    if total_tempo_geral:
        seg = total_tempo_geral.total_seconds()
        horas_gerais = f"{int(seg//3600)}h {int((seg%3600)//60)}m"
    
    percentual_concluido = 0
    if total_topicos > 0:
        percentual_concluido = round((card_topicos_iniciados / total_topicos) * 100, 1)

    # --- 6. CONTEXTO PARA O TEMPLATE ---
    contexto = {
        'horas_gerais': horas_gerais,
        'topicos_iniciados': card_topicos_iniciados,
        'total_topicos': total_topicos,
        'percentual_concluido': percentual_concluido,
        
        # Dados do Simulado (Novos)
        'total_questoes': total_respostas,
        'precisao_geral': precisao_geral,
        'chart_simulado_labels': json.dumps(chart_simulado_labels),
        'chart_simulado_data': json.dumps(chart_simulado_data),
        
        # Gráficos anteriores
        'chart_horas_labels': json.dumps(labels_horas, cls=DjangoJSONEncoder),
        'chart_horas_data': json.dumps(data_horas, cls=DjangoJSONEncoder),
        'chart_status_labels': json.dumps(labels_status, cls=DjangoJSONEncoder),
        'chart_status_data': json.dumps(data_status, cls=DjangoJSONEncoder),
        'chart_conhecimento_labels': json.dumps(labels_conhecimento, cls=DjangoJSONEncoder),
        'chart_conhecimento_data': json.dumps(data_conhecimento, cls=DjangoJSONEncoder),
    }
    
    return render(request, 'core/home.html', contexto)

@login_required
@csrf_exempt
def salvar_resultado_questao(request):
    if request.method == 'POST':
        try:
            dados = json.loads(request.body)
            
            # Print para depuração: veja se esses dados aparecem no seu terminal
            print(f"DEBUG: Recebido questao_id={dados.get('questao_id')}, topico_id={dados.get('topico_id')}, acertou={dados.get('acertou')}")

            # Criando o registro no banco
            ResultadoQuestao.objects.create(
                questao_id=int(dados.get('questao_id')),
                topico_id=int(dados.get('topico_id')),
                foi_acerto=bool(dados.get('acertou'))
            )
            return JsonResponse({'status': 'sucesso'})
        except Exception as e:
            # Isso vai imprimir o erro exato no seu terminal do VS Code/PowerShell
            print(f"❌ ERRO AO SALVAR RESULTADO: {str(e)}")
            return JsonResponse({'status': 'erro', 'mensagem': str(e)}, status=500)
    return JsonResponse({'status': 'metodo_invalido'}, status=400)