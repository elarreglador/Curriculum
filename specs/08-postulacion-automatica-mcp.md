# SPEC 08 — Postulación automática diaria con Playwright MCP

> **Estado:** Aprobado

> **Depende de:** 03-busca-ofertas-skill, 04-candidaturas-solo-markdown, 05-salidas-fuera-de-git, 06-estimacion-posibilidades-ofertas, 07-company-jobs-skill

> **Fecha:** 2026-11-24

> **Objetivo:** Crear una skill que, lanzada diariamente por cron a las 09:00, busque ofertas con las skills locales, envíe hasta cuatro candidaturas mediante Playwright MCP y registre en `output/` cada formulario respondido.

> **Enmienda (2026-11-25):** el usuario eliminó el tope diario y fijó como
> prioridad **al menos 15 candidaturas por ejecución**. `CANDIDATURAS_POR_DIA`
> se sustituye por `OBJETIVO_ENVÍOS = 15` (mínimo, sin tope); `UMBRAL_ENCAJE`
> se aplica en pisos sucesivos 55/45/35/25 y `job-search` amplía la búsqueda a
> empleos de informática afines, incluidos puestos de técnico, si faltan
> ofertas. `registrar_envio.py` ya no acepta `--maximo` y `contar` es sólo
> informativo. Las menciones a «cuatro candidaturas», al «tope diario» y a
> «nunca bajar el umbral» que siguen en el cuerpo quedan **derogadas** por
> esta enmienda: en caso de conflicto manda la skill.

---

## Por qué existe esta especificación

`job-search` y `cv-generator` producen material, pero el envío sigue siendo manual: cada mañana hay que abrir portales, repetir las mismas respuestas y adjuntar archivos. Para que la rutina funcione sin supervisión faltan tres piezas que hoy no existen: un lanzador headless, una sesión de navegador persistente y un registro de lo que el contratador pregunta y de lo que se le entrega.

Además, los formularios aplican filtros eliminatorios —años de experiencia, salario, permiso de trabajo— que la puntuación de `ofertas.py` no ve. La selección de las cuatro ofertas debe comprobar esos filtros dentro del propio formulario antes de pulsar «Enviar», y sustituir la oferta que los falle.

---

## Alcance

**En:**

- **Crea la skill de envío automático — `.opencode/skills/auto-apply/SKILL.md` — orquesta la rutina diaria sin supervisión.**
  - Constantes al inicio, editables a mano: `CANDIDATURAS_POR_DIA = 4`, `UMBRAL_ENCAJE = 55`.
  - Modo autónomo: sin preguntas al usuario; ante cualquier duda se omite la oferta y se registra el motivo.
  - Opción `--dry-run`: recorre el flujo completo sin pulsar el botón final de envío.
- **Lanza la rutina a las 09:00 — `.opencode/skills/auto-apply/scripts/postular-diario.sh` — ejecuta OpenCode en modo headless con `--auto`.**
  - El script hace `cd` al repositorio, crea `ofertas/YYYYMMDD/` y redirige la salida a `postulacion-HHMM.log`.
  - La línea de crontab queda documentada en la skill; **no se instala** automáticamente.
- **Selecciona hasta cuatro ofertas — informes de `job-search` y `company-jobs` — ordena por posibilidades y comprueba los filtros del formulario.**
  - Descarta duplicados de `ofertas/envios.json` y de `output/` mediante `revisar_output.py`.
  - Una oferta rechazada por pregunta eliminatoria se sustituye por la siguiente; el umbral 55 no se baja nunca.
- **Prepara cada candidatura — `output/YYYYMMDD-nombreempresa/` — reutiliza `cv-generator` en modo autónomo.**
  - Crea `info.md`, adapta `curriculum-EMPRESA.md` desde la plantilla y escribe `carta-EMPRESA.md`.
  - Si hay duda de empresa homónima o candidatura previa al mismo puesto, omite y registra.
