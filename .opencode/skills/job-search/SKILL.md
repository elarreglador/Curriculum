---
name: job-search
description: Busca ofertas de empleo adecuadas al CV del usuario (David Moreno Bolívar). Filtra por seniority, geografía y palabras clave del perfil, puntúa el encaje y genera un informe en ofertas/YYYYMMDD/lista-HHMM.md. Úsala cuando el usuario pida buscar ofertas de trabajo.
---

# job-search

Skill de búsqueda de ofertas de empleo. Encuentra ofertas vivas, las puntúa por
encaje con el perfil de `sources/curriculum-base.md` —banda y geografía según
`sources/criterios-busqueda.md`— y deja una lista corta justificada en
`ofertas/YYYYMMDD/`. 

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

## Fuentes

| Fuente | Uso | Límite conocido |
|---|---|---|
| LinkedIn (endpoint público de invitado) | **La principal.** Ofertas de España con título, empresa, fecha y descripción completa | Es un endpoint no oficial aunque público y anónimo; ritmo limitado. `f_WT` (filtro de remoto) **no lo respeta**: el remoto se detecta por el texto de la ubicación |
| Remotive, Himalayas | Complemento de **remoto Europa** | Cobertura de España casi nula: filtrar siempre por `--ubicacion` |
| InfoJobs, Indeed, el propio LinkedIn con sesión | No se usan | Bloquean o exigen login. Si hacen falta, `websearch` |
| Web oficial de una empresa (web de empleo) | Para ofertas concretas que no salen en portales | `webfetch` sobre la URL de la empresa |
| Web de empleo de empresas registradas (`ofertas/empresas.json`) | **Empresas conocidas** (pequeñas o que no publican en portales grandes) | `webfetch` sobre `url_empleo` de cada registro; se anota la revisión en `empresas.json` |

## Comandos

```bash
S=.opencode/skills/job-search/scripts/ofertas.py

# búsqueda principal: término + geografía de búsqueda
python3 $S buscar "IoT" --geo "Valencia, Spain" --dias 14 --paginas 1 --minimo 55 \
  --seniority "junior,mid" \
  --clave "iot,zigbee,embedded,firmware,kubernetes,python,linux" \
  --ubicacion "valencia,valencian,barcelona,madrid" --formato json

# misma búsqueda en Barcelona o Madrid (desplazable)
python3 $S buscar "backend developer" --geo "Barcelona, Spain" --seniority "junior,mid" --dias 14
python3 $S buscar "backend developer" --geo "Madrid, Spain" --seniority "junior,mid" --dias 14

# remoto Europa (obligatorio filtrar por geografía aquí)
python3 $S remoto "backend python kubernetes" --dias 45 \
  --ubicacion "spain,worldwide,europe,emea,united kingdom,netherland"

# descripción completa de una oferta concreta
python3 $S detalle 4441123182
python3 $S detalle "https://es.linkedin.com/jobs/view/...-4441123182" --formato json

# puntuar ofertas recogidas de la web de empleo de empresas registradas
python3 $S puntuar --ofertas-file ofertas-empresas.json --clave "iot,zigbee,embedded" \
  --ubicacion "valencia,valencian,barcelona,madrid" --dias 14 --formato json

# extraer empresas unicas de una pasada de ofertas (solo las de ofertas >= 75 puntos)
python3 $S empresas --ofertas-file ofertas-pasada.json --minimo 75
```

Opciones que importan:

| Opción | Para qué |
|---|---|
| `--geo` | **Dónde se busca** (texto que entiende LinkedIn: `Valencia, Spain`) |
| `--ubicacion` | **Dónde se puntúa** (tokens; sin acentos: `valencia,valencian`). Con `remoto` es además filtro duro |
| `--clave` | Palabras del perfil que suman. Se casan **por palabra completa**: `go` no casa dentro de `algorithm` |
| `--descartar` | Palabras o empresas que restan 20. Penalizan, **no descartan** |
| `--seniority` | Banda admitida: `junior,mid,senior,lead`. Fuera de banda: −15 |
| `--dias` | Antigüedad máxima en días (por defecto 14) |
| `--detalle N` | Cuántas ofertas hidratar con su descripción (por defecto 10). `0` para no hidratar |
| `--minimo` | Descarta por debajo de esa puntuación (por defecto 55) |
| `--permitir-sin-clave` | Desactiva el descarte de ofertas sin ni una palabra del perfil |
| `--sin-cache` | Ignora la caché (TTL 6 h) |

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

## Flujo de interacción

### Paso 1 — Derivar los criterios

