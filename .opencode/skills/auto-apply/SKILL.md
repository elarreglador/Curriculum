---
name: auto-apply
description: Presenta candidaturas de forma automática con Playwright MCP en LinkedIn y en webs de empresas, y registra cada formulario respondido en output/. Úsala para la rutina diaria de postulación lanzada por cron.
---

# auto-apply

Skill de envío automático de candidaturas. Toma las ofertas de los informes de
`job-search` y `company-jobs`, prepara el CV y la carta con `cv-generator`, rellena
el formulario con el MCP `playwright` y deja en `output/` el registro de lo que
pidió el contratador y de lo que se le entregó.

## Configuración

> **CANDIDATURAS_POR_DIA = 4**
>
> **UMBRAL_ENCAJE = 55**
>
> Cambia estos dos valores aquí. El resto de la skill habla de «el tope diario»
> y «el umbral de encaje»: no los repite.

## Principio de diseño

Los scripts resuelven **lo determinista** (convertir archivos, deduplicar,
contar envíos, escribir el índice). El agente resuelve **lo cualitativo**: si la
oferta merece el envío, si el formulario es compatible, qué significa cada
pregunta y si hay duda. La puntuación de `ofertas.py` ordena; no decide.

Esta skill trabaja **sin supervisión**: no hace preguntas al usuario. Ante
cualquier duda —empresa homónima, puesto repetido, pregunta sin respuesta— se
omite la oferta y se registra el motivo. Es preferible enviar menos candidaturas
que enviar una equivocada.

## Cuándo usar esta skill

- Rutina diaria lanzada por `postular-diario.sh` desde crontab.
- Cuando el usuario pida «postúlame hoy» o «envía las mejores ofertas».
- No se usa para buscar ofertas: para eso existe `job-search`.

## Herramientas

| Herramienta | Uso |
| --- | --- |
| `bash` | ejecutar los scripts y las skills locales |
| MCP `playwright` | navegar, leer el formulario, rellenarlo, adjuntar archivos y enviar |
| `read` | consultar datos del candidato, informes y registros |
| `webfetch` | completar `info.md` con datos de la empresa y de la oferta |
| `write` / `edit` | redactar `info.md`, CV, carta, registro e informe diario |

El perfil del navegador vive en `SENSIBLE/playwright-profile/`, configurado en el
servidor MCP. Nunca escribas credenciales, cookies ni tokens en ficheros del
repositorio.

## Archivos que intervienen

| Archivo | Papel |
| --- | --- |
| `sources/curriculum-base.md` | plantilla que se adapta, nunca se reescribe |
| `sources/criterios-busqueda.md` | banda y geografía permanentes |
| `sources/datos-candidatura.md` | **única** fuente de respuestas de formularios |
| `ofertas/YYYYMMDD/lista-HHMM.md` | salida de `job-search` |
| `ofertas/YYYYMMDD/empresas-HHMM.md` | salida de `company-jobs` |
| `ofertas/envios.json` | índice de deduplicación y tope diario |
| `output/YYYYMMDD-nombreempresa/` | candidatura y registro de envío |
| `ofertas/YYYYMMDD/postulacion-HHMM.md` | informe del lote |

## Comandos

```bash
A=.opencode/skills/auto-apply/scripts
C=.opencode/skills/cv-generator/scripts
R=.opencode/skills/company-research/scripts/empresas.py
S=.opencode/skills/job-search/scripts/ofertas.py

# 1. ¿Cuántas candidaturas caben hoy?
python3 $A/registrar_envio.py contar --maximo <tope diario>

# 2. Comprobar duplicados antes de preparar nada
python3 $C/revisar_output.py "EMPRESA" --puesto "PUESTO"

# 3. Preparar el directorio de la candidatura
python3 $C/nueva_candidatura.py "EMPRESA"

# 4. Generar los adjuntos (añadir --docx solo si el portal lo exige)
python3 $A/generar_adjuntos.py \
  output/YYYYMMDD-nombreempresa/curriculum-EMPRESA.md \
  output/YYYYMMDD-nombreempresa/carta-EMPRESA.md --verificar

# 5. Registrar el resultado final de cada oferta
python3 $A/registrar_envio.py registrar \
  --empresa "EMPRESA" --puesto "PUESTO" --url "URL" \
  --estado enviada --directorio output/YYYYMMDD-nombreempresa \
  --maximo <tope diario>
```

