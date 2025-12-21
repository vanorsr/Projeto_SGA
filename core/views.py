from .models import TblMaterias, TblTopicosMaster, TblSessaoEstudo, TblStatusEstudo
from django.db.models import Sum, Count, F, Q
from django.core.serializers.json import DjangoJSONEncoder
import json
import markdown  # <--- CERTIFIQUE-SE DE TER RODADO: pip install markdown
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from django.views.decorators.csrf import csrf_exempt

# Importando seus models
from .models import (
    TblMaterias, 
    TblTopicosMaster, 
    TblMaterialApoio, 
    TblSessaoEstudo, 
    TblConcursos
)

# Importando a função da IA
from core.ai_utils import gerar_conteudo_ia

def lista_materias(request):
    materiais = TblMaterias.objects.all()
    contexto = {'materias': materiais}
    return render(request, 'core/lista_materias.html', contexto)

def lista_topicos(request, id):
    materia = get_object_or_404(TblMaterias, pk=id)
    topico = TblTopicosMaster.objects.filter(id_materia_fk=id)
    contexto = {
        'materia': materia,
        'topicos': topico
    }
    return render(request, 'core/lista_topicos.html', contexto)

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

def gerar_conteudo_topico(request, id_topico):
    if request.method == "POST":
        try:
            # 1. Busca usando o nome EXATO do campo definido no seu Model
            topico = get_object_or_404(TblTopicosMaster, id_topico=id_topico)
            
            contexto_ia = f"Matéria: {topico.id_materia_fk} > "
            if topico.nivel_3: contexto_ia += f"{topico.nivel_3} > "
            if topico.nivel_4: contexto_ia += f"{topico.nivel_4} > "
            contexto_ia += f"Assunto: {topico.topico}"
            
            conteudo = gerar_conteudo_ia(contexto_ia)
            
            if conteudo:
                # 2. Atribuição dos campos (os nomes batem com o seu Model)
                topico.o_que_e = conteudo.get('o_que_e')
                topico.para_que_serve = conteudo.get('para_que_serve')
                topico.como_funciona = conteudo.get('como_funciona')
                topico.resumo_curto = conteudo.get('resumo_curto')
                
                # 3. O Pulo do Gato: Forçar o salvamento
                topico.save()
                
                print(f"✅ Tópico {id_topico} salvo com sucesso no banco!")
                return JsonResponse({"status": "sucesso", "mensagem": "Conteúdo gerado!"})
            else:
                return JsonResponse({"status": "erro", "mensagem": "IA retornou vazio."}, status=500)

        except Exception as e:
            print(f"❌ Erro ao salvar: {e}")
            return JsonResponse({"status": "erro", "mensagem": str(e)}, status=500)
            
    return JsonResponse({"status": "erro", "mensagem": "Método inválido"}, status=400)

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
    # Agora agrupamos pelo TEXTO do status, e não apenas contagem de linhas
    status_query = TblStatusEstudo.objects.values('status').annotate(qtd=Count('id_status'))
    
    labels_status = []
    data_status = []
    
    # Variável para o Card de Resumo (Vai contar só o que REALMENTE começou)
    card_topicos_iniciados = 0 

    for item in status_query:
        # Pega o texto do banco (ex: "Iniciado", "Não Iniciado", "Concluído")
        label = item['status'] 
        if not label: label = "Não Classificado" # Proteção contra nulos
        
        qtd = item['qtd']
        labels_status.append(label)
        data_status.append(qtd)
        
        # LÓGICA DO CARD:
        # Se o status NÃO FOR "Não Iniciado", consideramos como progresso.
        # Dica: Verifique se no seu banco está escrito exatamente "Não Iniciado" (com acento e espaços)
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

    # --- 4. TOTAIS GERAIS (Cards) ---
    total_topicos = TblTopicosMaster.objects.count()
    
    total_tempo_geral = TblSessaoEstudo.objects.aggregate(
        tempo=Sum(F('hora_fim') - F('hora_inicio'))
    )['tempo']
    
    horas_gerais = "0h"
    if total_tempo_geral:
        seg = total_tempo_geral.total_seconds()
        horas_gerais = f"{int(seg//3600)}h {int((seg%3600)//60)}m"
    
    # Cálculo da porcentagem real
    percentual_concluido = 0
    if total_topicos > 0:
        percentual_concluido = round((card_topicos_iniciados / total_topicos) * 100, 1)

    contexto = {
        'horas_gerais': horas_gerais,
        'topicos_iniciados': card_topicos_iniciados, # Agora usa a contagem filtrada
        'total_topicos': total_topicos,
        'percentual_concluido': percentual_concluido,
        
        'chart_horas_labels': json.dumps(labels_horas, cls=DjangoJSONEncoder),
        'chart_horas_data': json.dumps(data_horas, cls=DjangoJSONEncoder),
        
        'chart_status_labels': json.dumps(labels_status, cls=DjangoJSONEncoder),
        'chart_status_data': json.dumps(data_status, cls=DjangoJSONEncoder),
        
        'chart_conhecimento_labels': json.dumps(labels_conhecimento, cls=DjangoJSONEncoder),
        'chart_conhecimento_data': json.dumps(data_conhecimento, cls=DjangoJSONEncoder),
    }
    
    return render(request, 'core/home.html', contexto)