from django.contrib import admin
from .models import (
    TblConcursos,
    TblMaterias,
    TblTopicosMaster,
    TblStatusEstudo,
    TblEditalLink,
    TblMaterialApoio,
    TblSessaoEstudo,
    TblHistoricoEstudo,
    Questao,
    ResultadoQuestao,
)


@admin.register(TblConcursos)
class TblConcursosAdmin(admin.ModelAdmin):
    list_display = ('nomeconc_abrev', 'nome_concurso', 'banca', 'ano')
    search_fields = ('nome_concurso', 'nomeconc_abrev', 'banca')
    list_filter = ('banca', 'ano')


@admin.register(TblMaterias)
class TblMateriasAdmin(admin.ModelAdmin):
    list_display = ('nome_materia', 'nomemat_abrev', 'tipo_conhecimento')
    search_fields = ('nome_materia', 'nomemat_abrev')
    list_filter = ('tipo_conhecimento',)


@admin.register(TblTopicosMaster)
class TblTopicosMasterAdmin(admin.ModelAdmin):
    list_display = ('topico', 'id_materia_fk', 'nivel_3', 'nivel_4')
    search_fields = ('topico', 'nivel_3', 'nivel_4')
    list_filter = ('id_materia_fk',)


@admin.register(TblEditalLink)
class TblEditalLinkAdmin(admin.ModelAdmin):
    list_display = ('id_concurso_fk', 'id_topico_fk', 'prioridade_no_edital', 'esta_no_edital')
    list_filter = ('id_concurso_fk', 'prioridade_no_edital', 'esta_no_edital')


# Registros simples para os demais models
admin.site.register(TblStatusEstudo)
admin.site.register(TblMaterialApoio)
admin.site.register(TblSessaoEstudo)
admin.site.register(TblHistoricoEstudo)
admin.site.register(Questao)


@admin.register(ResultadoQuestao)
class ResultadoQuestaoAdmin(admin.ModelAdmin):
    list_display = ('data_resposta', 'topico', 'questao', 'foi_acerto')
    list_filter = ('foi_acerto', 'data_resposta', 'topico__id_materia_fk')
    search_fields = ('topico__topico',)