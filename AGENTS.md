# AGENTS.md

Repositorio personal de CV/portfolio (David Moreno Bolívar). No es un proyecto de software: no hay build, tests, lint ni CI. No inventes comandos ni flujos de trabajo.

## Convenciones
- Contenido (CV, specs, commits): **castellano**. 

## Estructura
- `sources/curriculum-github.md` — fuente de verdad del CV en formato GitHub (con badges del repo `elarreglador/rotulos`).
- `sources/curriculum-base.md` — **plantilla del CV**: contenido base y estructura de referencia (cabecera con foto, contacto al final). Es lo que copia y adapta `nueva_candidatura.py` en cada candidatura.
- `sources/criterios-busqueda.md` — **criterios permanentes de búsqueda** de ofertas: banda de seniority (`junior,mid`), geografía (Valencia base; Barcelona y Madrid desplazable; resto de España descartado en presencial/híbrido, el remoto admite cualquier sede de España o Europa) y remoto. Interno, no va en el CV. Única fuente de esos tres criterios para la skill `job-search`.
- `sources/datos-candidatura.md` — **respuestas permanentes a formularios** (experiencia, salario, disponibilidad, permiso de trabajo, idioma). Única fuente de datos para la skill `auto-apply`; un dato ausente no se inventa.
- `templates/curriculum-odt.odt` — plantilla de referencia histórica (no usada por el flujo actual).
- `output/YYYYMMDD-nombreempresa/` — candidaturas generadas (`pin.png` + `info.md` + CV y carta en `.md`, más `envio-EMPRESA.md` si se ha intentado el envío). **Ignorado por git**: cada candidatura queda en su propio directorio con la fecha de generación, de modo que se conserva el historial de lo enviado a cada empresa.
- `ofertas/YYYYMMDD/lista-HHMM.md` — listas de ofertas encontradas por encaje (`pin` de fecha + hora para permitir varias búsquedas el mismo día). **Ignorado por git**: guarda qué había disponible cada día. Lo redacta la skill `job-search`.
- `ofertas/YYYYMMDD/postulacion-HHMM.md` — informe diario de envíos: seleccionadas, enviadas, bloqueadas y descartadas. Lo redacta la skill `auto-apply`.
- `ofertas/envios.json` — índice local de envíos por URL (o empresa + puesto). **Ignorado por git**: evita repetir candidaturas. No hay tope diario.
- `assets/pin.png` — foto de la cabecera del CV; `assets/foto.jpg`, `assets/foto2.jpeg` — alternativas.
- `SENSIBLE/` — perfil persistente del navegador (`playwright-profile/`) y temporales de conversión. **Ignorado por git**: nunca contiene credenciales en texto ni se documenta su contenido.
- `specs/NN-slug.md` — especificaciones con metadatos (Estado, Depende de, Fecha, Objetivo). Flujo: `spec` → `spec-impl`.

## Búsqueda de ofertas por encaje
- **Estándar:** `ofertas/YYYYMMDD/lista-HHMM.md` con los **criterios usados en la cabecera** (términos, palabras clave, descartes, banda de seniority, geografía, antigüedad máxima), la lista corta con su encaje, el detalle de las mejores —argumento, qué cubre del CV y **qué no cubre**— y las descartadas con su motivo. Sin la cabecera de criterios el resultado no es reconstruible.
- El criterio de búsqueda tiene dos fuentes: `sources/criterios-busqueda.md` fija **banda de seniority, geografía y remoto** (permanente); el resto (términos, `--clave`, `--descartar`) lo deriva el agente de `sources/curriculum-base.md` en cada ejecución. Se pasan al script como banderas (`--clave`, `--descartar`, `--ubicacion`, `--seniority`).
- Reparto de responsabilidades: el script `ofertas.py` recoge, deduplica, filtra y puntúa (0-100, reproducible); el agente juzga el encaje y escribe la justificación. La puntuación ordena, no decide.
- El informe incluye una **reserva con encaje 25-54** (`lista-HHMM.md`) y, si `auto-apply` no llega a 15 envíos, un **modo ampliado** (`lista-ampliada-HHMM.md`) con tres grupos de términos de informática, incluidos puestos de técnico, con encaje ≥ 25 y sin contradecir los criterios permanentes.
- Comandos: `ofertas.py buscar <términos> --geo <lugar> [--clave ...] [--formato json]`, `ofertas.py remoto <términos> --ubicacion <países>`, `ofertas.py detalle <id|url>`.
- Fuente principal: el endpoint **público de invitado** de LinkedIn, en solo lectura y a 1 petición por segundo, con caché de 6 h en `cache/` (ignorada por git). No se rellena ni se envía ninguna candidatura: eso es del usuario y en su navegador.
- Además, la skill **delega** la revisión de la **web de empleo de las empresas registradas** en `ofertas/empresas.json` a la skill `company-jobs` (spec 07): busca `url_empleo` si falta, la anota o elimina la empresa si no existe, anota la revisión (`ultima_revision` + `ultimas_ofertas_vistas` + `instrucciones_agente`) y genera su propio informe en `ofertas/YYYYMMDD/empresas-HHMM.md`. Las ofertas encontradas se agregan al informe de `job-search` junto a las de otras fuentes.
- Skill: `.opencode/skills/job-search/` (ver spec 03)

