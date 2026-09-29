# AGENTS.md

Repositorio personal de CV/portfolio (David Moreno Bolívar). No es un proyecto de software: no hay build, tests, lint ni CI. No inventes comandos ni flujos de trabajo.

## Convenciones
- Contenido (CV, specs, commits): **castellano**. 

## Estructura
- `sources/curriculum-github.md` — fuente de verdad del CV en formato GitHub (con badges del repo `elarreglador/rotulos`).
- `sources/curriculum-base.md` — CV 1 página base en Markdown (fuente para generar ODTs).
- `templates/curriculum-odt.odt` — plantilla de referencia del último ODT generado.
- `output/YYYYMMDD-nombreempresa/` — candidaturas generadas (`info.md` + CV y carta en `.md`, `.odt` y `.pdf`). **Versionado en git**: cada candidatura queda en su propio directorio con la fecha de generación, de modo que se conserva el historial de lo enviado a cada empresa.
- `assets/foto.jpg`, `assets/foto2.jpeg` — fotografías para el CV.
- `specs/NN-slug.md` — especificaciones con metadatos (Estado, Depende de, Fecha, Objetivo). Flujo: `spec` → `spec-impl`.

## Generación ODT por empresa
- **Estándar:** por cada empresa, un directorio `output/YYYYMMDD-nombreempresa/` con `info.md` + `curriculum-NOMBREEMPRESA.md` + `.odt` + `.pdf` y `carta-NOMBREEMPRESA.md` + `.odt` + `.pdf`. El directorio va en minúsculas y sin acentos; los ficheros en mayúsculas.
- `info.md` — datos de la empresa y de la oferta, con sus fuentes. **Uso interno, no se envía a la empresa**: es el soporte de las cifras citadas en el CV y en la carta. Lo redacta el agente (Paso 5 de la skill); un dato sin verificar se escribe como `No consta`, nunca estimado.
- Flujo: copiar `sources/curriculum-base.md` → editar → convertir.
- Comandos: `nueva_candidatura.py "Empresa"` crea el directorio; `md2odt.py <fichero.md>` genera `.odt` y `.pdf` y falla con código 2 si no cabe en una página.
- **No usar** `libreoffice --headless --convert-to odt *.md`: el filtro Markdown de LibreOffice no está disponible en esta máquina y deja los `#` y `**` literales en el ODT.
- Skill automatizada: `.opencode/skills/cv-generator/` (ver spec 02)

## Git
- Repositorio git inicializado. Remote: `https://github.com/elarreglador/Curriculum`.