1. Lee `sources/criterios-busqueda.md`: ahí están fijados la **banda de
   seniority** (`junior,mid`; `senior`/`lead` descartados), la **geografía**
   (Valencia base, Barcelona y Madrid desplazable; resto de España descartado
   **solo en presencial e híbrido** — el remoto se rige por su propia línea y
   admite cualquier sede de España o Europa) y la política de **remoto**. Son
   criterios permanentes; no los rederives ni los contradigas.
2. Lee `sources/curriculum-base.md` y decide, cada vez:

- **Roles objetivo** (los 3-5 términos de búsqueda más determinantes)
- **Palabras clave**: sinónimos reales del CV en español **e inglés**
  (del `embedded` al `embebido`, `firmware`, `Zigbee`, `Kubernetes`…). Include
  las palabras que usaría la empresa, no las del CV.
- **Palabras de descarte**: lo que de verdad no es suyo (`SAP`, `scrum master`,
  `Unity`, `.NET` si no lo tiene). Añade siempre `senior,lead`: refuerza el
  castigo de banda con −20 extra.

Si el usuario ya ha dicho "buscarme ofertas de X", usa sus criterios y no le
preguntes lo que ya ha dicho.

### Paso 2 — Buscar en varias pasadas

Cuatro pasadas como mínimo, porque cada una encuentra lo que las otras no:

1. **Local** (`--geo "Valencia, Spain"`): lo que se puede ir sin mudanza.
2. **Barcelona** (`--geo "Barcelona, Spain"`): desplazable varias veces por semana.
3. **Madrid** (`--geo "Madrid, Spain"`): idem (cubre Pozuelo y el resto del área metropolitana).
4. **Remoto Europa** (`remoto`): solo tiene sentido con `--ubicacion`.

En las tres de España: `--seniority "junior,mid"` y
`--ubicacion "valencia,valencian,barcelona,madrid"`. Añade `--paginas 1` y
`--detalle 10` en todas. Guarda el JSON de cada una.

### Paso 2b — Integración con `company-jobs` (`ofertas/empresas.json`)

Las empresas registradas (pequeñas o que no publican en portales grandes) no salen
en LinkedIn. Este paso hace crecer y completar `empresas.json` trabajando junto con
la skill `company-research`. Se hace **de forma incremental y oportunista**: no se
revisan todas las empresas en una sola búsqueda.

0. **Registrar empresas nuevas** encontradas en las ofertas de esta búsqueda, pero
   solo las de ofertas con puntuación **superior a 75**:
   ```bash
   S=.opencode/skills/job-search/scripts/ofertas.py
   E=.opencode/skills/company-research/scripts/empresas.py
   # Extraer empresas unicas de las ofertas recogidas (stdin o --ofertas-file)
   python3 $S empresas --ofertas-file ofertas-pasada.json --minimo 75
   # Registrar cada una con los datos minimos:
   python3 $E upsert --nombre "EMPRESA" --ubicacion "UBICACION" --fuentes "ofertas/YYYYMMDD/lista-HHMM.md"
   ```
   (`url_empleo`, `web` y `actividad` quedan `null`: se completan en el punto 1.)

1. **Delegar la revisión en la skill `company-jobs`.** Desde la spec 07, la
   revisión de empresas registradas (completar `web`/`url_empleo`, revisar
   `url_empleo`, anotar `ultima_revision`/`ultimas_ofertas_vistas`/
   `instrucciones_agente` y eliminar las que no tengan apartado de vacantes) la
   hace la skill `company-jobs`, cuyo origen exclusivo es `empresas.json`:
   - Invocar `company-jobs` (o pedir al usuario que la ejecute) para procesar el
     lote de empresas pendientes.
   - `company-jobs` genera su propio informe en
     `ofertas/YYYYMMDD/empresas-HHMM.md` y actualiza `empresas.json`.
   - Las ofertas encontradas por `company-jobs` se incorporan a la lista de
     candidatas de este informe (Paso 4) con fuente "web de empleo de la empresa",
     junto a las de LinkedIn y remotos. Para puntuarlas, usar el subcomando
     `puntuar` como se indica arriba.
   - Si `company-jobs` no se ejecuta en esta búsqueda, se deja el lote de
     empresas pendientes para la siguiente ejecución (no se bloquea la búsqueda
     de LinkedIn).

   Comandos de referencia (los mismos que usa `company-jobs`):
   ```bash
   E=.opencode/skills/company-research/scripts/empresas.py
   S=.opencode/skills/job-search/scripts/ofertas.py
   python3 $E pendientes --limite 10 --formato json
   python3 $S puntuar --ofertas-file ofertas-empresas.json \
     --clave "..." --descartar "..." --ubicacion "..." --dias 14 --formato json
   ```

