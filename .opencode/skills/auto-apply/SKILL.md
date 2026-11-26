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

> **OBJETIVO_ENVÍOS = 15**
>
> **UMBRAL_ENCAJE = 55**
>
> **PISOS_ENCAJE = 55, 45, 35, 25**
>
> Cambia estos tres valores aquí. El resto de la skill habla de «el objetivo de
> envíos», «el umbral de encaje» y «los pisos de encaje»: no los repite.
>
> **No hay tope diario.** La prioridad es enviar **al menos 15 candidaturas por
> ejecución**, empezando por las mejores y bajando el listón por pasadas si
> faltan ofertas. Si aun así no llegan a 15, se amplía la búsqueda a puestos de
> informática afines, **incluidos los de técnico**, hasta completar el objetivo
> o agotar las fuentes. Solo entonces se deja constancia del faltante. Nunca se
> inventan ofertas ni se inventan datos para pasar los filtros del formulario.
>
> El 2026-11-25 se eliminaron los topes anteriores (4 y, transitoriamente, 10)
> por decisión explícita del usuario. La deduplicación sigue activa: una misma
> oferta no se envía dos veces.
>
> El 2026-11-25, también por decisión del usuario, **los filtros del formulario
> dejaron de ser eliminatorios**: años de experiencia, salario, permiso de
> trabajo, ubicación, seniority, disponibilidad y nivel de inglés se anotan como
> desajuste y la candidatura se envía igual con los datos reales. Una pregunta
> obligatoria sin valor en `sources/datos-candidatura.md` se deja en blanco o con
> la opción neutra, **salvo si es numérica** (años de experiencia con una
> tecnología): se responde `0` —decisión explícita del usuario de 2026-11-25
> para que un campo vacío no bloquee el envío— y, en un desplegable, se elige
> «0 años» o equivalente. `0` declara ausencia de experiencia en esa tecnología:
> no es un dato inventado. Nunca se inventa un dato para pasar el filtro. El
> desajuste y la respuesta `0` se registran solo en `envio-EMPRESA.md`.
>
> Las cuentas de usuario **no tienen tope**: se deduplican por dominio y viven en
> `SENSIBLE/cuentas.json`, gestionadas por la skill `account-signup`.

## Principio de diseño

Los scripts resuelven **lo determinista** (convertir archivos, deduplicar,
contar envíos, escribir el índice). El agente resuelve **lo cualitativo**: si la
oferta merece el envío, si el formulario es compatible, qué significa cada
pregunta y si hay duda. La puntuación de `ofertas.py` ordena; no decide.

Esta skill trabaja **sin supervisión**: no hace preguntas al usuario. Ante
cualquier duda —empresa homónima, puesto repetido, pregunta sin respuesta— se
omite la oferta y se registra el motivo, **salvo en las preguntas numéricas sin
valor**, que tienen regla permanente (`0`) y no detienen el envío. El objetivo
de 15 envíos es una prioridad, no una licencia para enviar a ciegas: es
preferible enviar menos candidaturas que enviar una equivocada.

## Cuándo usar esta skill

- Rutina diaria lanzada por `postular-diario.sh` desde crontab.
- Cuando el usuario pida «postúlame hoy» o «envía las mejores ofertas».
- No se usa para buscar ofertas: para eso existe `job-search`.

## Herramientas

