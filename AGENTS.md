# AGENTS.md

Repositorio personal de CV/portfolio (David Moreno Bolívar). No es un proyecto de software: no hay build, tests, lint ni CI. No inventes comandos ni flujos de trabajo.

## Convenciones
- Contenido (CV, specs, commits): **castellano**. 

## Estructura
- `sources/curriculum-github.md` — fuente de verdad del CV en formato GitHub (con badges del repo `elarreglador/rotulos`).
- `sources/curriculum-base.md` — **plantilla del CV**: contenido base y estructura de referencia (cabecera con foto, contacto al final). Es lo que copia y adapta `nueva_candidatura.py` en cada candidatura.
- `templates/curriculum-odt.odt` — plantilla de referencia del último ODT generado.
- `output/YYYYMMDD-nombreempresa/` — candidaturas generadas (`pin.png` + `info.md` + CV y carta en `.md`, `.odt` y `.pdf`). **Versionado en git**: cada candidatura queda en su propio directorio con la fecha de generación, de modo que se conserva el historial de lo enviado a cada empresa.
- `ofertas/YYYYMMDD/lista-HHMM.md` — listas de ofertas encontradas por encaje (`pin` de fecha + hora para permitir varias búsquedas el mismo día). **Versionado en git**: guarda qué había disponible cada día. Lo redacta la skill `job-search`.
- `assets/pin.png` — foto de la cabecera del CV; `assets/foto.jpg`, `assets/foto2.jpeg` — alternativas.
- `specs/NN-slug.md` — especificaciones con metadatos (Estado, Depende de, Fecha, Objetivo). Flujo: `spec` → `spec-impl`.

## Búsqueda de ofertas por encaje
- **Estándar:** `ofertas/YYYYMMDD/lista-HHMM.md` con los **criterios usados en la cabecera** (términos, palabras clave, descartes, banda de seniority, geografía, antigüedad máxima), la lista corta con su encaje, el detalle de las mejores —argumento, qué cubre del CV y **qué no cubre**— y las descartadas con su motivo. Sin la cabecera de criterios el resultado no es reconstruible.
- El criterio de búsqueda **no está en ningún fichero**: el agente lo deriva de `sources/curriculum-base.md` en cada ejecución y se lo pasa al script como banderas (`--clave`, `--descartar`, `--ubicacion`, `--seniority`).
- Reparto de responsabilidades: el script `ofertas.py` recoge, deduplica, filtra y puntúa (0-100, reproducible); el agente juzga el encaje y escribe la justificación. La puntuación ordena, no decide.
- Comandos: `ofertas.py buscar <términos> --geo <lugar> [--clave ...] [--formato json]`, `ofertas.py remoto <términos> --ubicacion <países>`, `ofertas.py detalle <id|url>`.
- Fuente principal: el endpoint **público de invitado** de LinkedIn, en solo lectura y a 1 petición por segundo, con caché de 6 h en `cache/` (ignorada por git). No se rellena ni se envía ninguna candidatura: eso es del usuario y en su navegador.
- Skill: `.opencode/skills/job-search/` (ver spec 03)

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