- **Convierte los Markdown a adjuntos — `.opencode/skills/auto-apply/scripts/generar_adjuntos.py` — genera `curriculum-EMPRESA.pdf` y `carta-EMPRESA.pdf`.**
  - Conversión con `markdown` 3.5.2 a HTML temporal y luego LibreOffice headless; DOCX solo si el portal lo exige.
  - LibreOffice directo sobre `.md` produce un PDF con sintaxis Markdown en texto plano: queda prohibido.
- **Rellena y envía cada formulario — MCP `playwright` con perfil persistente en `SENSIBLE/` — completa campos, adjunta archivos y pulsa enviar.**
  - Todas las respuestas salen de `sources/datos-candidatura.md`; no se inventa ningún dato.
  - CAPTCHA, verificación en dos pasos o error del portal: se salta la oferta; fallo de login: se detiene el lote.
- **Registra cada envío — `output/YYYYMMDD-nombreempresa/envio-EMPRESA.md` — guarda URL, fecha, estado, adjuntos y tabla pregunta→respuesta→origen.**
- **Actualiza el índice de duplicados — `ofertas/envios.json` — anota empresa, puesto, URL, fecha, estado y directorio de cada intento.**
- **Escribe el informe diario — `ofertas/YYYYMMDD/postulacion-HHMM.md` — resume seleccionadas, enviadas, bloqueadas y descartadas.**
- **Actualiza la documentación — `AGENTS.md`, `ESTRUCTURA.md` y `specs/04-candidaturas-solo-markdown.md` — añade la skill y la excepción de conversión.**
  - `README.md` no se toca: es el CV público, no documentación interna.

**Fuera del alcance:**

- Eludir CAPTCHAs, verificación en dos pasos ni ninguna protección anti-bot.
- Introducir datos bancarios, pagar tasas o firmar contratos.
- Gestión de respuestas, entrevistas ni seguimiento posterior al envío.
- Modificar los criterios permanentes de `sources/criterios-busqueda.md`.
- Cambiar `cv-generator`: sigue generando solo Markdown.
- Instalar la línea de crontab ni realizar envíos reales durante la implementación; las pruebas son con `--dry-run`.
- Traducir ofertas ni redactar CV o carta desde cero: se adapta la plantilla existente.
- Añadir campos al esquema único de `ofertas.py`: la puntuación ordena, el agente decide.

---

## Modelo de datos

### 1. Plantilla de respuestas: `sources/datos-candidatura.md`

Fichero versionable, interno, con valores permanentes. Los datos verificables se copian de `sources/curriculum-base.md`; los que no constan se dejan como `No consta`. Una pregunta **obligatoria** del formulario cuyo valor sea `No consta` produce el estado `sin-responder` y **ningún envío**.

```markdown
# Datos para formularios de candidatura

> Interno. Se usa tal cual en los formularios; no se envía como documento.

## Identidad y contacto

| Campo | Valor |
| --- | --- |
| Nombre completo | David Moreno Bolívar |
| Email | elarreglador@protonmail.com |
| Teléfono | 651 73 77 65 |
| Localidad | No consta |

## Experiencia y disponibilidad

| Campo | Valor | Origen |
| --- | --- | --- |
| Experiencia como desarrollador | 18 meses | sources/curriculum-base.md |
| Experiencia total en hardware e infraestructura | Más de 20 años | sources/curriculum-base.md |
| Salario pretendido | 24000-30000 EUR anual segun oferta | — |
| Disponibilidad | inmediata | — |
| Permiso de trabajo en España | si | — |
| Movilidad | Valencia base; Barcelona y Madrid desplazable | sources/criterios-busqueda.md |

## Respuestas frecuentes

| Pregunta habitual | Respuesta |
| --- | --- |
| Por qué te interesa el puesto | [texto corto, derivado del CV y de la oferta] |
| Nivel de inglés | B1 |

## Reglas de uso

- Nunca rellenar un dato con una estimación del agente.
- Ante una pregunta no prevista, responder solo si el valor está en este fichero.
- Si la pregunta es obligatoria y no tiene valor, omitir la oferta y registrarla.
```

### 2. Índice de envíos: `ofertas/envios.json`