| Herramienta | Uso |
| --- | --- |
| `bash` | ejecutar los scripts y las skills locales |
| skill `account-signup` | crear, reutilizar y verificar cuentas cuando el portal lo exige |
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
| `ofertas/YYYYMMDD/lista-HHMM.md` | salida de `job-search` (lista corta y reserva ≥ 25) |
| `ofertas/YYYYMMDD/lista-ampliada-HHMM.md` | salida del modo ampliado de `job-search` |
| `ofertas/YYYYMMDD/empresas-HHMM.md` | salida de `company-jobs` |
| `ofertas/envios.json` | índice de deduplicación (sin tope diario) |
| `output/YYYYMMDD-nombreempresa/` | candidatura y registro de envío |
| `ofertas/YYYYMMDD/postulacion-HHMM.md` | informe del lote |
| `.opencode/skills/auto-apply/scripts/notificar_telegram.py` | helper que avisa por Telegram de ofertas enviadas, cuentas y del lote diario |
| `SENSIBLE/telegram-postulacion.env` | chat ID de destino de los avisos, ignorado por git |
| `SENSIBLE/credenciales.env` | credenciales de `account-signup`, ignorado por git |
| `SENSIBLE/cuentas.json` | índice de cuentas por dominio, sin contraseñas |
| `.opencode/skills/account-signup/` | skill invocada cuando el portal exige cuenta |

## Comandos

```bash
A=.opencode/skills/auto-apply/scripts
C=.opencode/skills/cv-generator/scripts
R=.opencode/skills/company-research/scripts/empresas.py
S=.opencode/skills/job-search/scripts/ofertas.py

# 1. Envíos de hoy (solo informativo: no limita el lote)
python3 $A/registrar_envio.py contar

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
  --estado enviada --directorio output/YYYYMMDD-nombreempresa

# 6. Avisar por Telegram de la oferta enviada (best-effort)
python3 $A/notificar_telegram.py oferta \
  --empresa "EMPRESA" --puesto "PUESTO" --canal "LinkedIn Easy Apply" \
  --url "URL" --fecha "YYYY-MM-DDTHH:MM:SS+01:00" \
  --directorio output/YYYYMMDD-nombreempresa

# 7. Cuando el portal exige cuenta: account-signup
CU=.opencode/skills/account-signup/scripts/cuentas.py
T=.opencode/skills/auto-apply/scripts/notificar_telegram.py
python3 $CU buscar --dominio "empresa.com"
python3 $CU verificar-credenciales
python3 $CU registrar --empresa "EMPRESA" --dominio "empresa.com" \
  --url "URL" --estado creada --notas "registro completado"

# 8. Avisar de la cuenta al crearla y, más tarde, al verificarla
python3 $T cuenta --empresa "EMPRESA" --dominio "empresa.com" \
  --estado creada --fecha "YYYY-MM-DDTHH:MM:SS+01:00"
python3 $T cuenta --empresa "EMPRESA" --dominio "empresa.com" \
  --estado verificada --fecha "YYYY-MM-DDTHH:MM:SS+01:00"

# 9. Avisos de inicio y fin del lote: los envía postular-diario.sh por su cuenta.
python3 $T lote --estado inicio --fecha "YYYY-MM-DDTHH:MM:SS+01:00" \
  --modo normal --log ofertas/YYYYMMDD/postulacion-HHMM.log --sonda
python3 $T lote --estado fin --fecha "YYYY-MM-DDTHH:MM:SS+01:00" \
  --modo normal --duracion 2530 --enviadas 15 \
  --log ofertas/YYYYMMDD/postulacion-HHMM.log --sonda
```

`registrar` devuelve JSON con `registrado` y `duplicado`. Un `url` repetido no
crea una entrada nueva: actualiza la existente. No hay estado `tope_diario`:
el lote solo termina cuando se agota la cola o se alcanza el objetivo sin que
queden fuentes por explorar.

`notificar_telegram.py` imprime JSON con `ok: true` o `ok: false` y **siempre
termina con código 0**: si falla, se anota en el informe y el lote continúa.
Añade `--sonda` para ver el mensaje sin enviarlo. El token se lee del entorno o
de `/home/elarreglador/D-Lab/info_sensible/telegram.env` (opción `--env`). El
destino se resuelve en este orden: variable `TELEGRAM_CHAT_ID`, fichero ignorado
`SENSIBLE/telegram-postulacion.env` (opción `--destino-env`) y, como último
recurso, el chat de D-Lab. El `.env` de D-Lab no se toca: las alertas del clúster
siguen en su conversación.

### Avisos de inicio y fin del lote

