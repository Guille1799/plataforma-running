# Script para fusionar toda la documentación y convertir a Word

cd "c:\Users\guill\Desktop\plataforma-running"

Write-Host "=================================================================================" -ForegroundColor Cyan
Write-Host " INICIANDO CONVERSIÓN DE DOCUMENTACIÓN A WORD" -ForegroundColor Cyan
Write-Host "=================================================================================" -ForegroundColor Cyan

$files = @(
  "00_CONFIRMACION_DOCUMENTACION_GENERADA.md",
  "DOCUMENTACION_EXHAUSTIVA_RESUMEN.md",
  "DOCUMENTACION_TECNICA_INDICE_MAESTRO.md",
  "DOCUMENTACION_TECNICA_COMPLETA_PARTE1.md",
  "DOCUMENTACION_TECNICA_COMPLETA_PARTE2.md",
  "DOCUMENTACION_TECNICA_COMPLETA_PARTE3.md",
  "DOCUMENTACION_TECNICA_COMPLETA_PARTE4.md",
  "DOCUMENTACION_TECNICA_COMPLETA_PARTE5.md"
)

Write-Host "
Archivos a fusionar:" -ForegroundColor Green
$count = 1
foreach ($f in $files) { 
  Write-Host "  $count. $f" -ForegroundColor White
  $count++
}

Write-Host "
Fusionando archivos..." -ForegroundColor Cyan
$combined = ""
foreach ($file in $files) {
  if (Test-Path $file) {
    $combined += (Get-Content $file -Raw -Encoding UTF8)
    $combined += "

---

"
    Write-Host "   Agregado: $file" -ForegroundColor Green
  } else {
    Write-Host "   No encontrado: $file" -ForegroundColor Red
  }
}

$combined | Out-File -Encoding utf8 "temp_documentacion_completa.md"
Write-Host "
 Archivo temporal creado: temp_documentacion_completa.md" -ForegroundColor Green

Write-Host "
Convirtiendo a Word (DOCX)..." -ForegroundColor Cyan
pandoc temp_documentacion_completa.md 
  --from markdown 
  --to docx 
  --standalone 
  --output "PLATAFORMA_RUNNING_TIER2_DOCUMENTACION_COMPLETA.docx" 
  --table-of-contents 
  --toc-depth=3 
  --number-sections 
  --reference-doc=NULL

if (Test-Path "PLATAFORMA_RUNNING_TIER2_DOCUMENTACION_COMPLETA.docx") {
  $size = (Get-Item "PLATAFORMA_RUNNING_TIER2_DOCUMENTACION_COMPLETA.docx").Length / 1MB
  Write-Host " Documento Word creado exitosamente!" -ForegroundColor Green
  Write-Host "  Archivo: PLATAFORMA_RUNNING_TIER2_DOCUMENTACION_COMPLETA.docx" -ForegroundColor Green
  Write-Host "  Tamaño: $([math]::Round($size, 2)) MB" -ForegroundColor Green
} else {
  Write-Host " Error al crear documento Word" -ForegroundColor Red
}

Write-Host "
Convirtiendo a PDF..." -ForegroundColor Cyan
pandoc temp_documentacion_completa.md 
  --from markdown 
  --to pdf 
  --standalone 
  --output "PLATAFORMA_RUNNING_TIER2_DOCUMENTACION_COMPLETA.pdf" 
  --table-of-contents 
  --toc-depth=3 
  --number-sections

if (Test-Path "PLATAFORMA_RUNNING_TIER2_DOCUMENTACION_COMPLETA.pdf") {
  $size = (Get-Item "PLATAFORMA_RUNNING_TIER2_DOCUMENTACION_COMPLETA.pdf").Length / 1MB
  Write-Host " Documento PDF creado exitosamente!" -ForegroundColor Green
  Write-Host "  Archivo: PLATAFORMA_RUNNING_TIER2_DOCUMENTACION_COMPLETA.pdf" -ForegroundColor Green
  Write-Host "  Tamaño: $([math]::Round($size, 2)) MB" -ForegroundColor Green
} else {
  Write-Host " Error al crear documento PDF" -ForegroundColor Red
}

Write-Host "
Limpiando archivos temporales..." -ForegroundColor Cyan
Remove-Item "temp_documentacion_completa.md" -ErrorAction SilentlyContinue
Write-Host " Limpeza completada" -ForegroundColor Green

Write-Host "
=================================================================================" -ForegroundColor Cyan
Write-Host " CONVERSIÓN COMPLETADA" -ForegroundColor Cyan
Write-Host "=================================================================================" -ForegroundColor Cyan

Write-Host "
Archivos generados:" -ForegroundColor Yellow
Write-Host "   PLATAFORMA_RUNNING_TIER2_DOCUMENTACION_COMPLETA.docx" -ForegroundColor Green
Write-Host "   PLATAFORMA_RUNNING_TIER2_DOCUMENTACION_COMPLETA.pdf" -ForegroundColor Green

Write-Host "
Ubicación: c:\Users\guill\Desktop\plataforma-running\" -ForegroundColor Cyan
Write-Host "
¡Ahora puedes leer la documentación cómodamente en Word o PDF!" -ForegroundColor Green
