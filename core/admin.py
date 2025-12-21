from django.contrib import admin
from .models import ResultadoQuestao

@admin.register(ResultadoQuestao)
class ResultadoQuestaoAdmin(admin.ModelAdmin):
    # Colunas que aparecerão na lista do Admin
    list_display = ('data_resposta', 'topico', 'questao', 'foi_acerto')
    
    # Filtros laterais para facilitar a navegação
    list_filter = ('foi_acerto', 'data_resposta', 'topico__id_materia_fk')
    
    # Campo de busca
    search_fields = ('topico__topico',)