`postular-diario.sh` envía dos avisos de lote con el mismo helper (subcomando
`lote`), antes de lanzar `opencode run` y después de que termine:

- **Inicio:** fecha y hora, modo y ruta del log.
- **Fin:** fecha y hora, modo, duración, envíos registrados hoy
  (`registrar_envio.py contar`) y ruta del log. Si el lanzador terminó con un
  código distinto de 0, se añade `Resultado: error (código N)`.

Ambos son best-effort: un fallo de Telegram se escribe como JSON en el log y no
detiene la ejecución. En `--dry-run` **sí se envían**, con la línea
`Modo: --dry-run (modo seco, sin envíos reales)`: sirven para confirmar que cron
disparó y que el lote terminó, sin producir candidaturas. La prohibición de
avisar en modo seco sigue aplicando **solo** a las ofertas enviadas y a las
cuentas.

## Flujo de interacción

### Paso 0 — Preparar la ejecución

1. Detecta si la orden contiene `--dry-run`. En modo seco se recorre todo el
   flujo **menos** el clic final de envío. El modo seco se propaga a
   `account-signup`: no crea cuentas, no abre el correo y no avisa.
2. Lee los tres valores de la sección Configuración y `sources/datos-candidatura.md`.
3. Consulta `registrar_envio.py contar` solo para dejar constancia de los envíos
   de hoy: es informativo, **no limita el lote** (no hay tope diario).
4. No pidas confirmaciones: esta skill nunca interactúa con el usuario.

### Paso 1 — Obtener las ofertas

1. Ejecuta `job-search` con sus criterios habituales (cuatro pasadas: Valencia,
   Barcelona, Madrid y remoto), **incluida la reserva con encaje ≥ 25** de su
   Paso 2. Su Paso 2b delega en `company-jobs`; asegúrate de que se ejecuta para
   incorporar las ofertas de `ofertas/empresas.json`.
2. Sus reglas de «mostrar la lista antes de escribir» y de «confirmar empresa»
   quedan **suspendidas** aquí: el informe es la entrada de datos, no una
   pantalla de aprobación.
3. Lee `ofertas/YYYYMMDD/lista-HHMM.md` y `ofertas/YYYYMMDD/empresas-HHMM.md`.
   Si no hay ningún informe de hoy o ambos están vacíos, escribe el informe de
   postulación con «sin ofertas disponibles» y termina.
4. Si tras el Paso 2 faltan ofertas para el objetivo, vuelve a invocar
   `job-search` en su **modo ampliado** (Paso 2c): términos de informática afines,
   incluidos puestos de técnico, con encaje ≥ 25. Incorpora cada informe
   `lista-ampliada-HHMM.md` a la cola y repite con el siguiente grupo de términos
   hasta llegar a 15 o agotar los grupos previstos. Registra cada ronda en el
   informe de postulación.

### Paso 2 — Preseleccionar por encaje escalonado

1. Reúne la lista corta, la reserva y los informes ampliados. Ordena las ofertas
   por `Encaje` de mayor a menor y, dentro del mismo encaje, por `Posibilidades`
   de mayor a menor (`No consta` al final). Así se empieza por las más adecuadas
   a las capacidades del candidato.
2. Descarta las ya registradas en `ofertas/envios.json` (por `url`, o por
   empresa + puesto si no hay URL) y las que `revisar_output.py` detecte como
   candidatura previa al mismo puesto. Anota cada omisión para el informe.
3. Aplica los pisos de encaje **por pasadas sucesivas**, sin reordenar lo ya
   elegido: `≥ 55` (umbral), luego `≥ 45` si faltan ofertas, luego `≥ 35` y, por
   último, `≥ 25`. Cada pasada añade ofertas al final de la cola.
4. Si tras el último piso faltan ofertas para llegar a 15, pasa al punto 4 del
   Paso 1 (búsqueda ampliada) y vuelve a aplicar este paso sobre lo nuevo.
