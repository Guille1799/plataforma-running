# 📄 GUÍA: CONVERTIR DOCUMENTACIÓN A WORD

**Fecha:** 17 de Noviembre, 2025  
**Objetivo:** Crear documento Word de 100+ páginas con toda la documentación

---

## 📋 MÉTODO 1: Manual en Word (Recomendado)

### Paso 1: Preparar los archivos
```
1. Abre tu explorador de archivos
2. Ve a: c:\Users\guill\Desktop\plataforma-running\
3. Selecciona estos archivos:
   - 00_CONFIRMACION_DOCUMENTACION_GENERADA.md
   - DOCUMENTACION_TECNICA_INDICE_MAESTRO.md
   - DOCUMENTACION_TECNICA_COMPLETA_PARTE1.md
   - DOCUMENTACION_TECNICA_COMPLETA_PARTE2.md
   - DOCUMENTACION_TECNICA_COMPLETA_PARTE3.md
   - DOCUMENTACION_TECNICA_COMPLETA_PARTE4.md
   - DOCUMENTACION_TECNICA_COMPLETA_PARTE5.md
```

### Paso 2: Crear documento en Word
```
1. Abre Microsoft Word
2. Crea nuevo documento en blanco
3. Guarda como: "Plataforma_Running_TIER2_Documentacion.docx"
```

### Paso 3: Insertar contenido
```
MÉTODO A: Copiar/Pegar Directo

1. Abre archivo MD #1 en tu editor (VS Code, Notepad++, etc.)
2. Selecciona TODO (Ctrl+A)
3. Copia (Ctrl+C)
4. En Word, pega (Ctrl+V)
5. Repite para cada archivo en orden

MÉTODO B: Insertar como Texto (Mejor Formato)

1. En Word: Insert → Text → Text from File
2. Selecciona el primer archivo .md
3. Repite para cada archivo
4. Word automáticamente mantiene formato
```

### Paso 4: Aplicar formato
```
1. Selecciona todos los títulos "# Algo"
   - Format as: Heading 1
   
2. Selecciona todos los subtítulos "## Algo"
   - Format as: Heading 2
   
3. Selecciona todos los sub-subtítulos "### Algo"
   - Format as: Heading 3

4. Bloques de código (entre ```):
   - Format as: Code Block (Styles)
   
5. Listas (líneas con ├─, ✅, etc):
   - Bullet Points o Numbering
```

### Paso 5: Tabla de Contenido Automática
```
1. Position cursor al inicio (después de portada)
2. References → Table of Contents
3. Selecciona un estilo (Automatic)
4. Word genera TOC automáticamente
```

### Paso 6: Numeración y estilos
```
1. Selecciona todos los "Heading 1"
   - Format → Bullets and Numbering
   - Aplica numeración 1, 2, 3, etc.

2. Selecciona todos los "Heading 2"
   - Format → Bullets and Numbering
   - Aplica numeración 1.1, 1.2, etc.

3. References → Update Table → Update entire table
```

### Paso 7: Exportar a PDF (Opcional)
```
1. File → Export As → PDF
2. Guarda como: "Plataforma_Running_TIER2_Documentacion.pdf"
3. Sube a Google Drive, Sharepoint, etc.
```

---

## 🔧 MÉTODO 2: Pandoc (Automatizado)

### Instalación
```powershell
# En PowerShell como Admin
choco install pandoc

# O si usas scoop
scoop install pandoc
```

### Convertir archivos individuales
```powershell
cd c:\Users\guill\Desktop\plataforma-running\

# Convertir un archivo MD a DOCX
pandoc DOCUMENTACION_TECNICA_INDICE_MAESTRO.md -o temp_indice.docx

# Con opciones más avanzadas
pandoc DOCUMENTACION_TECNICA_INDICE_MAESTRO.md `
  --from markdown `
  --to docx `
  --standalone `
  --output temp_indice.docx `
  --table-of-contents `
  --toc-depth=2 `
  --number-sections
```

### Fusionar múltiples archivos en uno
```powershell
# Crear documento maestro con todas las partes

$files = @(
  "DOCUMENTACION_EXHAUSTIVA_RESUMEN.md",
  "DOCUMENTACION_TECNICA_INDICE_MAESTRO.md",
  "DOCUMENTACION_TECNICA_COMPLETA_PARTE1.md",
  "DOCUMENTACION_TECNICA_COMPLETA_PARTE2.md",
  "DOCUMENTACION_TECNICA_COMPLETA_PARTE3.md",
  "DOCUMENTACION_TECNICA_COMPLETA_PARTE4.md",
  "DOCUMENTACION_TECNICA_COMPLETA_PARTE5.md"
)

# Concatenar todos los archivos
$combined = ""
foreach ($file in $files) {
  $combined += (Get-Content $file -Raw)
  $combined += "`n`n---`n`n"  # Page break entre archivos
}

# Guardar como archivo temporal
$combined | Out-File -Encoding utf8 "documentacion_completa_temp.md"

# Convertir a DOCX
pandoc documentacion_completa_temp.md `
  --from markdown `
  --to docx `
  --standalone `
  --output "Plataforma_Running_TIER2_Documentacion_Completa.docx" `
  --table-of-contents `
  --toc-depth=3 `
  --number-sections

# Limpiar archivo temporal
Remove-Item "documentacion_completa_temp.md"

Write-Host "✅ Documento creado: Plataforma_Running_TIER2_Documentacion_Completa.docx"
```

---

## 📱 MÉTODO 3: Google Docs (Si no tienes Word)

### Pasos
```
1. Accede a Google Docs (docs.google.com)
2. Create new → Document
3. Nombra: "Plataforma Running TIER 2 Documentation"
4. Para cada archivo:
   - Abre el MD en VS Code
   - Ctrl+A para seleccionar todo
   - Ctrl+C para copiar
   - En Google Docs, Ctrl+V para pegar
