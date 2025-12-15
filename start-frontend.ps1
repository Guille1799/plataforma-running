# Start Frontend Server
Write-Host "`n" -ForegroundColor Green
Write-Host "╔═══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║        🚀 RunCoach AI - Frontend Server (Next.js)        ║" -ForegroundColor Cyan
Write-Host "║                   Port: 3000                             ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

$app_path = "c:\Users\Guille\proyectos\plataforma-running"

Write-Host "📂 Location: $app_path" -ForegroundColor Yellow
Write-Host "⚙️  Using: npm run dev" -ForegroundColor Yellow
Write-Host ""

Set-Location $app_path

Write-Host "⏳ Starting Next.js development server..." -ForegroundColor Cyan
npm run dev

Write-Host "`n✋ Server stopped" -ForegroundColor Yellow
