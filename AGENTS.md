# AGENTS.md

Repositorio personal de CV/portfolio (David Moreno Bolívar). No es un proyecto de software: no hay build, tests, lint ni CI. No inventes comandos ni flujos de trabajo.

## Convenciones
- Contenido (CV, specs, commits): **castellano**. 

## Estructura
- `sources/curriculum-github.md` — fuente de verdad del CV en formato GitHub (con badges del repo `elarreglador/rotulos`).
- `sources/curriculum-base.md` — CV 1 página base en Markdown (fuente para generar ODTs).
- `templates/curriculum-odt.odt` — plantilla de referencia del último ODT generado.
- `output/` — CVs generados por empresa (ignorado por git).
- `assets/foto.jpg`, `assets/foto2.jpeg` — fotografías para el CV.
- `specs/NN-slug.md` — especificaciones con metadatos (Estado, Depende de, Fecha, Objetivo). Flujo: `spec` → `spec-impl`.

## Generación ODT por empresa
- **Estándar:** por cada empresa, generar `output/curriculum-NOMBREEMPRESA.md` + `output/curriculum-NOMBREEMPRESA.odt` + `output/carta-NOMBREEMPRESA.md` + `output/carta-NOMBREEMPRESA.odt`.
- Flujo: copiar `sources/curriculum-base.md` → editar → convertir con LibreOffice.
- Fallback sin pandoc: `libreoffice --headless --convert-to odt output/curriculum-NOMBREEMPRESA.md --outdir output/`
- Skill automatizada: `.opencode/skills/cv-generator/` (ver spec 02)

## Git
- Repositorio git inicializado. Remote: `https://github.com/elarreglador/Curriculum`.
