# Monitoring Script - Quick Reference

## Basic usage

```powershell
.\scripts\production-monitor.ps1
```

Continuous mode:

```powershell
.\scripts\production-monitor.ps1 -Continuous
```

Custom interval:

```powershell
.\scripts\production-monitor.ps1 -Continuous -IntervalSeconds 30
```

## What it does

1. Checks Frontend (Vercel)
2. Checks Backend (Render `/health`)
3. Measures response times
4. Reports failures and warnings
5. Generates text reports (`monitoring-report-*.txt`)

Full documentation: [`../docs/MONITORING_GUIDE.md`](../docs/MONITORING_GUIDE.md)