`registrar` devuelve JSON. `registrado: false` con `motivo: tope_diario` (código
de salida 2) significa que el lote debe parar. Un `url` repetido no crea una
entrada nueva: actualiza la existente.

## Flujo de interacción

### Paso 0 — Preparar la ejecución

1. Detecta si la orden contiene `--dry-run`. En modo seco se recorre todo el
   flujo **menos** el clic final de envío.
2. Lee los dos valores de la sección Configuración y `sources/datos-candidatura.md`.
3. Consulta el hueco disponible con `registrar_envio.py contar`. Si no queda
   hueco, escribe el informe con el lote vacío y termina.
4. No pidas confirmaciones: esta skill nunca interactúa con el usuario.

### Paso 1 — Obtener las ofertas

1. Ejecuta `job-search` con sus criterios habituales (cuatro pasadas: Valencia,
   Barcelona, Madrid y remoto). Su Paso 2b delega en `company-jobs`; asegúrate de
   que se ejecuta para incorporar las ofertas de `ofertas/empresas.json`.
2. Sus reglas de «mostrar la lista antes de escribir» y de «confirmar empresa»
   quedan **suspendidas** aquí: el informe es la entrada de datos, no una
   pantalla de aprobación.
3. Lee `ofertas/YYYYMMDD/lista-HHMM.md` y `ofertas/YYYYMMDD/empresas-HHMM.md`.
   Si no hay ningún informe de hoy o ambos están vacíos, escribe el informe de
   postulación con «sin ofertas disponibles» y termina.

### Paso 2 — Preseleccionar

1. Descarta toda oferta con encaje inferior al umbral. **No lo bajes nunca**,
   aunque queden menos ofertas de las que caben en el lote.
2. Ordena por `Posibilidades` de mayor a menor. `No consta` va al final.
3. Descarta las ya registradas en `ofertas/envios.json` (por `url`, o por
   empresa + puesto si no hay URL) y las que `revisar_output.py` detecte como
   candidatura previa al mismo puesto. Anota cada omisión para el informe.
4. Compón una **cola** con las restantes, no solo las primeras: las que fallen
   un filtro del formulario se sustituyen por la siguiente de la cola.
5. No presentes dos candidaturas al mismo puesto de empresa(s) relacionadas
   detectadas en la deduplicación de `job-search`.

### Paso 3 — Abrir la oferta y detectar el canal

1. Navega a la URL con `browser_navigate` y toma un `browser_snapshot`.
2. Clasifica el canal: `LinkedIn Easy Apply` o `web de la empresa`.
3. Si la URL no abre, no hay formulario o hace falta un navegador distinto,
   registra `error` con el motivo y pasa a la siguiente de la cola.
4. Si el acceso exige iniciar sesión y la sesión persistente no está activa,
   **detén el lote**: anota el fallo de login en el informe y termina.

### Paso 4 — Comprobar los filtros eliminatorios antes de seguir

1. Lee con `browser_snapshot` / `browser_find` los campos obligatorios y sus
   opciones. Busca especialmente años de experiencia, salario, permiso de
   trabajo, ubicación, seniority y disponibilidad.
2. Compara cada condición con `sources/datos-candidatura.md`.
   - Si una condición excluyente no se cumple (por ejemplo, exige más años de
     experiencia de los declarados), registra `descartada-por-filtro` con la
     pregunta literal y la respuesta que se habría entregado. Pasa a la
     siguiente de la cola.
   - Si una pregunta **obligatoria** no tiene valor en el fichero de datos,
     registra `sin-responder` con la pregunta literal. Pasa a la siguiente.
   - Si es opcional y no tiene valor, se deja en blanco o se elige la opción
     neutra del formulario, si la hay.
3. No rellenas ni envías nada de esta oferta hasta que pase este paso.

### Paso 5 — Preparar la candidatura

1. Llama a `cv-generator` en modo autónomo: sus confirmaciones de empresa,
   puesto repetido y revisión de `info.md` se resuelven así:
   - Duda de empresa homónima → registrar `error` y omitir la oferta.
   - Puesto repetido detectado en el Paso 2 → ya descartada; no llegar aquí.
   - `info.md` se escribe sin mostrarlo al usuario, con la misma regla de
     «No consta» y la tabla de fuentes de la skill original.
