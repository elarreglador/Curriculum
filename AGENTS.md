# AGENTS.md

Repositorio personal de CV/portfolio (David Moreno Bolívar). No es un proyecto de software: no hay build, tests, lint ni CI. No inventes comandos ni flujos de trabajo.

## Convenciones
- Contenido (CV, specs, commits): **castellano**. 

## Estructura
- `sources/curriculum-github.md` — fuente de verdad del CV en formato GitHub (con badges del repo `elarreglador/rotulos`).
- `sources/curriculum-base.md` — **plantilla del CV**: contenido base y estructura de referencia (cabecera con foto, contacto al final). Es lo que copia y adapta `nueva_candidatura.py` en cada candidatura.
- `templates/curriculum-odt.odt` — plantilla de referencia del último ODT generado.
- `output/YYYYMMDD-nombreempresa/` — candidaturas generadas (`pin.png` + `info.md` + CV y carta en `.md`, `.odt` y `.pdf`). **Versionado en git**: cada candidatura queda en su propio directorio con la fecha de generación, de modo que se conserva el historial de lo enviado a cada empresa.
- `assets/pin.png` — foto de la cabecera del CV; `assets/foto.jpg`, `assets/foto2.jpeg` — alternativas.
- `specs/NN-slug.md` — especificaciones con metadatos (Estado, Depende de, Fecha, Objetivo). Flujo: `spec` → `spec-impl`.

## Generación ODT por empresa
- **Estándar:** por cada empresa, un directorio `output/YYYYMMDD-nombreempresa/` con `pin.png` + `info.md` + `curriculum-NOMBREEMPRESA.md` + `.odt` + `.pdf` y `carta-NOMBREEMPRESA.md` + `.odt` + `.pdf`. El directorio va en minúsculas y sin acentos; los ficheros en mayúsculas.
- `info.md` — datos de la empresa y de la oferta, con sus fuentes. **Uso interno, no se envía a la empresa**: es el soporte de las cifras citadas en el CV y en la carta. Lo redacta el agente (Paso 5 de la skill); un dato sin verificar se escribe como `No consta`, nunca estimado.
- Flujo: `nueva_candidatura.py` deja el directorio con la foto y una copia de `sources/curriculum-base.md` → el agente **adapta el texto** de esa copia (no la reescribe desde cero) → `md2odt.py` convierte.
- Comandos: `nueva_candidatura.py "Empresa"` prepara el andamiaje (`--foto` cambia la imagen, `--sin-foto` la omite); `md2odt.py <fichero.md>` genera `.odt` y `.pdf` y falla con código 2 si no cabe en una página.
- La cabecera del CV es una tabla HTML de dos columnas con la foto. Sus anchos van en **píxeles absolutos** (`700` = `90` + `610`) a propósito: el importador HTML de LibreOffice ignora los porcentajes y con `width="100%"` el nombre se parte en tres líneas.
- **No usar** `libreoffice --headless --convert-to odt *.md`: el filtro Markdown de LibreOffice no está disponible en esta máquina y deja los `#` y `**` literales en el ODT.
- Skill automatizada: `.opencode/skills/cv-generator/` (ver spec 02)

## Git
- Repositorio git inicializado. Remote: `https://github.com/elarreglador/Curriculum`.
