# iniciar.ps1
# ============
# Inicia o servidor Django local apontando para o banco de produção (Supabase).
# Use este script sempre que for gerar conteúdo IA ou trabalhar com dados reais.
#
# Uso:
#   .\iniciar.ps1
#
# Se quiser usar o banco LOCAL (SQLite) em vez do Supabase, NÃO use este script.
# Rode direto: python manage.py runserver

Write-Host ""
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "  SGA - Iniciando servidor conectado ao Supabase" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

# Define a variável de ambiente apontando pro Supabase
$env:DATABASE_URL="postgresql://postgres.dvgtkpqhbnfyqmypsodo:VVdh20170621%40%23@aws-1-sa-east-1.pooler.supabase.com:5432/postgres"

Write-Host "✅ DATABASE_URL configurada (Supabase produção)" -ForegroundColor Green
Write-Host "📍 Servidor vai abrir em: http://127.0.0.1:8000" -ForegroundColor Yellow
Write-Host "💡 Tudo que você gravar aqui vai pro banco da produção" -ForegroundColor Yellow
Write-Host ""
Write-Host "Pressione Ctrl+C para parar o servidor quando terminar." -ForegroundColor Gray
Write-Host ""

# Inicia o servidor
python manage.py runserver

# Quando o servidor for parado (Ctrl+C), limpa a variável
Remove-Item Env:DATABASE_URL -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "🛑 Servidor parado. DATABASE_URL removida do ambiente." -ForegroundColor Cyan
Write-Host ""