2. No reescribas el CV: adapta la copia que deja `nueva_candidatura.py`.
3. Si algún dato de la empresa no se puede verificar, escribe `No consta`.
4. Crea `envio-EMPRESA.md` con la plantilla del apartado «Registro de envío»,
   dejando el estado pendiente de fijar al final.

### Paso 6 — Generar los adjuntos

1. Ejecuta `generar_adjuntos.py` sobre `curriculum-EMPRESA.md` y
   `carta-EMPRESA.md` con `--verificar`.
2. Genera DOCX solo si el formulario lo pide expresamente; si admite PDF, PDF.
3. Si el PDF no pasa la verificación o falta la foto, registra `error` y pasa a
   la siguiente oferta. Nunca adjuntes un `.md`.

### Paso 7 — Rellenar el formulario

1. Usa `browser_fill_form` para los campos de texto y `browser_type` cuando el
   control no admita relleno directo. Usa `browser_file_upload` para los
   adjuntos.
2. Cada respuesta debe venir de `sources/datos-candidatura.md` o, si es un
   texto libre de motivación, del CV adaptado y de la oferta. Guarda en memoria
   la tripleta **pregunta → respuesta → origen** para el registro.
3. Marca la casilla «Seguir a [empresa]» cuando aparezca: es la preferencia
   permanente del usuario. No marques otras casillas de marketing ni
   comunicaciones comerciales.
4. Si aparece CAPTCHA o verificación en dos pasos: no lo eludas. Registra
   `bloqueada`, cierra limpiamente y pasa a la siguiente.
5. Si un error del portal impide continuar, registra `bloqueada` con el mensaje
   visto en pantalla y pasa a la siguiente.

### Paso 8 — Enviar y confirmar

1. Antes de pulsar el botón final, revisa el `browser_snapshot`: las respuestas
   eliminatorias siguen siendo las del fichero de datos y los archivos están
   adjuntos.
2. **Si es modo seco:** detente aquí. Fija el estado `bloqueada` con motivo
   «Ejecución en modo seco: no se pulsó enviar» y pasa a la siguiente.
3. Si no es modo seco, pulsa «Enviar» una sola vez y espera la pantalla de
   confirmación. Sin confirmación visible, registra `error`.
4. Con confirmación, fija el estado `enviada` y anota la fecha y hora reales.

### Paso 9 — Registrar

1. Rellena `envio-EMPRESA.md` con todos los campos, incluidas las tripletas
   pregunta → respuesta → origen recogidas en el Paso 7. Si el estado no es
   `enviada`, el **motivo** es obligatorio.
2. Llama a `registrar_envio.py registrar` con el estado final y el tope diario.
   Si devuelve `tope_diario`, termina el lote y anótalo en el informe.
3. Repite desde el Paso 3 con la siguiente oferta de la cola hasta agotar el
   hueco disponible o la cola.

### Paso 10 — Escribir el informe diario

`YYYYMMDD` es la fecha de hoy; `HHMM` permite varias ejecuciones el mismo día.

```markdown
# Postulación automática — YYYY-MM-DD

> Búsqueda interna. No se envía a ninguna empresa.

## Cabecera

- **Modo:** normal | --dry-run
- **Fecha y hora:** YYYY-MM-DDTHH:MM:SS+01:00
- **Fuentes:** informes de job-search y company-jobs de hoy
- **Umbral de encaje:** [valor de la configuración]
- **Tope diario:** [valor de la configuración]
- **Orden:** Posibilidades descendente (tras filtrar por encaje)

## Seleccionadas

| # | Empresa | Puesto | Canal | Encaje | Posibilidades | Estado | Registro |
| --- | --- | --- | --- | --- | --- | --- | --- |

## Enviadas

- [empresa, puesto, hora y directorio, o «Ninguna»]

## Descartadas por filtro

| Empresa | Puesto | Pregunta que excluye | Respuesta que se habría entregado |
| --- | --- | --- | --- |

## Bloqueadas y con error

| Empresa | Puesto | Estado | Motivo |
| --- | --- | --- | --- |

## Sin responder

| Empresa | Puesto | Pregunta literal |
| --- | --- | --- |

## Omisiones por duplicado

| Empresa | Puesto | Motivo |
| --- | --- | --- |

## Fuentes

| Dato | Fuente | Fecha |
| --- | --- | --- |
```