5. Compón una **cola** con las resultantes, no solo las primeras: las ofertas
   que se bloqueen o den error se sustituyen por la siguiente. Un desajuste de
   filtro no sustituye a nadie: se anota y se envía igual.
6. No presentes dos candidaturas al mismo puesto de empresa(s) relacionadas
   detectadas en la deduplicación de `job-search`.

### Paso 3 — Abrir la oferta y detectar el canal

1. Navega a la URL con `browser_navigate` y toma un `browser_snapshot`.
2. Clasifica el canal: `LinkedIn Easy Apply` o `web de la empresa`.
3. Si la URL no abre, no hay formulario o hace falta un navegador distinto,
   registra `error` con el motivo y pasa a la siguiente de la cola.
4. Si el acceso exige iniciar sesión o crear cuenta, invoca `account-signup`
   (que antes comprueba el índice por dominio). Con cuenta `verificada` o
   `creada`, continúa al Paso 4; con `pendiente-verificacion`, registra
   `bloqueada` con ese motivo y pasa a la siguiente de la cola. Con
   credenciales ausentes, 2FA, CAPTCHA o dato obligatorio sin valor, registra
   el estado correspondiente y sigue: **un muro de registro ya no detiene el
   lote**.

### Paso 4 — Detectar desajustes de filtros (no excluyentes)

Este paso se ejecuta **después** de que `account-signup` haya dejado la sesión
autenticada, si el portal exigía cuenta. **Ningún filtro del formulario descarta
la oferta**: solo se anota lo que no encaja y se sigue con el envío.

1. Lee con `browser_snapshot` / `browser_find` los campos obligatorios y sus
   opciones. Busca especialmente años de experiencia, salario, permiso de
   trabajo, ubicación, seniority, disponibilidad y nivel de inglés.
2. Compara cada condición con `sources/datos-candidatura.md`.
   - Si el formulario exige más de lo declarado (más años de experiencia, un
     nivel de inglés superior, otro rango salarial, otra ubicación...), **no
     descartes**: guarda la pregunta literal, lo que exige y la respuesta real
     que se va a entregar para anotarlo en `envio-EMPRESA.md`.
   - Si una pregunta **obligatoria** no tiene valor en el fichero de datos, se
     deja en blanco o se elige la opción neutra («Prefiero no decirlo») si
     existe. Guarda la pregunta literal para anotarla igualmente en
     `envio-EMPRESA.md`. Nunca rellenes el dato con una estimación.
   - **Excepción numérica:** si la pregunta obligatoria sin valor pide años de
     experiencia con una tecnología —por ejemplo «¿Cuántos años de experiencia
     profesional tienes gestionando infraestructuras en AWS y GCP?»— responde
     **`0`** (en un desplegable, «0 años» o «Menos de 1 año»). La regla está en
     `sources/datos-candidatura.md` y es decisión del usuario (2026-11-25): `0`
     declara que no se tiene experiencia profesional en esa tecnología, no es
     una estimación ni un dato inventado, y evita que un campo vacío impida
     enviar. Anota la pregunta, la respuesta y su origen en `envio-EMPRESA.md`.
     **No abandones la candidatura por este motivo.**
   - Si es opcional y no tiene valor, se deja en blanco o se elige la opción
     neutra del formulario, si la hay.
3. No rellenas ni envías nada de esta oferta hasta que pase este paso. Si el
   portal rechaza el formulario por un campo obligatorio sin valor, registra
   `error` o `bloqueada` con el mensaje literal: se intentó enviar sin inventar
   el dato, no se cambió la respuesta para forzar el pase. Las preguntas
   numéricas sin dato ya se han respondido con `0` según la regla anterior y
   no deberían llegar aquí.

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
   texto libre de motivación, del CV adaptado y de la oferta. Las preguntas
   numéricas sin valor se rellenan con `0` según la regla de ese fichero; guarda
   en memoria la tripleta **pregunta → respuesta → origen** para el registro
   (el origen de esos `0` es la regla de 2026-11-25, no «—»).
