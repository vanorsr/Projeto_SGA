# SGA — Roadmap de Evolução

Mapa de melhorias e funcionalidades previstas, sem compromisso de data.
Organizado por categoria e ordenado dentro de cada uma pela sensação de
impacto versus esforço.

---

## 🎯 Inteligência de Recomendação

### Priorização por peso da disciplina no edital
**Status:** ideia mapeada · **Prioridade:** alta

Hoje o Dashboard de Cobertura ordena as matérias apenas por nível de
"urgência" (quanto menos conteúdo gerado, mais urgente). Mas matérias
de peso alto no edital (ex: Conhecimentos Bancários, Informática, Vendas
e Negociação no BB) deveriam ter precedência sobre matérias de peso
baixo (ex: Língua Inglesa) mesmo quando ambas estão pouco cobertas.

**O que já está pronto pra isso:**
- O campo `prioridade_no_edital` existe em `TblEditalLink` (ALTA / MEDIA / BAIXA)
- O `populate_bb.py` já popula essas prioridades corretamente

**O que falta:**
- Calcular a prioridade média de cada matéria no edital ativo
- Cruzar essa prioridade com o percentual de cobertura
- Ordenar matérias considerando ambos fatores — fórmula tipo:
  `score = (peso_no_edital × 2) + urgencia_cobertura`
- Mostrar badge de peso (⭐⭐⭐ / ⭐⭐ / ⭐) em cada linha da tabela
- Talvez uma vista alternativa: "Só matérias de alta prioridade"

**Benefício esperado:**
Quando você tiver 2h disponíveis, o sistema não te direciona pra matéria
"mais vazia", mas pra matéria que **mais vai render na prova**.

---

## ⏱️ Visão Temporal do Esforço

### Horas de estudo na linha do tempo (semanal, mensal, anual)
**Status:** ideia mapeada · **Prioridade:** alta

Hoje o sistema mostra o **total acumulado** de horas por matéria, mas
não mostra **ritmo ao longo do tempo**. Sem essa visão, não dá pra
responder perguntas essenciais:
- "Estudei mais essa semana ou a anterior?"
- "Meu ritmo é suficiente pra chegar na prova com X horas de preparo?"
- "Qual foi meu melhor mês de estudo?"

**O que já está pronto pra isso:**
- A tabela `TblSessaoEstudo` já registra `hora_inicio` e `hora_fim` de
  cada sessão — agregação por data é direta
- Campo `id_materia_fk` permite quebrar por matéria
- Ligação via `TblEditalLink` permite associar sessão a concurso(s)

**Design proposto (a refinar quando implementar):**

1. **Nova seção na home: "⏱️ Ritmo de Estudo"**
   - Três cards no topo: **Esta semana / Este mês / Este ano**, cada um
     com total de horas + variação vs período anterior (↑ 20% / ↓ 5%)
   - Gráfico de barras diário dos últimos 30 dias (padrão de consistência)
   - Gráfico de linha mensal dos últimos 12 meses (tendência)

2. **Filtros:**
   - Seletor de concurso (dropdown) — "BB 2026 / Todos os concursos"
   - Recorte por matéria (opcional)

3. **Métricas secundárias úteis:**
   - **Streak** (dias consecutivos estudando) — ótimo pra gamificação saudável
   - **Dias da semana mais produtivos** (heatmap estilo GitHub)
   - **Média diária** nos últimos 7/30 dias
   - **Projeção**: "Mantendo esse ritmo, até a data da prova você terá X horas"

4. **Detalhes com granularidade:**
   - Clicar numa semana expande pra dias individuais
   - Clicar num mês expande pra semanas
   - Drill-down natural, sem criar telas novas

**Armadilhas a evitar no design:**

