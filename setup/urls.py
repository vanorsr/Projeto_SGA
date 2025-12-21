from django.contrib import admin
from django.urls import path
# Importando as views (incluindo a home)
from core.views import (
    home, 
    lista_materias, 
    lista_topicos, 
    detalhe_topico, 
    registrar_estudo, 
    gerar_conteudo_topico
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # --- ROTA RAIZ (DASHBOARD) ---
    path('', home, name='home'),  # Agora o http://127.0.0.1:8000/ cai aqui!

    # --- MATÉRIAS (Mudei de '' para 'materias/') ---
    path('materias/', lista_materias, name='lista_materias'),

    # --- OUTRAS ROTAS ---
    path('topicos/<int:id>/', lista_topicos, name='lista_topicos'),
    path('topico/<int:id>/', detalhe_topico, name='detalhe_topico'),
    
    # --- API (JSON) ---
    path('api/registrar_estudo/', registrar_estudo, name='registrar_estudo'),
    path('api/gerar_conteudo/<int:id_topico>/', gerar_conteudo_topico, name='gerar_conteudo'),
]