5. Format → Styles → Aplica estilos a títulos
6. Insert → Table of contents → automática
7. File → Download → Microsoft Word (.docx)
```

---

## 🎨 FORMATTING TIPS

### Headings
```markdown
# Heading 1  →  Format as "Heading 1"
## Heading 2  →  Format as "Heading 2"
### Heading 3  →  Format as "Heading 3"
```

### Code Blocks
```markdown
```python
def code_example():
    pass
```
→ Selecciona y aplica "Code" o monospace font
```

### Listas
```markdown
- Item 1     →  Bullet Point
- Item 2
- Item 3

1. Item 1    →  Numbered List
2. Item 2
3. Item 3
```

### Tablas
```markdown
| Header 1 | Header 2 |
|----------|----------|
| Cell 1   | Cell 2   |
```
→ Word automáticamente reconoce y formatea

### Emphasis
```markdown
**bold**      → Ctrl+B
*italic*      → Ctrl+I
`code`        → Monospace
```

---

## 📊 RESULTADO ESPERADO

Después de la conversión, tendrás:

### Documento Word (.docx)
```
Tamaño:                    ~80-100 MB
Páginas:                   100-150
Estilo:                    Professional
Tabla de Contenido:        Automática
Índice:                    Completo
Searchable:                Sí
Editable:                  Sí
Shareable:                 Sí (Google Drive, Email, etc)
```

### PDF Exportado
```
Tamaño:                    ~30-40 MB
Páginas:                   100-150
Estilo:                    Professional
Print-friendly:            Sí
Searchable:                Sí
Editable:                  No (para seguridad)
Archivable:                Sí
```

---

## ⚡ SCRIPT RÁPIDO (PowerShell)

Si tienes Pandoc instalado, simplemente copia/pega esto:

```powershell
# Script para convertir documentación a Word

Write-Host "Iniciando conversión de documentación..." -ForegroundColor Green

$path = "c:\Users\guill\Desktop\plataforma-running"
cd $path

# Listar archivos
Write-Host "`nArchivos a fusionar:" -ForegroundColor Cyan
$files = @(
  "DOCUMENTACION_EXHAUSTIVA_RESUMEN.md",
  "DOCUMENTACION_TECNICA_INDICE_MAESTRO.md",
  "DOCUMENTACION_TECNICA_COMPLETA_PARTE1.md",
  "DOCUMENTACION_TECNICA_COMPLETA_PARTE2.md",
  "DOCUMENTACION_TECNICA_COMPLETA_PARTE3.md",
  "DOCUMENTACION_TECNICA_COMPLETA_PARTE4.md",
  "DOCUMENTACION_TECNICA_COMPLETA_PARTE5.md"
)

foreach ($f in $files) { Write-Host "  ✓ $f" -ForegroundColor Green }

# Concatenar
Write-Host "`nFusionando archivos..." -ForegroundColor Cyan
$combined = ""
foreach ($file in $files) {
  $combined += (Get-Content $file -Raw)
  $combined += "`n`n"
}
$combined | Out-File -Encoding utf8 "temp_full.md"

# Convertir
Write-Host "Convirtiendo a Word..." -ForegroundColor Cyan
pandoc temp_full.md `
  --from markdown `
  --to docx `
  --standalone `
  --output "PLATAFORMA_RUNNING_TIER2_DOCUMENTACION_COMPLETA.docx" `
  --table-of-contents `
  --toc-depth=3 `
  --number-sections

# Limpiar
Remove-Item "temp_full.md"

Write-Host "`n✅ ¡Conversión completada!" -ForegroundColor Green
Write-Host "Archivo creado: PLATAFORMA_RUNNING_TIER2_DOCUMENTACION_COMPLETA.docx" -ForegroundColor Yellow
```

---

## 🔗 ENLACES ÚTILES

- **Pandoc Documentation**: https://pandoc.org/
- **Microsoft Word**: https://www.microsoft.com/office
- **Google Docs**: https://docs.google.com
- **Online MD to DOCX Converter**: https://cloudconvert.com/ (si no quieres instalar Pandoc)

---

## ❓ TROUBLESHOOTING

### "Pandoc no reconocido"
```powershell
# Verificar instalación
pandoc --version

# Si no funciona, reinstalar
choco uninstall pandoc
choco install pandoc

# Reiniciar PowerShell
```

### "Encoding issues"
```powershell
# Asegúrate de usar UTF-8
pandoc ... -f markdown+utf8 ...

# O especificar explícitamente
--variable encoding=utf-8
```

### "Formato de tabla incorrecto"
```
En Word:
1. Selecciona la tabla
2. Table Design → Aplica un estilo
3. Properties → Adjust borders
```

### "Tabla de contenido no se actualiza"
```
En Word:
1. Right-click en la TOC
2. Update Field
3. Select "Update entire table"
```

---

## ✅ CHECKLIST DE CONVERSIÓN

- [ ] Archivos MD preparados
- [ ] Word/Google Docs abierto
- [ ] Contenido copiado/pegado en orden
- [ ] Headings formateados correctamente
- [ ] Código con monospace font
- [ ] Listas con bullets/numbers
- [ ] Tabla de Contenido generada
- [ ] Numeración de secciones aplicada
- [ ] Revisión de formato general
- [ ] Exportado a PDF (opcional)
- [ ] Guardado en Google Drive (opcional)
- [ ] Compartido con el team (opcional)

---

**¡Listo! Tienes 3 métodos para convertir.** 🚀

*Recomendación: Método 1 (Manual) si necesitas control total, Método 2 (Pandoc) si quieres automatizar.*