3. Marca la casilla «Seguir a [empresa]» cuando aparezca: es la preferencia
   permanente del usuario. No marques otras casillas de marketing ni
   comunicaciones comerciales.
4. Si aparece CAPTCHA o verificación en dos pasos: no lo eludas. Registra
   `bloqueada`, cierra limpiamente y pasa a la siguiente.
5. Si un error del portal impide continuar, registra `bloqueada` con el mensaje
   visto en pantalla y pasa a la siguiente.

### Paso 8 — Enviar y confirmar

1. Antes de pulsar el botón final, revisa el `browser_snapshot`: las respuestas
   siguen saliendo del fichero de datos (o están en blanco/neutras cuando no hay
   valor, y son `0` en las preguntas numéricas sin valor) y los archivos están
   adjuntos. Los desajustes detectados en el Paso 4 no se han usado para cambiar
   ninguna respuesta; el `0` de las numéricas es la única excepción prevista.
2. **Si es modo seco:** detente aquí. Fija el estado `bloqueada` con motivo
   «Ejecución en modo seco: no se pulsó enviar» y pasa a la siguiente. No se
   envía ningún aviso de candidatura a Telegram; los avisos de inicio y fin del
   lote los gestiona el lanzador y van marcados como modo seco.
3. Si no es modo seco, pulsa «Enviar» una sola vez y espera la pantalla de
   confirmación. Sin confirmación visible, registra `error`.
4. Con confirmación, fija el estado `enviada` y anota la fecha y hora reales.

### Paso 9 — Registrar

1. Rellena `envio-EMPRESA.md` con todos los campos, incluidas las tripletas
   pregunta → respuesta → origen recogidas en el Paso 7, el campo **Cuenta**
   devuelto por `account-signup` y el apartado «Filtros y preguntas sin dato»
   del Paso 4 con cada desajuste y cada pregunta sin valor. Si el estado no es
   `enviada`, el **motivo** es obligatorio.
2. Llama a `registrar_envio.py registrar` con el estado final (sin tope diario).
   Un `url` ya registrado actualiza la entrada; no envíes dos veces la misma
   oferta.
3. Si el estado final es `enviada`, llama a `notificar_telegram.py oferta` con
   los mismos datos del registro y su fecha real. Si devuelve `ok: false`,
   anota `telegram: error` en el informe y continúa. En `--dry-run` no se llama.
4. Repite desde el Paso 3 con la siguiente oferta de la cola **hasta agotarla**,
   incluidas las rondas ampliadas del Paso 1. Llegar a 15 no detiene el lote si
   aún quedan ofertas viables: el objetivo es un mínimo, no un tope.

### Paso 10 — Escribir el informe diario

`YYYYMMDD` es la fecha de hoy; `HHMM` permite varias ejecuciones el mismo día.

```markdown
# Postulación automática — YYYY-MM-DD

> Búsqueda interna. No se envía a ninguna empresa.

## Cabecera

- **Modo:** normal | --dry-run
- **Fecha y hora:** YYYY-MM-DDTHH:MM:SS+01:00
- **Fuentes:** informes de job-search y company-jobs de hoy, incluidas las rondas ampliadas
- **Objetivo de envíos:** [valor de la configuración] (mínimo, sin tope)
- **Umbral de encaje:** [valor de la configuración]
- **Pisos aplicados:** [55 | 45 | 35 | 25 — último piso alcanzado]
- **Rondas ampliadas:** [términos de cada ronda y ofertas aportadas, o «Ninguna»]
- **Orden:** Encaje descendente; dentro del mismo encaje, Posibilidades descendente

## Seleccionadas

| # | Empresa | Puesto | Canal | Encaje | Posibilidades | Estado | Registro |
| --- | --- | --- | --- | --- | --- | --- | --- |

## Enviadas

- [empresa, puesto, hora y directorio, o «Ninguna»]

## Cuentas

| Empresa | Dominio | Estado | Momento del aviso |
| --- | --- | --- | --- |
| [o «Ninguna»] | | | |

## Avisos Telegram con error

- [empresa, puesto y motivo devuelto por el helper, o «Ninguno»]

## Bloqueadas y con error

| Empresa | Puesto | Estado | Motivo |
| --- | --- | --- | --- |

## Omisiones por duplicado

| Empresa | Puesto | Motivo |
| --- | --- | --- |

## Fuentes

| Dato | Fuente | Fecha |
| --- | --- | --- |
```