- **Não transformar em vaidade:** gráfico bonito que você olha e esquece
  não agrega. Conectar métrica a ação (ex: "ritmo abaixo da média,
  considere reservar 30 min hoje").
- **Não punir folgas saudáveis:** perder streak de 1 dia não pode
  gerar culpa. Linguagem deve ser construtiva, nunca moralista.
- **Não inflar o número:** só contar tempo de **sessões efetivamente
  finalizadas e registradas**, não tempo de app aberto.

**Benefício esperado:**
Junto com a Cobertura (que diz "o que estudar"), a visão temporal diz
"quanto você está estudando" e "se é suficiente" — completam a régua
completa de autogestão.

**Relação com a priorização por peso:**
As duas features juntas viram um produto poderoso. Imagine a home
mostrando: *"Você está estudando 8h/semana, mas só 20% disso em
matérias de peso alto. Sugestão: no próximo bloco, priorize
Conhecimentos Bancários."*

---

## 📚 Estudo e Retenção

### Sistema de Revisão Espaçada (SRS)
**Status:** backlog · **Prioridade:** alta

O campo `data_ultima_revisao` já existe em `TblStatusEstudo` mas não é
usado. Implementar algoritmo FSRS ou SM-2 simplificado que indique quais
tópicos "venceram" a janela de revisão e precisam ser revisitados antes
de avançar. Transforma o sistema de "diário de estudos" em "orientador
de retenção".

### Tela "Estudar Agora" com recomendação contextualizada
**Status:** backlog · **Prioridade:** média

Uma tela/widget na home que responde: "dado que tenho X minutos
disponíveis hoje, qual é a próxima melhor ação?". Combinaria cobertura,
peso, revisões pendentes, ritmo histórico e tempo disponível.

### Flashcards
**Status:** backlog · **Prioridade:** baixa

Feature que existia no Access (SGA antigo) e ainda não foi portada.
Cards de memorização rápida por tópico — útil pra legislação, datas,
prazos e exceções.

---

## 🎨 Experiência e Interface

### Subtópicos (níveis 3, 4, 5) usados na navegação
**Status:** backlog · **Prioridade:** média

O model `TblTopicosMaster` tem `nivel_3`, `nivel_4` e `nivel_5`
implementados, mas a interface usa apenas `topico` e `nivel_3`. A Tela 3
do Access antigo mostrava hierarquia completa com colunas de subtópico.
Reconstruir essa "tela-comando" no SGA.

### Importação de tópicos em massa via interface
**Status:** backlog · **Prioridade:** baixa

Hoje novos editais são carregados via script Python (`populate_bb.py`).
Criar tela web que aceite planilha (CSV/Excel) ou colagem direta de
edital e popule tópicos automaticamente.

### Exportar material em PDF
**Status:** backlog · **Prioridade:** baixa

Gerar um PDF por tópico ou por matéria contendo tríade + aprofundamento
+ questões + materiais de apoio. Útil pra revisão offline ou impressão.

---

## 🔐 Segurança e Multiusuário

### Remover `@csrf_exempt` de `salvar_resultado_questao`
**Status:** dívida técnica · **Prioridade:** baixa

A view já recebe o token CSRF via JavaScript. O `@csrf_exempt` atual é
proteção contra um bug antigo que não existe mais. Remover fortalece a
segurança sem quebrar o fluxo.

### Registro público de novos usuários
**Status:** backlog · **Prioridade:** depende do rumo do produto

Hoje só o admin cria usuários. Se o SGA virar produto, implementar
autocadastro com confirmação de email.

### Convite por link (onboarding controlado)
**Status:** backlog · **Prioridade:** depende do rumo do produto

Meio-termo entre "só admin cria" e "autocadastro aberto". Útil pra
compartilhar com colegas de estudo sem abrir o sistema pro mundo.

---

## ⚙️ Infraestrutura e Qualidade

### Testes automatizados
**Status:** dívida técnica · **Prioridade:** média

Ainda não há testes unitários. Começar pelos pontos críticos:
- `gerar_conteudo_ia` (com mocks do Claude)
- Permissões de `remover_material`
- Cálculos do dashboard de cobertura

### Monitoramento de erros em produção
**Status:** backlog · **Prioridade:** baixa

Sentry (tier gratuito) captura erros 500 automaticamente e manda alerta
por email. Ajudaria a descobrir bugs que o usuário nem reportou.

### Fallback automático de provedor de IA
**Status:** backlog · **Prioridade:** baixa

A arquitetura multi-provider já está pronta (pode trocar Gemini ↔ Claude
alterando 1 variável). Evoluir pra fallback automático: tenta Gemini
(gratuito) → se der 503 repetido, cai pro Claude (pago) → se o Claude
também falhar, erro amigável pro usuário.

### Upgrade de RAM pra desbloquear geração IA em produção
**Status:** aguardando gatilho financeiro · **Prioridade:** média

Hoje a geração de conteúdo IA precisa ser feita localmente porque o
Render Free de 512 MB não aguenta o pico de memória. O plano Padrão
(US$25/mês, 2GB) elimina essa limitação. Revisitar quando o SGA tiver
mais usuários, virar fonte de receita ou o estudo exigir geração no
tablet com frequência.

---

## 🧭 Produto e Estratégia

### Decisão futura: SGA permanece pessoal ou vira produto?
**Status:** em observação

O SGA foi construído como ferramenta pessoal de estudo, separado
estrategicamente da ElevaMind. Se os resultados pessoais forem bons
(aprovação no BB, TRT, etc.) e outros concurseiros demonstrarem
interesse, avaliar:
- Posicionamento (nicho de RH? concursos em geral?)
- Modelo de monetização (freemium? assinatura?)
- Time de conteúdo humano ou IA-first?
- Identidade visual própria (hoje usa paleta emprestada da ElevaMind)

**Quando revisitar:** após 3 meses de uso consistente.

---

*Última atualização: abril/2026*
