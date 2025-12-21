from django.contrib import admin
from django.urls import path

# Importamos todas as funções diretamente do core.views
from core.views import (
    home, 
    lista_materias, 
    lista_topicos, 
    detalhe_topico, 
    registrar_estudo, 
    gerar_conteudo_topico,
    salvar_resultado_questao # <--- Certifique-se de que esta função está salva no seu core/views.py
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Dashboard e Navegação
    path('', home, name='home'),
    path('materias/', lista_materias, name='lista_materias'),
    path('topicos/<int:id>/', lista_topicos, name='lista_topicos'),
    path('topico/<int:id>/', detalhe_topico, name='detalhe_topico'),
    
    # Endpoints de API
    path('api/registrar_estudo/', registrar_estudo, name='registrar_estudo'),
    path('api/gerar_conteudo/<int:id_topico>/', gerar_conteudo_topico, name='gerar_conteudo'),
    
    # Rota para salvar os acertos/erros das questões do simulado
    path('salvar-resultado-questao/', salvar_resultado_questao, name='salvar_resultado_questao'),
]