Reglas del informe: si no hay ofertas, indícalo en «Seleccionadas» y deja el
resto de secciones con «Ninguna». No escribas datos que no estén en los informes
de entrada ni en los registros de `output/`.

## Registro de envío

Plantilla de `output/YYYYMMDD-nombreempresa/envio-EMPRESA.md`:

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

## Archivos generados

- `curriculum-EMPRESA.md` → `curriculum-EMPRESA.pdf`
- `carta-EMPRESA.md` → `carta-EMPRESA.pdf`
- `info.md` (interno, no enviado)

## Incidencias

- [Ninguna, o descripción del bloqueo sin intentar eludirlo]
```

Estados admitidos: `enviada`, `descartada-por-filtro`, `bloqueada`,
`sin-responder`, `error`.

## Modo seco

La orden `opencode run --auto ... "Ejecuta la skill auto-apply en modo --dry-run"`
o `postular-diario.sh --dry-run` recorre las ofertas, genera CV, carta, adjuntos,
registros e informe, pero **no pulsa «Enviar»**. Ningún registro queda con estado
`enviada`. Es la única forma de probar el flujo contra ofertas reales.

## Crontab

El lanzador está en `scripts/postular-diario.sh`. La línea que el usuario debe
añadir a su crontab (la skill **no la instala**) es:

```cron
0 9 * * * /home/elarreglador/Documentos/trabajo/.opencode/skills/auto-apply/scripts/postular-diario.sh
```

Cada ejecución escribe `ofertas/YYYYMMDD/postulacion-HHMM.log`.

## Reglas importantes

1. **Sin preguntas.** Modo autónomo: duda → omisión con registro.
2. **Sin datos inventados.** Toda respuesta sale de `sources/datos-candidatura.md`;
   una obligatoria sin valor detiene esa candidatura.
3. **Sin capas de umbral.** Nunca bajes el umbral de encaje ni envíes más del
   tope diario.
4. **Sin elusión.** CAPTCHA, 2FA y protecciones anti-bot se registran, no se
   sortean. Un fallo de login detiene el lote.
5. **Sin secretos.** Nada de credenciales en `output/`, en el informe ni en esta
   skill. El perfil del navegador solo vive en `SENSIBLE/`.
6. **Sin duplicados.** URL repetida, o empresa + puesto repetidos, se omiten.
7. **Sin tocar `cv-generator` ni `README.md`.** Esta skill adapta su salida; no
   cambia la plantilla ni el CV público.
8. **Sin commits.** `output/` y `ofertas/` son locales; no se versionan.
9. **Castellano** para CV, carta, registros e informe.
10. **Ritmo pausado** entre formularios: el objetivo es pasar desapercibido, no
    ganar una carrera.

## Estructura de archivos

```
trabajo/
├── sources/
│   ├── curriculum-base.md          # plantilla del CV
│   ├── criterios-busqueda.md       # banda y geografía permanentes
│   └── datos-candidatura.md        # respuestas de formularios
├── SENSIBLE/                       # ignorado por git
│   ├── playwright-profile/         # sesión del navegador
│   └── tmp/                        # HTML temporal y perfil de LibreOffice
├── ofertas/
│   ├── YYYYMMDD/
│   │   ├── lista-HHMM.md           # job-search
│   │   ├── empresas-HHMM.md        # company-jobs
│   │   ├── postulacion-HHMM.md     # informe de esta skill
│   │   └── postulacion-HHMM.log    # salida del lanzador
│   └── envios.json                 # índice de envíos, ignorado por git
├── output/
│   └── YYYYMMDD-nombreempresa/
│       ├── info.md
│       ├── curriculum-EMPRESA.md / .pdf
│       ├── carta-EMPRESA.md / .pdf
│       └── envio-EMPRESA.md
└── .opencode/skills/auto-apply/
    ├── SKILL.md
    └── scripts/
        ├── generar_adjuntos.py
        ├── registrar_envio.py
        └── postular-diario.sh
```
