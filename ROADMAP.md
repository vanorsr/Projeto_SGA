# SGA — Roadmap de Evolução

Mapa de melhorias e funcionalidades previstas, sem compromisso de data.
Organizado por categoria e ordenado dentro de cada uma pela sensação de
impacto versus esforço.

---

## 🎯 Inteligência de Recomendação

### Dropdown de seleção de concurso (filtro multi-edital)
**Status:** ideia mapeada · **Prioridade:** alta · **Gatilho:** antes do uso real do segundo concurso

A partir do momento que o SGA tiver mais de um concurso ativo (ex: BB + CEF),
o dashboard atual perde poder informativo: a "cobertura" passa a misturar
tópicos de editais diferentes, escondendo o estado real de cada um.

**Comportamento esperado:**
- Dropdown no topo da home com opções: "BB 2026 / CEF TBN 2026 / Todos os concursos"
- Padrão: "Todos os concursos" (compatível com uso atual)
- Seleção persiste em sessão (localStorage)
- Todos os números do dashboard se reajustam ao filtro:
  - Cobertura de IA / Material / 100% Prontos
  - Tabela de matérias por urgência
  - Cards de tempo total e tópicos iniciados

**Importância arquitetural:**
Esta não é uma feature "nice to have" — é **pré-requisito do uso multi-edital
real**. Sem ela, o usuário com 2+ concursos não tem leitura clara do progresso
de cada um. Deve ser implementada **junto com (ou antes de)** o uso efetivo do
CEF como segundo concurso.

**O que já está pronto:**
- `TblEditalLink` já liga concurso ↔ tópico
- Cobertura por matéria já é calculada de forma agregada
- Falta apenas filtrar pelo concurso selecionado

---

### Gráficos comparativos entre concursos
**Status:** ideia mapeada · **Prioridade:** média · **Gatilho:** após 30+ dias com 2+ concursos ativos

Quando houver dois ou mais concursos com cobertura significativa, gráficos
comparativos lado a lado ajudam a ver desbalanço de preparação:

**Visões propostas (a refinar):**
1. **Cobertura comparativa**: barras BB vs CEF (IA, Material, 100% Prontos)
2. **Horas de estudo por concurso**: rosca mostrando proporção
3. **Tópicos comuns x específicos**: onde está o esforço (compartilhado vs único)
4. **Projeção até a prova**: dois "termômetros" lado a lado mostrando
   ritmo necessário pra cada um

**Armadilha a evitar:**
Gráfico bonito que vira vaidade. Cada visão deve responder a uma pergunta
prática que o usuário **realmente faria**. Se a pergunta não existir, o
gráfico não serve. Antes de implementar, validar com 30+ dias de uso real
quais perguntas surgem na cabeça quando estuda pra dois concursos
simultaneamente.

---

### Diagnóstico de sobreposição entre concursos
**Status:** ideia mapeada · **Prioridade:** baixa · **Gatilho:** ao carregar concurso novo

Quando o usuário carrega um concurso novo, mostrar **uma vez** um diagnóstico:
- Quantos tópicos do novo concurso já existem (vindos de outros editais)
- Quais matérias têm 100% de sobreposição
- Quais são exclusivas do novo concurso

**Por que prioridade baixa:**
Pode parecer útil ter uma tela permanente de "matérias comuns", mas na
prática é informação consultada **uma vez** — quando o usuário carrega o
concurso e quer entender o esforço extra. Depois disso, ele não volta
mais nessa tela. Por isso, melhor implementar como **mensagem one-time**
após rodar `populate_*.py`, ou como tela acessível apenas via menu
secundário, do que como elemento de destaque no dashboard.

**Alternativa mais leve:**
Já no `populate_cef_tbn.py` atual, o output do terminal mostra:
"X tópicos criados, Y reutilizados". Esse log já entrega 80% da
informação útil sem precisar de tela.

---

### Priorização por peso da disciplina no edital
**Status:** ideia mapeada · **Prioridade:** alta