Reglas del informe: si no hay ofertas, indícalo en «Seleccionadas» y deja el
resto de secciones con «Ninguna». Si se envían menos de 15, añade una línea
**Faltaron para el objetivo:** N, con el último piso y las rondas ampliadas
agotadas. No escribas datos que no estén en los informes de entrada ni en los
registros de `output/`. Nunca escribas credenciales en el informe:
`SENSIBLE/credenciales.env` no se copia aquí.

## Registro de envío

Plantilla de `output/YYYYMMDD-nombreempresa/envio-EMPRESA.md`:

```markdown
# Envío de candidatura — EMPRESA

> Registro interno. No se envía a la empresa.

- **Fecha y hora:** YYYY-MM-DDTHH:MM:SS+01:00
- **Oferta:** [URL de la oferta original]
- **Puesto:** [nombre del puesto]
- **Canal:** LinkedIn Easy Apply | web de la empresa
- **Cuenta:** no requerida | reutilizada | creada | pendiente-verificacion
- **Estado:** enviada | bloqueada | error (`descartada-por-filtro` y `sin-responder`: solo registros históricos)
- **Adjuntos entregados:** curriculum-EMPRESA.pdf, carta-EMPRESA.pdf | solo CV | ninguno
- **Motivo del estado:** [obligatorio si el estado no es «enviada»; una frase]

## Información solicitada y entregada

| Pregunta del formulario | Respuesta entregada | Origen de la respuesta |
| --- | --- | --- |

## Filtros y preguntas sin dato (no excluyentes)

| Tipo | Pregunta del formulario | Lo que exige o falta | Respuesta entregada | Origen |
| --- | --- | --- | --- | --- |
| Desajuste de filtro | [pregunta literal] | [condición exigida] | [dato real] | sources/datos-candidatura.md |
| Sin dato | [pregunta literal] | [obligatoria, sin valor en el fichero] | [en blanco / opción neutra] | — |
| Sin dato (numérica) | «¿Cuántos años de experiencia profesional tienes gestionando infraestructuras en AWS y GCP?» | obligatoria, sin valor en el fichero | 0 | sources/datos-candidatura.md (regla 2026-11-25) |

> Si no hay desajustes ni preguntas sin dato, escribe «Ninguno». Este apartado
> sustituye a los antiguos estados `descartada-por-filtro` y `sin-responder`: la
> candidatura se envía igual. Un `0` entregado por la regla numérica se anota aquí
> como «Sin dato (numérica)» y también en «Información solicitada y entregada»;
> no se trata como dato inventado.

## Archivos generados

- `curriculum-EMPRESA.md` → `curriculum-EMPRESA.pdf`
- `carta-EMPRESA.md` → `carta-EMPRESA.pdf`
- `info.md` (interno, no enviado)

## Incidencias

- [Ninguna, o descripción del bloqueo sin intentar eludirlo]
```

Estados admitidos: `enviada`, `descartada-por-filtro`, `bloqueada`,
`sin-responder`, `error`. Los dos estados de filtro (`descartada-por-filtro` y
`sin-responder`) son **legacy**: siguen admitidos en `ofertas/envios.json` para
registros históricos, pero esta skill ya no los produce.

## Modo seco

La orden `opencode run --auto ... "Ejecuta la skill auto-apply en modo --dry-run"`
o `postular-diario.sh --dry-run` recorre las ofertas, genera CV, carta, adjuntos,
registros e informe, pero **no pulsa «Enviar»**. Ningún registro queda con estado
`enviada`. Los avisos de inicio y fin del lote sí se envían, marcados como
`--dry-run`. Es la única forma de probar el flujo contra ofertas reales.