Ignorado por git (el directorio `ofertas/` ya lo está). Clave de deduplicación: `url`; si falta, `empresa` + `puesto`.

```json
{
  "version": 1,
  "envios": [
    {
      "empresa": "EDICOM",
      "puesto": "Desarrollador IoT",
      "url": "https://...",
      "fecha_envio": "2026-11-24T09:12:00+01:00",
      "estado": "enviada",
      "directorio": "output/20261124-edicom"
    }
  ]
}
```

Estados admitidos: `enviada`, `descartada-por-filtro`, `bloqueada`, `sin-responder`, `error`. El tope diario se calcula contando las entradas de **hoy** con estado `enviada`.

### 3. Registro por candidatura: `output/YYYYMMDD-nombreempresa/envio-EMPRESA.md`

```markdown
# Envío de candidatura — EMPRESA

> Registro interno. No se envía a la empresa.

- **Fecha y hora:** YYYY-MM-DDTHH:MM:SS+01:00
- **Oferta:** [URL de la oferta original]
- **Puesto:** [nombre del puesto]
- **Canal:** LinkedIn Easy Apply | web de la empresa
- **Estado:** enviada | descartada-por-filtro | bloqueada | sin-responder | error
- **Adjuntos entregados:** curriculum-EMPRESA.pdf, carta-EMPRESA.pdf | solo CV | ninguno
- **Motivo del estado:** [obligatorio si el estado no es «enviada»; una frase]

## Información solicitada y entregada

| Pregunta del formulario | Respuesta entregada | Origen de la respuesta |
| --- | --- | --- |
| Años de experiencia como desarrollador | 18 meses | sources/datos-candidatura.md |

## Archivos generados

- `curriculum-EMPRESA.md` → `curriculum-EMPRESA.pdf`
- `carta-EMPRESA.md` → `carta-EMPRESA.pdf`
- `info.md` (interno, no enviado)

## Incidencias

- [Ninguna, o descripción del bloqueo sin intentar eludirlo]
```

### 4. Sesión del navegador

`SENSIBLE/playwright-profile/` guarda el perfil persistente del MCP `playwright`. Se añade `/SENSIBLE/` a `.gitignore`. Ninguna credencial, token ni cookie se escribe en `SKILL.md`, en el informe ni en `output/`.

---

## Plan de implementación

1. Crear este documento `specs/08-postulacion-automatica-mcp.md` y añadir `/SENSIBLE/` a `.gitignore`. Dejar el estado en `Borrador`.
2. Crear `sources/datos-candidatura.md` con la plantilla anterior y el fichero inicial `ofertas/envios.json` (`{"version": 1, "envios": []}`). El usuario completa los campos `No consta` antes del primer envío real.
3. Implementar `.opencode/skills/auto-apply/scripts/generar_adjuntos.py`: Markdown → HTML temporal en `SENSIBLE/tmp/` → PDF con LibreOffice headless (`-env:UserInstallation` propio para no chocar con una instancia abierta), y DOCX bajo petición. Prueba de humo: convertir un CV de `output/` y comprobar con `pdftotext` que no aparece sintaxis Markdown.
4. Implementar `.opencode/skills/auto-apply/scripts/registrar_envio.py`: alta en `ofertas/envios.json` con deduplicación por `url` y recuento de envíos del día. Probar con dos altas del mismo `url`: la segunda no duplica el registro.
5. Configurar el MCP `playwright` con `--user-data-dir SENSIBLE/playwright-profile` en `~/.config/opencode/opencode.jsonc` (fuera del repositorio: requiere consentimiento explícito). Verificar que una sesión iniciada sigue viva tras dos ejecuciones separadas del MCP.
6. Escribir `.opencode/skills/auto-apply/SKILL.md` con las constantes del alcance y el flujo completo: buscar → seleccionar → preparar candidatura → convertir adjuntos → comprobar filtros del formulario → rellenar → enviar → registrar → informe. Incluir las reglas de modo autónomo y de `--dry-run`.
7. Crear `.opencode/skills/auto-apply/scripts/postular-diario.sh`: `cd` al repositorio, `mkdir -p ofertas/YYYYMMDD`, ejecutar `opencode run --auto --archived --title "postulación diaria YYYYMMDD" "Ejecuta la skill auto-apply"` con redirección a `postulacion-HHMM.log`. Documentar en la skill la línea de crontab `0 9 * * * <ruta>/postular-diario.sh` **sin instalarla**.
8. Actualizar `AGENTS.md` y `ESTRUCTURA.md` con la nueva skill, el fichero de datos, el índice y el registro de envío; añadir una enmienda en `specs/04-candidaturas-solo-markdown.md` que autorice la conversión exclusivamente desde `auto-apply`.
9. Ejecutar una prueba controlada con `--dry-run` sobre ofertas reales: verificar que se generan `ofertas/YYYYMMDD/postulacion-HHMM.md`, el informe, los adjuntos y los registros `envio-EMPRESA.md`, y que **ningún** registro queda con estado `enviada`.