Hoje o Dashboard de Cobertura ordena as matérias apenas por nível de
"urgência" (quanto menos conteúdo gerado, mais urgente). Mas matérias
de peso alto no edital (ex: Conhecimentos Bancários, Informática, Vendas
e Negociação no BB) deveriam ter precedência sobre matérias de peso
baixo (ex: Língua Inglesa) mesmo quando ambas estão pouco cobertas.

**O que já está pronto pra isso:**
- O campo `prioridade_no_edital` existe em `TblEditalLink` (ALTA / MEDIA / BAIXA)
- O `populate_bb.py` e `populate_cef_tbn.py` já populam essas prioridades

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

**Sinergia com filtro de concurso:**
Faz mais sentido aplicar a priorização **dentro de um concurso específico**
do que num agregado de todos. Por isso, idealmente é implementada DEPOIS
do dropdown de concurso.

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

Hoje novos editais são carregados via script Python (`populate_*.py`).
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

### Migração de stack para alinhar com ElevaMind (Cloudflare + Supabase)
**Status:** em radar · **Prioridade:** revisitar em 3-6 meses

**Motivações que justificam a ideia:**
- Eliminar limite de memória do Render Free (geração IA pelo tablet
  sem precisar gastar com assinatura paga)
- Concentrar infraestrutura em um único provedor (Cloudflare), reduzindo
  carga cognitiva de manutenção
- Alinhar SGA com a stack já dominada na ElevaMind

**Restrições técnicas a considerar:**

1. **Cloudflare Pages é hospedagem estática.** Não roda Django. Pra
   adotar essa stack, são necessárias mudanças arquiteturais profundas.

2. **Cloudflare Workers tem suporte a Python apenas em beta** (em abril/2026)
   e não suporta Django nativamente — é outra filosofia de execução
   (serverless stateless, limites de tempo curtos por requisição).

3. **Caminhos possíveis:**
   - **a) Reescrita full** do backend em JavaScript/TypeScript
     (Cloudflare Workers + D1 ou Workers + Supabase) — esforço grande,
     2-6 semanas dependendo do escopo
   - **b) Frontend-only no Cloudflare** + backend Django mantido em
     outro lugar (Render, Fly.io, Railway). Não simplifica de fato,
     porque continuamos com 2 provedores
   - **c) Aguardar maturação** do Python Workers — pode evoluir o
     suficiente nos próximos 6-12 meses pra rodar uma API leve

4. **Sobre a memória da IA:** ainda que reescrita, o pico de memória
   ao receber e parsear a resposta JSON do Claude continua existindo.
   Workers tem limite de memória por requisição (128MB no plano gratuito,
   no plano pago tem mais), então pode resolver, mas precisa ser
   verificado caso a caso.

**Decisão atual: NÃO migrar agora.**

Motivos:
- O foco do momento é estudar pro BB, não reescrever sistema
- Workaround atual (gerar IA local, consumir pelo tablet) é viável
- Custo de oportunidade alto: 2-6 semanas que poderiam ser horas de
  estudo
- Risco de quebrar funcionalidades que já funcionam bem

**Quando revisitar:**
- Após o BB (mai/jun 2026) — passada a urgência da prova
- Se SGA virar produto e a infra atual ficar limitante
- Se o Python Workers do Cloudflare amadurecer e suportar Django/FastAPI
- Se o custo do plano pago do Render se tornar incômodo recorrente

**Alternativas mais leves a considerar antes da migração full:**
- Plano Padrão do Render (US$25/mês) elimina memória sem reescrever
- Fly.io ou Railway (similares ao Render, com tiers gratuitos
  potencialmente mais generosos)
- Manter Render + adicionar Cloudflare DNS/CDN na frente (parcial,
  mas começa a integrar com ecossistema sem reescrita)

---

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

## 🧭 Plano de Carreira e Estratégia de Estudo

### Plano de fases (BB → TRT)
**Status:** em execução · **Atualizado em:** abril/2026

**Contexto pessoal relevante:**
- 55 anos, aposentado pelo INSS (RGPS)
- Base jurídica: Direito cursado até o 10º período, faltam 6 disciplinas
  (estimadas em 12 meses pra concluir)
