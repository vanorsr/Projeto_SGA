import markdown # Certifique-se de ter o 'markdown' instalado no venv
from django.db import models
from django.utils.safestring import mark_safe

# =======================================================
# 1º: TABELAS INDEPENDENTES (Que não dependem de ninguém)
# =======================================================

class TblConcursos(models.Model):
    # Cole aquela estrutura que você me mandou aqui, NO TOPO
    id_concurso = models.AutoField(db_column='ID_Concurso', primary_key=True)
    nome_concurso = models.CharField(db_column='Nome_Concurso', max_length=255, blank=True, null=True)
    nomeconc_abrev = models.CharField(db_column='NomeConc_Abrev', max_length=255, blank=True, null=True)
    banca = models.CharField(db_column='Banca', max_length=255, blank=True, null=True)
    ano = models.IntegerField(db_column='Ano', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tbl_Concursos'
        verbose_name = 'Concurso'
        verbose_name_plural = 'Concursos'
    
    def __str__(self):
        return f"{self.nomeconc_abrev} ({self.ano})"
    
class TblMaterias(models.Model):
    id_materia = models.AutoField(db_column='ID_Materia', primary_key=True)
    nome_materia = models.CharField(db_column='Nome_Materia', max_length=255, blank=True, null=True)
    nomemat_abrev = models.CharField(db_column='NomeMat_Abrev', max_length=255, blank=True, null=True)
    tipo_conhecimento = models.CharField(db_column='Tipo_Conhecimento', max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tbl_Materias'
        verbose_name = 'Matéria'
        verbose_name_plural = 'Matérias'

    def __str__(self):
        return self.nome_materia or "Matéria sem nome"
    
class TblStatusEstudo(models.Model):
    id_status = models.AutoField(db_column='ID_Status', primary_key=True)
    # Aponte para 'TblTopicosMaster' (com aspas se a classe estiver definida DEPOIS desta, ou sem aspas se antes)
    id_topico_fk = models.ForeignKey('TblTopicosMaster', models.DO_NOTHING, db_column='ID_Topico_FK', blank=True, null=True)
    
    status = models.CharField(db_column='Status', max_length=255, blank=True, null=True)
    nivel_confianca = models.CharField(db_column='Nivel_Confianca', max_length=255, blank=True, null=True)
    data_ultima_revisao = models.DateTimeField(db_column='Data_Ultima_Revisao', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tbl_Status_Estudo'
        verbose_name = 'Status do Estudo'


class TblTopicosMaster(models.Model):
    id_topico = models.AutoField(db_column='ID_Topico', primary_key=True)
    id_materia_fk = models.ForeignKey('TblMaterias', models.DO_NOTHING, db_column='ID_Materia_FK', blank=True, null=True)
    topico = models.CharField(db_column='Topico', max_length=255, blank=True, null=True)
    nivel_3 = models.CharField(db_column='Nivel_3', max_length=255, blank=True, null=True)
    nivel_4 = models.CharField(db_column='Nivel_4', max_length=255, blank=True, null=True)
    nivel_5 = models.CharField(db_column='Nivel_5', max_length=255, blank=True, null=True)
    o_que_e = models.TextField(db_column='O_Que_E', blank=True, null=True)
    para_que_serve = models.TextField(db_column='Para_Que_Serve', blank=True, null=True)
    como_funciona = models.TextField(db_column='Como_Funciona', blank=True, null=True)
    resumo_curto = models.TextField(db_column='Resumo_Curto', blank=True, null=True)
    conteudo_mestre = models.TextField(db_column='CONTEUDO_MESTRE', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tbl_Topicos_Master'
        verbose_name = 'Tópico'
        verbose_name_plural = 'Tópicos Master'

    def __str__(self):
        return self.topico or "Tópico sem nome"

    # --- PROPRIEDADES PARA O HTML ---
    # Essas funções transformam o texto bruto da IA em HTML formatado
    
    @property
    def o_que_e_html(self):
        if self.o_que_e:
            return mark_safe(markdown.markdown(self.o_que_e))
        return None

    @property
    def para_que_serve_html(self):
        if self.para_que_serve:
            return mark_safe(markdown.markdown(self.para_que_serve))
        return None

    @property
    def como_funciona_html(self):
        if self.como_funciona:
            return mark_safe(markdown.markdown(self.como_funciona))
        return None

    @property
    def resumo_curto_html(self):
        if self.resumo_curto:
            return mark_safe(markdown.markdown(self.resumo_curto))
        return None


class TblEditalLink(models.Model):
    id_link = models.AutoField(db_column='ID_Link', primary_key=True)
    id_concurso_fk = models.ForeignKey(TblConcursos, models.DO_NOTHING, db_column='ID_Concurso_FK', blank=True, null=True)
    id_topico_fk = models.ForeignKey(TblTopicosMaster, models.DO_NOTHING, db_column='ID_Topico_FK', blank=True, null=True)
    prioridade_no_edital = models.CharField(db_column='Prioridade_no_Edital', max_length=255, blank=True, null=True)
    esta_no_edital = models.BooleanField(db_column='Esta_No_Edital', blank=True, null=True)
    ssma_timestamp = models.TextField(db_column='SSMA_TimeStamp', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tbl_Edital_Link'


class TblMaterialApoio(models.Model):
    id_material = models.AutoField(db_column='ID_Material', primary_key=True)
    id_topico_fk = models.ForeignKey(TblTopicosMaster, models.DO_NOTHING, db_column='ID_Topico_FK', blank=True, null=True)
    descricao = models.CharField(db_column='Descricao', max_length=255, blank=True, null=True)
    link_conteudo = models.TextField(db_column='link_Conteudo', blank=True, null=True)
    tipo_material = models.CharField(db_column='Tipo_Material', max_length=255, blank=True, null=True)
    duracao_minutos = models.IntegerField(db_column='Duracao_Minutos', blank=True, null=True)
    ssma_timestamp = models.TextField(db_column='SSMA_TimeStamp', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tbl_Material_Apoio'

class TblSessaoEstudo(models.Model):
    id_sessao = models.AutoField(db_column='ID_Sessao', primary_key=True)
    
    # FK para Matéria
    id_materia_fk = models.ForeignKey(TblMaterias, models.DO_NOTHING, db_column='ID_Materia_FK', blank=True, null=True)
    
    # 👇 FK para Concurso (AQUI ESTÁ A MUDANÇA)
    id_concurso_fk = models.ForeignKey(TblConcursos, models.DO_NOTHING, db_column='ID_Concurso_FK', blank=True, null=True)
    
    hora_inicio = models.DateTimeField(db_column='Hora_Inicio', blank=True, null=True)
    hora_fim = models.DateTimeField(db_column='Hora_Fim', blank=True, null=True)
    
    # Campos novos que criamos via script
    qtd_questoes = models.IntegerField(db_column='Qtd_Questoes', blank=True, null=True)
    qtd_erros = models.IntegerField(db_column='Qtd_Erros', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tbl_Sessao_Estudo'
        verbose_name = 'Sessão de Estudo'
        verbose_name_plural = 'Sessões de Estudo'

    def __str__(self):
        return f"Sessão {self.id_sessao}"


class TblHistoricoEstudo(models.Model):
    id_historico = models.AutoField(primary_key=True)
    id_topico_fk = models.ForeignKey(TblTopicosMaster, on_delete=models.CASCADE, db_column='id_topico_fk')
    data_estudo = models.DateTimeField(auto_now_add=True)
    tempo_segundos = models.IntegerField()
    
    class Meta:
        db_table = 'tbl_Sessao_Estudo' # Verifique se esta tabela no SQL Server é a mesma de TblSessaoEstudo
        managed = False
        verbose_name = 'Histórico de Estudo'
        verbose_name_plural = 'Histórico de Estudos'

    def __str__(self):
        return f"{self.data_estudo} - {self.id_topico_fk.topico} ({self.tempo_segundos}s)"

# FORA da classe anterior, na margem esquerda:
class Questao(models.Model):
    # Usamos 'TblTopicosMaster' pois é o nome da sua tabela de tópicos
    topico = models.ForeignKey('TblTopicosMaster', on_delete=models.CASCADE, related_name='questoes')
    enunciado = models.TextField()
    opcao_a = models.TextField()
    opcao_b = models.TextField()
    opcao_c = models.TextField()
    opcao_d = models.TextField()
    opcao_e = models.TextField()
    alternativa_correta = models.CharField(max_length=1) 
    justificativa = models.TextField()

    class Meta:
        managed = True # O Django vai criar esta tabela para você
        verbose_name = 'Questão'
        verbose_name_plural = 'Questões'

    def __str__(self):
        # Usamos .topico pois é o campo nome no seu TblTopicosMaster
        return f"Questão {self.id} - {self.topico.topico}"
    
class ResultadoQuestao(models.Model):
    # Relacionamentos
    questao = models.ForeignKey('Questao', on_delete=models.CASCADE, related_name='resultados')
    topico = models.ForeignKey('TblTopicosMaster', on_delete=models.CASCADE, related_name='resultados_questoes')
    
    # Dados da performance
    foi_acerto = models.BooleanField() # True para acerto, False para erro
    data_resposta = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'tbl_Resultados_Questoes' # Nome da tabela no SQL Server
        managed = True
        verbose_name = 'Resultado de Questão'
        verbose_name_plural = 'Resultados de Questões'

    def __str__(self):
        status = "Acerto" if self.foi_acerto else "Erro"
        return f"{status} - {self.topico.topico} ({self.data_resposta.strftime('%d/%m/%Y')})"