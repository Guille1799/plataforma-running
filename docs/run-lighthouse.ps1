#!/usr/bin/env powershell
<#
.SYNOPSIS
Lighthouse Performance Audit Runner
Audits the production build for performance, accessibility, and best practices
#>

param(
    [string]$Url = "http://localhost:3000",
    [string]$Output = "lighthouse-report"
)

Write-Host "🔍 Lighthouse Performance Audit" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green
Write-Host ""

# Check if lighthouse is installed
$lighthouse = npm list -g lighthouse 2>/dev/null | Select-String "lighthouse"
if (-not $lighthouse) {
    Write-Host "📦 Installing Lighthouse globally..." -ForegroundColor Yellow
    npm install -g lighthouse
}

Write-Host "🚀 Starting audit on $Url" -ForegroundColor Cyan
Write-Host ""

# Run Lighthouse with JSON output
$reportPath = "$Output.json"
Write-Host "📊 Generating report: $reportPath" -ForegroundColor Cyan

lighthouse $Url `
    --output json `
    --output-path "$reportPath" `
    --chrome-flags="--headless" `
    --view `
    2>&1

# Parse the JSON report
if (Test-Path $reportPath) {
    Write-Host ""
    Write-Host "✅ Report generated successfully" -ForegroundColor Green
    
    # Extract scores
    $json = Get-Content $reportPath | ConvertFrom-Json
    $scores = $json.categories
    
    Write-Host ""
    Write-Host "📈 Lighthouse Scores:" -ForegroundColor Green
    Write-Host "=====================" -ForegroundColor Green
    
    foreach ($category in $scores.PSObject.Properties) {
        $name = $category.Name
        $score = [math]::Round($category.Value.score * 100)
        $color = if ($score -ge 90) { "Green" } elseif ($score -ge 50) { "Yellow" } else { "Red" }
        Write-Host "$name : $score" -ForegroundColor $color
    }
    
    Write-Host ""
    Write-Host "📄 Full report:" -ForegroundColor Cyan
    Write-Host "$reportPath" -ForegroundColor Cyan
    
} else {
    Write-Host "❌ Failed to generate report" -ForegroundColor Red
}