---

## Criterios de aceptación

- [ ] Existe `specs/08-postulacion-automatica-mcp.md` con estado `Aprobado`.
- [ ] Existe `.opencode/skills/auto-apply/SKILL.md` con `CANDIDATURAS_POR_DIA = 4` y `UMBRAL_ENCAJE = 55` una sola vez, al principio.
- [ ] `postular-diario.sh` ejecuta `opencode run --auto`, escribe `postulacion-HHMM.log` y su línea de crontab está documentada pero no instalada.
- [ ] La selección usa solo los informes de `job-search` y `company-jobs`, filtra por encaje ≥ 55 y ordena por posibilidades; nunca baja el umbral.
- [ ] Se omiten las ofertas ya registradas en `ofertas/envios.json` o con candidatura previa al mismo puesto en `output/`, y la omisión queda registrada.
- [ ] Las preguntas eliminatorias del formulario se comprueban antes de enviar; si fallan, se registra `descartada-por-filtro` y se sustituye la oferta por la siguiente.
- [ ] Toda respuesta entregada procede de `sources/datos-candidatura.md`; una pregunta obligatoria sin valor produce `sin-responder` y ningún envío.
- [ ] `generar_adjuntos.py` produce un PDF legible sin sintaxis Markdown visible, comprobado con `pdftotext`; solo genera DOCX si el portal lo exige.
- [ ] Los formularios se rellenan con el MCP `playwright` usando el perfil persistente de `SENSIBLE/`, ignorado por git.
- [ ] Cada intento deja un `envio-EMPRESA.md` con URL, fecha, estado, adjuntos, tabla pregunta→respuesta→origen e incidencias.
- [ ] `ofertas/envios.json` se actualiza con un registro por intento y no admite duplicados por `url`.
- [ ] Un CAPTCHA, 2FA o error de portal salta la oferta y la registra como `bloqueada`; un fallo de login detiene el lote y lo anota en el informe.
- [ ] `--dry-run` recorre el flujo sin pulsar «Enviar» y no escribe ningún estado `enviada`.
- [ ] Cada ejecución genera `ofertas/YYYYMMDD/postulacion-HHMM.md` con seleccionadas, enviadas, bloqueadas y descartadas, además del `.log`.
- [ ] `AGENTS.md`, `ESTRUCTURA.md` y la enmienda de la spec 04 están actualizados; `README.md` permanece intacto.
- [ ] `.gitignore` incluye `/SENSIBLE/` y ningún fichero versionado contiene credenciales ni datos de sesión.

---

## Decisiones