## Generación de candidaturas por empresa
- **Estándar:** por cada empresa, un directorio `output/YYYYMMDD-nombreempresa/` con `pin.png` + `info.md` + `curriculum-NOMBREEMPRESA.md` + `carta-NOMBREEMPRESA.md`. El directorio va en minúsculas y sin acentos; los ficheros en mayúsculas.
- `info.md` — datos de la empresa y de la oferta, con sus fuentes. **Uso interno, no se envía a la empresa**: es el soporte de las cifras citadas en el CV y en la carta. Lo redacta el agente (Paso 5 de la skill); un dato sin verificar se escribe como `No consta`, nunca estimado.
- Flujo: `nueva_candidatura.py` deja el directorio con la foto y una copia de `sources/curriculum-base.md` → el agente **adapta el texto** de esa copia (no la reescribe desde cero).
- Comandos: `nueva_candidatura.py "Empresa"` prepara el andamiaje (`--foto` cambia la imagen, `--sin-foto` la omite)

- La cabecera del CV es una tabla HTML de dos columnas con la foto. Sus anchos van en **píxeles absolutos** (`700` = `90` + `610`) a propósito: el importador HTML de LibreOffice ignora los porcentajes y con `width="100%"` el nombre se parte en tres líneas.
- Skill automatizada: `.opencode/skills/cv-generator/` (ver spec 02)

## Postulación automática diaria
- **Estándar:** la skill `auto-apply` (spec 08) toma los informes de `job-search` y `company-jobs`, detecta los desajustes de filtro del formulario (no excluyentes) y escribe `ofertas/YYYYMMDD/postulacion-HHMM.md` con seleccionadas, enviadas, bloqueadas y omitidas por duplicado. **Sin tope diario**: prioriza al menos 15 candidaturas por ejecución, ordenadas por encaje, con pisos sucesivos 55/45/35/25; si faltan ofertas, `job-search` amplía la búsqueda a empleos de informática afines, incluidos puestos de técnico, hasta agotar las fuentes.
- Las respuestas salen **solo** de `sources/datos-candidatura.md`. Una pregunta obligatoria sin valor se deja en blanco o con la opción neutra y se envía igual; **si es numérica** (años de experiencia con una tecnología sin declarar), se responde `0` por decisión del usuario (2026-11-25) para no abandonar la candidatura: declara cero experiencia en esa tecnología, no es un dato inventado. Nunca se inventa un dato. Los desajustes de filtro y las preguntas sin dato, incluidos esos `0`, se anotan **solo** en `output/YYYYMMDD-nombreempresa/envio-EMPRESA.md`. Los estados son `enviada`, `descartada-por-filtro`, `bloqueada`, `sin-responder` y `error`; los dos de filtro son legacy (registros históricos, ya no se producen).
- Cada intento deja `output/YYYYMMDD-nombreempresa/envio-EMPRESA.md` con la pregunta del contratador, la respuesta entregada y su origen. El índice `ofertas/envios.json` evita duplicados, sin limitar la cantidad de envíos.
- Cada oferta con estado `enviada` dispara un aviso por Telegram (spec 09) mediante `.opencode/skills/auto-apply/scripts/notificar_telegram.py`: el token se lee en tiempo de ejecución del entorno o de `D-Lab/info_sensible/telegram.env`, y el destino de `SENSIBLE/telegram-postulacion.env` (o del entorno), sin tocar el chat de las alertas del clúster. Es best-effort y nunca se ejecuta en `--dry-run`.
- Los adjuntos PDF se generan desde el Markdown con `generar_adjuntos.py` (HTML intermedio + LibreOffice headless). LibreOffice directo sobre `.md` produce texto plano: no usarlo. `cv-generator` sigue generando solo `.md`.
- El lanzador es `.opencode/skills/auto-apply/scripts/postular-diario.sh`: ejecuta `opencode run --auto` y redirige a `postulacion-HHMM.log`. La línea de crontab (`0 9 * * * …`) está documentada en la skill, **no instalada**.
- Pruebas: `postular-diario.sh --dry-run` recorre el flujo sin pulsar «Enviar». Ningún registro queda con estado `enviada` en una prueba.
- Skill: `.opencode/skills/auto-apply/` (ver spec 08)

## Git
- Repositorio git inicializado. Remote: `https://github.com/elarreglador/Curriculum`.