## Crontab

El lanzador está en `scripts/postular-diario.sh`. La línea que el usuario debe
añadir a su crontab (la skill **no la instala**) es:

```cron
0 9 * * * /home/elarreglador/Documentos/trabajo/.opencode/skills/auto-apply/scripts/postular-diario.sh
```

Cada ejecución escribe `ofertas/YYYYMMDD/postulacion-HHMM.log` y avisa por
Telegram al inicio y al final (sección «Avisos de inicio y fin del lote»).

## Reglas importantes

1. **Sin preguntas.** Modo autónomo: duda de identidad (empresa homónima, puesto
   repetido) → omisión con registro. Un desajuste de filtro ya no es una duda:
   se anota y se envía.
2. **Sin datos inventados.** Toda respuesta sale de `sources/datos-candidatura.md`;
   una obligatoria sin valor se deja en blanco o con la opción neutra y se envía
   igual. **Salvo en las numéricas:** un «¿cuántos años de experiencia con X?»
   sin valor se responde `0` por decisión del usuario (2026-11-25), se anota como
   «Sin dato (numérica)» y se envía igual. `0` declara ausencia de experiencia en
   esa tecnología: no es un dato inventado ni una estimación. Nunca se inventa un
   dato para pasar un filtro.
3. **Sin tope diario, con pisos.** El objetivo es al menos 15 envíos; se baja
   por pasadas a 45, 35 y 25, y se amplían los términos a informática y puestos
   de técnico si aún faltan ofertas. No se envía por debajo del último piso; los
   filtros del formulario se registran como desajuste, nunca se eluden.
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
11. **Aviso por oferta enviada y por lote.** El token se lee en tiempo de
    ejecución del entorno o del fichero de D-Lab; el destino sale de
    `SENSIBLE/telegram-postulacion.env` (o del entorno). Nada de eso se copia al
    repo, a `output/` ni al informe. Un fallo de Telegram se anota y no detiene
    el lote. El lanzador avisa del inicio y del fin; en modo seco los avisos de
    lote van marcados como tal.
12. **Cuentas sin detener el lote.** Si el portal exige registro o login, invoca
    `account-signup`: un muro de registro ya no detiene el lote. Las credenciales
    viven solo en `SENSIBLE/credenciales.env`; 2FA y CAPTCHA se registran, no se
    eluden. Los avisos de cuenta se envían al crear y al verificar.
13. **Filtros blandos.** Ningún filtro del formulario descarta la oferta:
    experiencia, salario, permiso de trabajo, ubicación, seniority,
    disponibilidad y nivel de inglés se anotan como desajuste solo en
    `envio-EMPRESA.md` y el CV se envía con los datos reales.

## Estructura de archivos

```
trabajo/
├── sources/
│   ├── curriculum-base.md          # plantilla del CV
│   ├── criterios-busqueda.md       # banda y geografía permanentes
│   └── datos-candidatura.md        # respuestas de formularios
├── SENSIBLE/                       # ignorado por git
│   ├── playwright-profile/         # sesión del navegador
│   ├── telegram-postulacion.env    # chat ID de los avisos
│   ├── credenciales.env            # credenciales de account-signup
│   ├── cuentas.json                # índice de cuentas por dominio
│   └── tmp/                        # HTML temporal y perfil de LibreOffice
├── ofertas/
│   ├── YYYYMMDD/
│   │   ├── lista-HHMM.md           # job-search (corta + reserva)
│   │   ├── lista-ampliada-HHMM.md  # job-search, modo ampliado
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
├── .opencode/skills/account-signup/
│   ├── SKILL.md
│   └── scripts/cuentas.py
└── .opencode/skills/auto-apply/
    ├── SKILL.md
    └── scripts/
        ├── generar_adjuntos.py
        ├── registrar_envio.py
        ├── notificar_telegram.py
        └── postular-diario.sh
```