Reglas de este paso:
- **No re-revisar** empresas con `url_empleo` revisadas en los últimos 15 días.
- **Anotar la fecha de revisión siempre**, incluso si no se encontraron ofertas.
- Las empresas sin `url_empleo`: primer intento fallido queda **pendiente** (se
  anota `ultima_revision`); segundo intento fallido se **elimina** del registro y
  se anota en "Descartadas".
- Solo se registran empresas nuevas cuya oferta tenga puntuación **superior a 75**.
- La revisión de empresas registradas se **delega en `company-jobs`** (spec 07); `job-search` solo incorpora sus ofertas al informe final.
- Las ofertas de empresa se cualifican igual que el resto (argumento, qué cubre,
  qué no cubre, antigüedad).

### Paso 3 — Cualificar

Para las 5-10 mejores de cada pasada, lee la descripción
(`detalle` ya viene en el JSON; si no, `python3 $S detalle <id>`) y decide:

- **El argumento**: por qué encaja, en una frase que conecte la trayectoria con
  el negocio de la empresa. Reutiliza el eje del CV, no un listado de tecnologías.
- **Qué cubre** del `curriculum-base.md` cada requisito.
- **Qué NO cubre**: los requisitos que no puede cumplir. Esto es lo más útil de
  la lista: decide si salga la candidatura antes de escribir el CV.
- **Antigüedad**: una oferta de 20 días puede tenerla cerrada.
- **Posibilidades (0-100 o `No consta`)**: estimación de las posibilidades
  reales de obtener el puesto, más allá del encaje técnico. Tiene en cuenta la
  accesibilidad (seniority, idioma, certificaciones, competencia, antigüedad de
  la oferta, tamaño de la empresa). Si no hay base para estimar, escribe
  `No consta`. Para convocatorias públicas (si se reintrodujeran) se escribiría
  `N/A`.

Muestra la lista al usuario **antes** de escribir nada.

### Paso 4 — Escribir `ofertas/YYYYMMDD/lista-HHMM.md`
IMPORTANTE: Este paso no es opcional, el usuario espera este documento.

`YYYYMMDD` es la fecha de hoy; `HHMM` permite varias búsquedas el mismo día.

```markdown
# Ofertas por encaje — YYYY-MM-DD

> Búsqueda interna. No se envía a ninguna empresa.

## Criterios usados

- **Derivados de:** `sources/curriculum-base.md` (términos y palabras clave) y `sources/criterios-busqueda.md` (banda y geografía)
- **Términos:** [los mismos de la consulta]
- **Palabras clave:** [la lista completa]
- **Descartes:** [la lista]
- **Banda de seniority:** [...]
- **Geografía:** [qué se buscó]
- **Antigüedad máxima:** N días
- **Encaje mínimo para lista corta:** 55
- **Orden:** Posibilidades descendente (tras filtro de encaje ≥ 55)

## Lista corta

Filtro: encaje mínimo de 55. Ordenada por Posibilidades (descendente).

| # | Empresa | Puesto | Ubicación | Publicada | Encaje | Posibilidades | Enlace |
|---|---|---|---|---|---|---|---|

> Los valores de la columna **Posibilidades** se escriben con el signo `%` (por ejemplo, `70 %`). La columna **Encaje** no lleva signo.

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
| Ofertas | Web de empleo de empresas registradas (`ofertas/empresas.json`) | YYYY-MM-DD |
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
│   ├── criterios-busqueda.md     # banda de seniority, geografía y remoto (fijo)
│   └── curriculum-base.md        # de aquí se derivan el resto de criterios
├── ofertas/                     # listas de búsqueda, ignoradas por git
│   └── YYYY-MM-DD/
│       └── lista-HHMM.md
└── .opencode/skills/job-search/
    ├── SKILL.md
    ├── .gitignore               # cache/ y __pycache__/
    └── scripts/
        └── ofertas.py            # incluye subcomando `puntuar`
└── .opencode/skills/company-research/
    └── scripts/
        └── empresas.py           # gestión de ofertas/empresas.json (upsert, listar, mostrar, eliminar)
└── .opencode/skills/company-jobs/
    └── SKILL.md                 # revisión de ofertas en webs de empresas registradas
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
10. **Empresas conocidas**: revisarlas cada 15 días como mínimo; anotar siempre la fecha de revisión en `ofertas/empresas.json`, incluso sin ofertas. Las que no tengan `url_empleo`: primer intento queda pendiente, segundo intento se elimina.

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