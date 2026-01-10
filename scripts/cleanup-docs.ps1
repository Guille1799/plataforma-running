# Limpiar documentación obsoleta
# Mantener solo: PRODUCTION_STATUS.md, MONITORING_GUIDE.md, AI_MONITORING_SYSTEM.md, RENDER_VERCEL_ENV_VARS.md, SUPABASE_CIRCUIT_BREAKER_FIX.md

$keep = @(
    "PRODUCTION_STATUS.md",
    "MONITORING_GUIDE.md", 
    "AI_MONITORING_SYSTEM.md",
    "RENDER_VERCEL_ENV_VARS.md",
    "SUPABASE_CIRCUIT_BREAKER_FIX.md"
)

$docsPath = "docs"
$allDocs = Get-ChildItem -Path $docsPath -Filter "*.md" -File

$removed = 0
foreach ($doc in $allDocs) {
    if ($doc.Name -notin $keep) {
        Write-Host "Eliminando: $($doc.Name)" -ForegroundColor Yellow
        Remove-Item $doc.FullName -Force
        $removed++
    }
}

Write-Host "`n✅ Documentación limpiada. Eliminados: $removed archivos. Mantenidos: $($keep.Count) archivos." -ForegroundColor Green
