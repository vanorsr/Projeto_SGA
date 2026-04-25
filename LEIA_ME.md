# SGA — Guia de Uso Rápido

Documento curto pra lembrar como operar o projeto no dia a dia.
Leia em 2 minutos antes de mexer no código depois de muito tempo.

---

## 🔌 Como rodar o servidor

### Caso 1 — Estudar / gerar conteúdo "pra valer"
**Use sempre que quiser que o conteúdo gerado apareça no tablet/celular.**

```powershell
$env:DATABASE_URL="postgresql://postgres.dvgtkpqhbnfyqmypsodo:VVdh20170621%40%23@aws-1-sa-east-1.pooler.supabase.com:5432/postgres"
python manage.py runserver
# Acesse: http://127.0.0.1:8000
# Gere conteúdo, adicione materiais, etc.
# Tudo é gravado no Supabase (banco da produção)
# Ao terminar:
Remove-Item Env:DATABASE_URL
```

**Atalho:** rode `.\iniciar.ps1` que faz isso pra você.

### Caso 2 — Testar feature nova ou alteração arriscada
**Use quando quer mexer no banco sem risco de quebrar produção.**

```powershell
python manage.py runserver
# Acesse: http://127.0.0.1:8000
# Tudo é gravado no SQLite local (db.sqlite3)
# Produção fica intocada
```

---

## 🧠 Por que essa separação?

O Render Free (onde a aplicação roda em produção) tem 512 MB de RAM —
**não dá conta da geração de conteúdo IA**. Por isso, geramos a IA
**no notebook local**, mas conectados ao **banco de produção (Supabase)**.

- Computador local processa a IA (tem RAM sobrando)
- Supabase armazena o resultado
- Tablet lê do Supabase via Render

**Sem duplicação. Sem perda. Mesmo banco.**

---

## 🚫 Erros clássicos a evitar

### "Gerei IA mas não aparece no tablet"
**Causa:** rodou `runserver` sem `DATABASE_URL`. Gerou no SQLite local.
**Solução:** sempre defina a env var antes de gerar.

### "Quero testar uma feature, mas tenho medo de quebrar"
**Causa:** medo legítimo. Não rode com `DATABASE_URL` definida.
**Solução:** rode `runserver` puro. SQLite local é descartável.

### "O dashboard mostra números diferentes em casa e no tablet"
**Causa:** está acessando `127.0.0.1:8000` sem `DATABASE_URL`. Está vendo
o SQLite local, não o Supabase.
**Solução:** ou define a env var, ou abre direto `projeto-sga.onrender.com`.

---

## 📦 Comandos úteis

### Aplicar migrations no banco de produção
```powershell
$env:DATABASE_URL="postgresql://..."
python manage.py migrate
Remove-Item Env:DATABASE_URL
```

### Resetar senha de usuário (local)
```powershell
python manage.py changepassword vanor
```

### Resetar senha de usuário (produção)
```powershell
$env:DATABASE_URL="postgresql://..."
python manage.py changepassword vanor
Remove-Item Env:DATABASE_URL
```

### Listar migrations pendentes
```powershell
python manage.py showmigrations core
```

### Carregar novo edital
```powershell
# Local primeiro pra testar
python populate_<concurso>.py

# Depois em produção
$env:DATABASE_URL="postgresql://..."
python populate_<concurso>.py
Remove-Item Env:DATABASE_URL
```

### Deduplicar tópicos
```powershell
python deduplicar_topicos.py
# Mesmo padrão pra produção
```

---

## 🌐 URLs importantes

- **Produção (tablet/celular/qualquer dispositivo):** https://projeto-sga.onrender.com
- **Local (notebook):** http://127.0.0.1:8000
- **GitHub:** https://github.com/vanorsr/Projeto_SGA
- **Admin Supabase:** https://supabase.com (login com a conta cadastrada)
- **Admin Render:** https://render.com (login com a conta cadastrada)

---

## 🛠️ Stack atual

- **Backend:** Django 5.2.9 (Python)
- **Banco produção:** PostgreSQL (Supabase, São Paulo)
- **Banco local:** SQLite (descartável, só pra testes)
- **Hospedagem:** Render Free 512 MB
- **IA:** Claude Haiku 4.5 (`claude-haiku-4-5-20251001`)
- **Frontend:** Bootstrap 5 + Poppins + tema ElevaMind

Ver `ROADMAP.md` pra evoluções planejadas.

---

*Última atualização: abril/2026*
