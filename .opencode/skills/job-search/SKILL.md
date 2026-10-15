# job-search

Skill de búsqueda de ofertas de empleo. Encuentra ofertas vivas, las puntúa por
encaje con el perfil de `sources/curriculum-base.md` y deja una lista corta
justificada en `ofertas/YYYYMMDD/`. 

## Principio de diseño

El script resuelve **solo lo estructurado y determinista** (recoger, normalizar,
deduplicar, filtrar, puntuar). Todo lo **cualitativo** (si la oferta encaja de
verdad, cuál es el argumento, qué requisitos no se cubren) lo decide el agente
con la descripción completa.

Motivo: un filtro de palabras no sabe que "Desarrollador de Firmware IoT" es un
encaje perfecto y "Senior Cloud Architect" no, aunque ambas contengan `iot` y
`cloud`. La puntuación ordena el ruido; el argumento lo pone quien lo juzga.

## Cuándo usar esta skill

- El usuario quiere saber **qué empresas están contratando** algo que le encaje.
- El usuario quiere buscar ofertas de trabajo
- Para comprobar qué se le está escapando (suelen ser las empresas pequeñas o
  las que no publican en portales grandes).
- **Búsqueda exhaustiva multi-pasada** con hidratación y filtro de consultoras por campo `Sectores` para obtener solo ofertas >70 pts.

## Fuentes