- Objetivo principal: **construir segunda aposentadoria pública (RPPS)**
  via concurso estatutário, somando ao benefício atual do INSS
- Objetivo secundário: fluxo de caixa imediato via concurso de curto prazo

**Plano de fases acordado:**

**Fase 1 — Foco BB (agora até prova ~mai/jun 2026)**
- 90% do tempo: matérias do BB Escriturário Agente Comercial
- 10%: revisão passiva da Constituição Federal (15-20 min/dia em momentos
  "mortos") — mantém base jurídica acordada sem competir com BB
- CEF TBN carregado no SGA como benefício colateral (sobreposição alta com BB,
  custo marginal zero)
- TRT MG **não** carregado ainda — evitar dispersão visual no dashboard

**Fase 2 — Pós-prova BB (jun-set 2026)**
- Inversão: TRT vira foco principal
- Carregar TRT MG no SGA
- Iniciar revisão dirigida das matérias jurídicas (Constitucional,
  Administrativo, Civil, Processual Civil, Penal, Processual Penal)
- Decidir nesse momento sobre conclusão das 6 disciplinas pendentes
  do curso de Direito (12 meses estimados)

**Fase 3 — Pré-edital TRT (quando edital sair: 2º sem 2026 ou 1º sem 2027)**
- Foco total TRT por 4-6 meses
- Eventual conclusão da graduação em paralelo (se for prático)

**Por que esse plano e não outro:**
- A base jurídica existente (10 períodos) reduz drasticamente o tempo de
  preparação pro TRT — não é "começar do zero", é "atualizar e revisar"
- BB tem janela próxima e resolve fluxo de caixa intermediário
- Conclusão do curso pode ser feita em paralelo com vida ativa
- Misturar estudo bancário e jurídico em paralelo seria sobrecarga
  cognitiva real, mesmo com base prévia

---

### Validação previdenciária com profissional especializado
**Status:** AÇÃO PENDENTE · **Prioridade:** crítica · **Prazo:** antes da posse num eventual concurso público

**Motivação:**
A estratégia de carreira está toda construída em torno da hipótese de
**acumulação de aposentadoria do RGPS (já recebida) com aposentadoria
do RPPS (a construir via concurso estatutário)**. Antes de qualquer
decisão definitiva, é essencial validar com advogado previdenciário:

**Pontos a esclarecer com profissional:**

1. **Viabilidade da acumulação no caso pessoal:**
   - Quantos anos de INSS já contribuídos (pré e pós-aposentadoria)
   - Como a aposentadoria atual do INSS foi concedida (regra de cálculo)
   - Se há tempo "excedente" que pode ser averbado pro RPPS sem perder o RGPS

2. **Cálculo do tempo necessário no RPPS:**
   - Regra geral é 25 anos contribuição total + 10 como servidor + 5 no cargo
   - Se a contagem recíproca do INSS é aceita pra cumprir os 25 anos
   - Estimativa concreta de quantos anos de serviço público são necessários

3. **Quantificação do redutor (sistema de faixas — art. 24 EC 103/2019):**
   - Estimar o valor real que será recebido na cumulação
   - Comparar cenários: cumulação reduzida vs aposentadoria única ampliada

4. **Decisão estratégica final:**
   - Se a acumulação se mostra inviável ou pouco vantajosa, pode-se
     reposicionar o objetivo (ex: focar em uma única aposentadoria
     pública robusta, sem se importar com o RGPS atual)
   - Se for viável, definir tempo necessário e cargo-alvo ideal

**Premissa pessoal validada (sentimento, não estudo):**
*"Mesmo que a primeira aposentadoria seja zerada pelo redutor, se a
segunda for de R$8k+ vitalícios, vale a pena: estarei dobrando a renda
vitalícia comparada ao baseline atual."*

Esse raciocínio é financeiramente sólido, mas precisa de números reais
do previdenciarista pra confirmar.

**Custo estimado da consulta:** R$300-500
**Quando agendar:** após estabilização do plano de estudo (60-90 dias após
início do foco no BB), ou em qualquer momento que surgir oportunidade
concreta de aprovação.

---

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