- **Sí:** Playwright MCP para todo el navegador. Ya se ha usado en este repositorio y admite perfil persistente, necesario para la sesión de LinkedIn.
- **Sí:** perfil de navegador en `SENSIBLE/playwright-profile/`, ignorado por git. Sin credenciales en código, documentación ni informes.
- **Sí:** envío real pulsando el botón final, con tope de cuatro candidaturas por día y registro posterior. Es la automatización solicitada.
- **Sí:** `sources/datos-candidatura.md` como fuente única de respuestas de formulario. Versionable y auditable; el cron no puede preguntar.
- **Sí:** conversión Markdown → HTML → PDF desde la skill nueva, con enmienda en la spec 04. Verificado: LibreOffice directo sobre `.md` genera un PDF en texto plano con los asteriscos y almohadillas visibles.
- **Sí:** `cv-generator` sigue intacto y solo produce Markdown. La conversión es competencia del canal de envío, no de la generación.
- **Sí:** script wrapper más línea de crontab documentada. El usuario conserva el control de instalar el lanzamiento; el repositorio no modifica su crontab.
- **Sí:** `envio-EMPRESA.md` junto al CV y la carta. Separa lo que pidió el contratador de lo que se le entregó, con su origen.
- **Sí:** máximo cuatro ofertas sin bajar el umbral de 55. Si una cae en un filtro eliminatorio, se sustituye; si no hay más, se envían menos.
- **Sí:** saltar y registrar CAPTCHA, 2FA o errores de portal. No se eluden protecciones; solo un fallo de login detiene el lote.
- **Sí:** índice `ofertas/envios.json` como fuente de deduplicación. `output/` se sigue usando en la revisión previa, pero el índice es la consulta rápida.
- **Sí:** modo autónomo sin confirmaciones y con omisión ante la duda. Las preguntas de `cv-generator` (empresa homónima, puesto repetido) se resuelven omitiendo y registrando.
- **Sí:** opción `--dry-run` y pruebas sin envíos reales durante la implementación. El envío a una empresa es una acción externa e irreversible.
- **No:** tocar `README.md`. Es el CV público que se entrega a las empresas, no documentación de herramientas internas.
- **No:** añadir `posibilidades` ni datos de formulario al esquema de `ofertas.py`. La puntuación ordena; el juicio cualitativo sigue siendo del agente.
- **No:** gestionar respuestas, entrevistas ni ningún paso posterior al envío. Será otra especificación si llega el caso.

---

## Riesgos

| Riesgo | Mitigación |
| --- | --- |
| El portal cambia sus campos o el flujo de Easy Apply | Usar snapshots del MCP en cada paso; ante selectores dudosos, `bloqueada` y registro con el estado del formulario |
| La cuenta de LinkedIn se limita por envíos frecuentes | Tope de cuatro al día, ritmo pausado entre formularios y sin reintentos sobre CAPTCHAs |
| La sesión del navegador caduca | Perfil persistente en `SENSIBLE/`; si falla el login, se detiene el lote y se anota en el informe |
| El PDF sale con sintaxis Markdown o sin la foto | Conversión vía HTML con rutas de imagen absolutas; verificación obligatoria con `pdftotext` en la prueba de humo |
| Pregunta obligatoria no prevista en `sources/datos-candidatura.md` | Estado `sin-responder`, sin envío y pregunta anotada literalmente para añadirla al fichero |
| La misma oferta aparece con dos URL distintas | Deduplicación por `url` y, como respaldo, comparación de empresa + puesto con `revisar_output.py` |
| El cron no encuentra `opencode`, el MCP o el directorio | El wrapper usa rutas absolutas y `cd` explícito; el log captura el error y el informe queda sin entradas |
| Datos personales o de sesión acaban versionados | `/SENSIBLE/` en `.gitignore` y regla de no copiar cookies ni tokens a `output/` ni al informe |
| Se envía una candidatura a una empresa homónima | Sin confirmación interactiva, la duda resuelve omisión y registro; nunca se envía «a ciegas» |

---

## Lo que **no** está en esta especificación

- Elusión de CAPTCHAs, 2FA o cualquier mecanismo de seguridad de los portales.
- Reenvío automático, cartas de seguimiento ni gestión de entrevistas.
- Pago de tasas, datos bancarios o firma de documentos.
- Modificación de `sources/criterios-busqueda.md` ni de la banda de seniority.
- Generación de ODT ni cambio del estándar solo-Markdown de `cv-generator`.
- Instalación del crontab ni envíos reales durante la implementación.
- Cambios en `README.md`, que es el CV público.
- Notificaciones por correo, integraciones con bases de datos externas ni panel de control.