| Fuente | Uso | Límite conocido |
|---|---|---|
| LinkedIn (endpoint público de invitado) | **La principal.** Ofertas de España con título, empresa, fecha y descripción completa | Es un endpoint no oficial aunque público y anónimo; ritmo limitado. `f_WT` (filtro de remoto) **no lo respeta**: el remoto se detecta por el texto de la ubicación |
| Remotive, Himalayas | Complemento de **remoto Europa** | Cobertura de España casi nula: filtrar siempre por `--ubicacion` |
| Remote OK | Agregador remoto global, sin auth | API pública `https://remoteok.com/api`, 1 req/s, caché 6 h |
| We Work Remotely | Tablero remoto premium, requiere API key | Gratis previa solicitud a `hello@weworkremotely.com`, token en `WWR_TOKEN` |
| Adzuna | Agregador multi-país (ES, UK, FR, DE, IT...) | Requiere `ADZUNA_APP_ID` + `ADZUNA_KEY` (gratis en developer.adzuna.com) |
| Jooble | Agregador global, busca por keyword+location | Requiere `JOOBLE_KEY` (gratis en jooble.org) |
| UPV, UV, GVA, CSIC (`publico`) | **Convocatorias de empleo público**: oposiciones, PAS, personal investigador | Ver apartado [Convocatorias](#convocatorias-empleo-público) |
| InfoJobs, Indeed, el propio LinkedIn con sesión | No se usan | Bloquean o exigen login. Si hacen falta, `websearch` |
| Web oficial de una empresa (web de empleo) | Para ofertas concretas que no salen en portales | `webfetch` sobre la URL de la empresa |

## Comandos

```bash
S=.opencode/skills/job-search/scripts/ofertas.py

# búsqueda principal: término + geografía de búsqueda
python3 $S buscar "IoT" --geo "Valencia, Spain" --dias 21 --paginas 2 --minimo 30 \
  --clave "iot,zigbee,embedded,firmware,kubernetes,python,linux" \
  --ubicacion "valencia,valencian" --formato json

# todas las de España, banda mid/senior
python3 $S buscar "backend developer" --geo "Spain" --seniority "mid,senior" --dias 14

# remoto Europa (obligatorio filtrar por geografía aquí)
python3 $S remoto "backend python kubernetes" --dias 45 \
  --ubicacion "spain,worldwide,europe,emea,united kingdom,netherland"

# nuevas fuentes remotas (sin --geo, son inherentemente remotas)
python3 $S buscar "python kubernetes" --fuente remoteok --dias 30 --minimo 20
python3 $S buscar "python kubernetes" --fuente weworkremotely --dias 30 --minimo 20

# Adzuna (requiere ADZUNA_APP_ID + ADZUNA_KEY en .env, --geo = código país ISO)
python3 $S buscar "backend python" --fuente adzuna --geo es --dias 14 --minimo 20

# Jooble (requiere JOOBLE_KEY en .env, --geo = código país ISO)
python3 $S buscar "backend python" --fuente jooble --geo es --dias 14 --minimo 20

# convocatorias de empleo público (sin --geo ni --seniority)
python3 $S publico --clave "informatica,sistemas,desarrollo" --dias 14 --formato json
python3 $S publico --fuentes gva,csic --clave "administracion,gestion"

# descripción completa de una oferta concreta
python3 $S detalle 4441123182
python3 $S detalle "https://es.linkedin.com/jobs/view/...-4441123182" --formato json

# BÚSQUEDA EXHAUSTIVA MULTI-PASADA (nuevo)
# Ejecuta las 4 pasadas, hidrata descripciones, filtra consultoras por campo Sectores,
# y devuelve SOLO ofertas con puntuación >= 70 (sin cambiar el algoritmo de puntuación)
python3 $S buscar-todo "backend iot embedded firmware kubernetes python" \
  --dias 21 --paginas 2 --minimo 70 \
  --clave "backend,iot,embedded,firmware,kubernetes,python,java,nodejs,zigbee,mqtt,esp32,linux,docker,git,mysql,rest,api,cloud,aws,azure,gcp" \
  --descartar "sap,scrum master,unity,.net,comercial,teleoperador,telemarketing,lemon.io,ateam" \
  --ubicacion "valencia,valencian,madrid,barcelona,sevilla,vigo,spain,españa,worldwide,europe,emea,united kingdom,netherlands,germany,france,ireland" \
  --seniority "mid,senior,lead" \
  --formato json
```

Opciones que importan:

| Opción | Para qué |
|---|---|
| `--geo` | **Dónde se busca** (texto que entiende LinkedIn: `Valencia, Spain`) |
| `--ubicacion` | **Dónde se puntúa** (tokens; sin acentos: `valencia,valencian`). Con `remoto` es además filtro duro |
| `--clave` | Palabras del perfil que suman. Se casan **por palabra completa**: `go` no casa dentro de `algorithm` |
| `--descartar` | Palabras o empresas que restan 20. Penalizan, **no descartan** |
| `--seniority` | Banda admitida: `junior,mid,senior,lead`. Fuera de banda: −15 |
| `--fuentes` | (`publico`) Fuentes a consultar, separadas por comas. Por defecto, todas: `upv,uv,gva,csic` |
| `--dias` | Antigüedad máxima en días (por defecto 14). En `publico` además define la ventana de días de la GVA |
| `--detalle` | (`publico`) Convocatorias **por fuente** a hidratar con su ficha (por defecto 15; `0` para no hidratar) |
| `--minimo` | Descarta por debajo de esa puntuación (por defecto 1) |
| `--permitir-sin-clave` | Desactiva el descarte de ofertas sin ni una palabra del perfil |
| `--detalle N` | Cuántas ofertas hidratar con su descripción (por defecto 10). `0` para no hidratar |
| `--sin-cache` | Ignora la caché (TTL 6 h) |
| `WWR_TOKEN` | (env) Token de We Work Remotely (solicitar a hello@weworkremotely.com) |
| `ADZUNA_APP_ID` + `ADZUNA_KEY` | (env) Credenciales de Adzuna (gratis en developer.adzuna.com) |
| `JOOBLE_KEY` | (env) API key de Jooble (gratis en jooble.org) |

## Puntuación

| Señal | Puntos |
|---|---|
| Base: oferta vigente y no es una empresa de selección | +25 |
| Palabra clave en el título (máx. 3) | +12 c/u |
| Palabra clave en la descripción (máx. 2) | +6 c/u |
| Ubicación en el objetivo | +15 |
| Remota, si `--remoto` | +10 |
| Publicada esta semana / hace dos semanas | +10 / +5 |
| Idioma distinto de los admitidos | −25 |
| Nivel fuera de la banda | −15 |
| Perfil comercial o de telemarketing | −25 |
| Palabra o empresa de `--descartar` | −20 (máx. 2) |

**Tope por evidencia débil:** si ninguna palabra clave aparece en el **título**,
la puntuación se queda en 45 aunque la descripción case. Motivo: cualquier
boletín de IT contiene `api`, `rest` o `network`, así que una coincidencia en la
descripción no distingue un puesto de otro. El título es la señal; la descripción solo la confirma.

**Descartes duros** (no salen nunca en la lista): más de `--dias` días,
empresa de selección, perfil comercial, y ninguna palabra clave del perfil en
título ni descripción.

La puntuación ordena; **no decide**. Un 81 y un 45 pueden ser ambos
interesantes, y uno puede ser irrelevante.

## Búsqueda exhaustiva multi-pasada (`buscar-todo`)

### Objetivo
Obtener **solo ofertas con puntuación ≥ 70** sin modificar el algoritmo de puntuación,
combinando 4 pasadas complementarias, hidratación masiva de descripciones y filtro
definitivo de consultoras por el campo `Sectores` de la oferta hidratada.

### Por qué 4 pasadas
Cada fuente/pasada encuentra ofertas que las otras no ven:
1. **Local** (`--geo "Valencia, Spain"`): ofertas presenciales/hibridas en tu zona.
2. **Nacional** (`--geo "Spain"`): ofertas en Madrid, Barcelona, Sevilla, Vigo, etc.
3. **Remoto Europa** (`remoto`): Remotive + Himalayas + Remote OK + We Work Remotely, filtrado por `--ubicacion`.
4. **Agregadores globales** (`--fuente adzuna|jooble --geo es`): cobertura multi-país de España.

### Flujo automatizado de `buscar-todo`

1. **Deriva criterios** del CV (Paso 1) y construye las 4 consultas con los mismos `--clave`, `--descartar`, `--ubicacion`, `--seniority`.
2. **Ejecuta las 4 búsquedas** en serie (LinkedIn local, LinkedIn nacional, remoto, adzuna/jooble si hay credenciales).
3. **Deduplicación global** por ID y por firma `empresa|título` normalizada.
4. **Hidratación masiva**: `--detalle 20` por pasada (máx. 80 ofertas hidratadas) para obtener descripción completa, criterios, sector, seniority real.
5. **Filtro de consultoras por campo `Sectores`**: tras hidratar, descarta cualquier oferta donde `Sectores` contenga "Servicios y consultoría de TI" (o equivalentes), **además** de la heurística por nombre. Este es el filtro definitivo: una oferta hidratada con sector "Desarrollo de software" no es consultora aunque el nombre lo sugiera.
6. **Re-puntuación** con datos completos (descripción, sector real, seniority inferido de la hidratación).
7. **Filtro final `--minimo`** (por defecto 70 en este modo): solo ofertas ≥ umbral salen en el JSON.
8. **Genera `ofertas/YYYYMMDD/lista-HHMM.md`** con la lista corta ya cualificada (Pasos 3-4 del flujo estándar).

### Opciones específicas de `buscar-todo`

| Opción | Defecto | Descripción |
|---|---|---|
| `--minimo` | 70 | Umbral final de puntuación (más alto que en búsquedas simples) |
| `--detalle` | 20 | Ofertas a hidratar **por pasada** (total máx. ~80) |
| `--paginas` | 2 | Páginas por pasada en LinkedIn |
| `--sin-consultoras-sector` | false | Desactiva el filtro por campo `Sectores` (solo heurística por nombre) |

### Ejemplo de uso típico

```bash
python3 $S buscar-todo "backend iot embedded firmware kubernetes python zigbee mqtt esp32" \
  --dias 21 --paginas 2 --minimo 70 \
  --clave "backend,iot,embedded,firmware,kubernetes,python,java,nodejs,zigbee,mqtt,esp32,linux,docker,git,mysql,rest,api,cloud,aws,azure,gcp" \
  --descartar "sap,scrum master,unity,.net,comercial,teleoperador,telemarketing,lemon.io,ateam" \
  --ubicacion "valencia,valencian,madrid,barcelona,sevilla,vigo,spain,españa,worldwide,europe,emea,united kingdom,netherlands,germany,france,ireland" \
  --seniority "mid,senior,lead" \
  --formato json
```

**Salida**: JSON con `ofertas` (solo ≥70), `descartadas` (con motivo), `resumen`, y archivo `ofertas/YYYYMMDD/lista-HHMM.md` listo para revisar.

## Convocatorias (empleo público)

El subcomando `publico` recoge convocatorias de las sedes oficiales. Mismo
criterio de puntuación, con tres salvedades por ser organismos públicos y no
vacantes privadas (bandera `convocatoria` en el JSON):

- **No infiere `seniority` ni `idioma`** (la convocatoria fija el grupo y el
  idioma legal es castellano), así que no hay castigos de −15 ni −25.
- **No aplica el descarte de consultora ni de perfil comercial** (+25 base limpio).
- **Sí se puntúan** `--clave`, `--descartar`, `--ubicacion` (salvo GVA, cuya
  ficha no lleva ciudad) y la antigüedad (`--dias`), si la fuente trae fecha.
- **Las convocatorias sin descripción se hidratan solas** (`--detalle`, por
  defecto 15 por fuente): baja la ficha enlazada y puntúa con su cuerpo. Con
  `--detalle 0` solo se ve el título. Cuesta ~1 petición por segundo por ficha.
- Añade **`informatica`** a `--clave` en esta ruta: es la palabra con la que las
  sedes públicas nombran los puestos de TI (sin ella, UV/CSIC salen a 0).

| Fuente (`--fuentes`) | Qué trae | Particularidades |
|---|---|---|
| `upv` | Convocatorias de acceso libre de la UPV | Sin fecha (no penaliza antigüedad). Trae algún documento auxiliar (p. ej. «Hojas de autobaremación») que `--clave` descarta solo |
| `uv` | Solo **turno libre** del PAS de la UV | Sin fecha. Excluye promoción interna y personal laboral a propósito. El título solo dice grupo y escala: el área está en la ficha, que `--detalle` hidrata |
| `gva` | Novedades de empleo público de la sede GVA (hoy + `--dias` hacia atrás, máx. ~10 días) | Sin ciudad en la ficha. El portal a veces contesta «Aplicación fuera de servicio»: el script lo avisa y no lo cachea |
| `csic` | Convocatorias de acceso del CSIC, con fecha | Paginación de 8 en 8 (`--paginas`, por defecto 2); corta al superar `--dias`. Muchas son tesis y libre designación: la ficha hidratada es lo que permite descartarlas con criterio |

El mismo flujo de los pasos 1-4 aplica: criterios del CV, `--clave` del perfil,
lista corta justificada. Un `recogidas: 0` con `--clave` muy estrecho es
normal; un `0` de una sola fuente con `--fuentes gva` casi siempre es el
portal caído (habrá un `[aviso]` en stderr).

## Flujo de interacción

### Paso 1 — Derivar los criterios del CV

Lee `sources/curriculum-base.md` y decide, cada vez:

- **Roles objetivo** (los 3-5 términos de búsqueda más determinantes)
- **Palabras clave**: sinónimos reales del CV en español **e inglés**
  (del `embedded` al `embebido`, `firmware`, `Zigbee`, `Kubernetes`…). Include
  las palabras que usaría la empresa, no las del CV.
- **Palabras de descarte**: lo que de verdad no es suyo (`SAP`, `scrum master`,
  `Unity`, `.NET` si no lo tiene).
- **Banda de seniority**: qué busca ahora mismo.
- **Geografía**: qué cuenta como destino.

Si el usuario ya ha dicho "buscarme ofertas de X", usa sus criterios y no le
preguntes lo que ya ha dicho.

### Paso 2 — Buscar en varias pasadas

Cuatro búsquedas como mínimo, porque cada una encuentra lo que las otras no:

1. **Local** (`--geo "Valencia, Spain"`): lo que se puede ir sin mudanza.
2. **Nacional** (`--geo "Spain"`): lo que ya se vio en candidaturas anteriores (Pozuelo,
   Sevilla, Vigo).
3. **Remoto Europa** (`remoto`): agrega Remotive + Himalayas + Remote OK + We Work Remotely; solo tiene sentido con `--ubicacion`.
4. **Agregadores globales** (`--fuente adzuna|jooble --geo es`): para cubrir España con fuentes multi-país.

Añade `--paginas 2` y `--detalle 10` en todas. Guarda el JSON de cada una.

### Paso 3 — Cualificar

Para las 5-10 mejores de cada pasada, lee la descripción
(`detalle` ya viene en el JSON; si no, `python3 $S detalle <id>`) y decide:

- **El argumento**: por qué encaja, en una frase que conecte la trayectoria con
  el negocio de la empresa. Reutiliza el eje del CV, no un listado de tecnologías.
- **Qué cubre** del `curriculum-base.md` cada requisito.
- **Qué NO cubre**: los requisitos que no puede cumplir. Esto es lo más útil de
  la lista: decide si salga la candidatura antes de escribir el CV.
- **Antigüedad**: una oferta de 20 días puede tenerla cerrada.

Muestra la lista al usuario **antes** de escribir nada.

### Paso 4 — Escribir `ofertas/YYYYMMDD/lista-HHMM.md`
IMPORTANTE: Este paso no es opcional, el usuario espera este documento.

`YYYYMMDD` es la fecha de hoy; `HHMM` permite varias búsquedas el mismo día.

```markdown
# Ofertas por encaje — YYYY-MM-DD

> Búsqueda interna. No se envía a ninguna empresa.

## Criterios usados

- **Derivados de:** `sources/curriculum-base.md`
- **Términos:** [los mismos de la consulta]
- **Palabras clave:** [la lista completa]
- **Descartes:** [la lista]
- **Banda de seniority:** [...]
- **Geografía:** [qué se buscó]
- **Antigüedad máxima:** N días

## Lista corta

Ordenada de mayor a menor encaje.

| # | Empresa | Puesto | Ubicación | Publicada | Encaje | Enlace |
|---|---|---|---|---|---|---|

## Detalle

### 1. EMPRESA — Puesto

- **Argumento:** [una frase, el eje]
- **Qué cubre:** [requisito → parte del CV]
- **Qué no cubre:** [requisito → por qué]
- **Verificar antes de postular:** [...]
- **Siguiente paso:** `nueva_candidatura.py "EMPRESA"`

## Descartadas

| Empresa | Puesto | Motivo |
|---|---|---|

## Fuentes

| Dato | Fuente | Fecha |
|---|---|---|
| Ofertas | LinkedIn, endpoint público de invitado | YYYY-MM-DD |
```

Reglas del fichero:

- **Los criterios van a la cabecera.** Es lo que hace la búsqueda reproducible:
  sin ellos, un resultado de hoy no se puede reconstruir mañana.
- **Toda cifra viene del JSON** de la búsqueda, con su fecha.
- Si un dato no aparece en ninguna fuente, escribe `No consta`. No estimes
  salario, ni nivel de idiomas, ni el estado de la oferta.
- Marca las ofertas de más de 14 días como probablemente cerradas.


## Estructura de archivos

```
trabajo/
├── sources/
│   └── curriculum-base.md        # de aquí se derivan los criterios
├── ofertas/                     # listas de búsqueda, versionadas
│   └── YYYY-MM-DD/
│       └── lista-HHMM.md
└── .opencode/skills/job-search/
    ├── SKILL.md
    ├── .gitignore               # cache/ y __pycache__/
    └── scripts/
        └── ofertas.py
```

## Reglas importantes

1. **Un argumento, no un listado.** La misma regla del CV: si la justificación
   es una lista de tecnologías, todavía no está escrita.
2. **Lo que no cubres se escribe.** Ocultar un requisito que no cumple es la
   forma más rápida de perder una entrevista.
3. **No rellenes ni envíes candidaturas.** La búsqueda produce material; el
   envío es del usuario y en su navegador.
4. **Comprueba siempre el campo `Sectores` de la oferta hidratada.** Si dice
   «Servicios y consultoría de TI», es una consultora: estás aplicando a una
   intermediaria, no al cliente final. La lista de `CONSULTORAS` es heurística
   y se escapa; ese campo no.
5. **Ritmo y caché.** El script ya limita a 1 petición por segundo y cachea 6 h.
   No llames a la fuente en bucle ni pongas `--sin-cache` salvo depuración.
6. **Enlaza siempre a la oferta original**, no a un agregador intermedio. Es lo
   que piden los términos de Remotive y lo que hace el informe utilizable.
7. **Idioma:** castellano para el informe. Las ofertas en otro idioma se marcan,
   no se traducen.
8. **Sin commits** sin que el usuario lo pida. `ofertas/` sí se versiona: guarda
   qué había disponible cada día.
9. **ofertas/YYYYMMDD/lista-HHMM.md**: El documento en el directorio ofertas debe existir

## Detalles de la fuente que ya están comprobados

No los vuelvas a descubrir a costa de una petición:

- El endpoint **no acepta `f_C`** (código de país): devuelve vacío. Usa `--geo`.
- **`f_WT=2` se ignora**: la misma consulta con y sin él da resultados
  idénticos. El remoto se detecta por el texto de la ubicación, no por filtro.
- **Con `--geo` la página trae 10 ofertas; sin `--geo`, 25.** El script mide la
  primera página y salta el tamaño correcto.
- El detalle trae un `<h2 class="top-card-layout__title">`, **no un `<h1>`**, y
  los requisitos vienen como `description__job-criteria-subheader`.
- El idioma se infiere de la descripción por palabras clave. Si no hay
  descripción (o no se hidrató), el idioma queda como desconocido y **no penaliza**.
- La deduplicación no detecta **la misma oferta bajo dos páginas de empresa**
  (`SEPTEO` y `SEPTEO España y Portugal` son la misma vacante con distinto nombre
  comercial). Al elegir la lista corta, compara por empresa antes de recomendar
  dos candidaturas al mismo puesto.
- La lista `CONSULTORAS` heurística sobre el nombre se escapa. El campo
  `Sectores` de la oferta hidratada es el dato fiable: «Servicios y consultoría de
  TI» delata a una intermediaria aunque el nombre parezca limpio.
- Los agregadores remotos traen mucho *gig* de baja calidad (redactores,
  asistentes, IA genérica) y plataformas de *staffing* sin filtrar (`lemon.io`,
  `A.Team`). Sube `--minimo`, añádelas a `--descartar`, y **espera que la lista
  remota salga vacía**: es un resultado legítimo, no un fallo.
- **Remote OK**: devuelve array JSON donde el primer elemento es metadatos; las ofertas empiezan en índice 1. Incluye `tags` (tecnologías) útiles para filtrado previo.
- **We Work Remotely**: requiere token Bearer; la respuesta agrupa por categoría (`jobs.{categoria}[]`). El campo `region` indica geografía (ej. `Worldwide`, `Europe`, `Spain`).
- **Adzuna**: usa código de país ISO en la URL (`/es/`, `/gb/`, `/fr/`). El campo `redirect_url` lleva a la oferta original; `contract_type` indica `permanent`, `contract`, etc.
- **Jooble**: endpoint POST con JSON `{"keywords": "...", "location": "..."}`. Devuelve `jobs[]` con `link` a la oferta original. El campo `type` indica `full-time`, `part-time`, `remote`.