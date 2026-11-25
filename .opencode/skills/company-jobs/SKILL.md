---
name: company-jobs
description: Revisa las ofertas publicadas en la web de empleo de las empresas registradas en ofertas/empresas.json. Origen exclusivo: ese fichero. Completa web/url_empleo cuando falten, elimina las que no tengan apartado de vacantes, anota instrucciones_agente para facilitar futuras revisiones, y genera un informe en ofertas/YYYYMMDD/empresas-HHMM.md. Úsala cuando el usuario quiera revisar las empresas registradas o actualizar sus ofertas.
---

# company-jobs

Skill de revisión de ofertas en webs de empresas registradas. Su **único origen** es
`ofertas/empresas.json`: no consulta LinkedIn, agregadores remotos ni otras fuentes.
Completa los campos `web` y `url_empleo` cuando falten, elimina las empresas que no
tengan apartado de vacantes, anota `instrucciones_agente` para facilitar futuras
revisiones y genera un informe por lote en `ofertas/YYYYMMDD/empresas-HHMM.md`.

## Configuración del lote

> **WEBS_POR_EJECUCION = 10**
>
> Este valor se indica una sola vez aquí. Cambia el número si quieres revisar más o
> menos webs por ejecución; el resto de la skill se adapta automáticamente.

## Principio de diseño

El script cubre **solo lo estructurado y determinista** (gestión del registro en
`empresas.json`, puntuación de ofertas). Todo lo **cualitativo** (si la oferta encaja
de verdad, cuál es el argumento, qué requisitos no se cubren) lo decide el agente con
la descripción completa.

Motivo: una web de empleo no expone una API uniforme; cada empresa usa su propio
portal (Workday, Teamtailor, Sage HR, páginas propias…). El agente es quien mejor
sabe extraer y normalizar las ofertas de cada una, y quien puede anotar las
`instrucciones_agente` que ahorran tokens en la siguiente revisión.

## Cuándo usar esta skill

- El usuario quiere **revisar las empresas registradas** en `ofertas/empresas.json`.
- El usuario quiere **actualizar las ofertas** publicadas por esas empresas.
- El usuario quiere **completar** los campos `web` y `url_empleo` de empresas pendientes.
- El usuario quiere **eliminar** del registro las empresas sin apartado de vacantes.
- Tras una búsqueda de `job-search`, para procesar el lote de empresas pendientes.

## Herramientas

| Herramienta | Uso |
|---|---|
| `bash` | ejecutar `empresas.py` y `ofertas.py` |
| `websearch` | buscar la web oficial y la URL de empleo cuando falten |
| `webfetch` | leer la web oficial y la web de empleo de la empresa |
| skill `account-signup` | crear o reutilizar cuenta cuando el portal exige login para ver ofertas |
| `read` | consultar `empresas.json` o el CV si hace falta |

## Comandos

```bash
E=.opencode/skills/company-research/scripts/empresas.py
S=.opencode/skills/job-search/scripts/ofertas.py

# empresas pendientes de revision (sin url_empleo)
python3 $E pendientes --limite 10 --formato json

# listar el registro completo
python3 $E listar --formato json
python3 $E listar --formato tabla

# mostrar un registro concreto
python3 $E mostrar "EMPRESA"

# upsert por stdin
python3 $E upsert --stdin <<'JSON'
{ "nombre": "...", "web": "...", "url_empleo": "...", "ultima_revision": "YYYY-MM-DD",
  "ultimas_ofertas_vistas": [], "modo_consulta": "webfetch|playwright|wget|curl|navegador|api",
  "instrucciones_agente": "...", "fuentes": ["https://..."] }
JSON

# eliminar un registro
python3 $E eliminar "EMPRESA"

# puntuar ofertas encontradas en webs de empresas
python3 $S puntuar --ofertas-file ofertas-empresas.json \
  --clave "iot,zigbee,embedded,firmware,kubernetes,python,linux" \
  --descartar "senior,lead,sap,scrum" \
  --ubicacion "valencia,valencian,barcelona,madrid" --dias 14 --formato json
```

## Flujo de interacción

### Paso 0 — Derivar los criterios (solo si se va a puntuar)

1. Lee `sources/criterios-busqueda.md`: ahí están fijados la **banda de seniority**
   (`junior,mid`; `senior`/`lead` descartados), la **geografía** (Valencia base,
   Barcelona y Madrid desplazable; resto de España descartado solo en presencial e
   híbrido) y la política de **remoto**.
2. Lee `sources/curriculum-base.md` y decide, cada vez:
   - **Roles objetivo** (los 3-5 términos de búsqueda más determinantes)
   - **Palabras clave**: sinónimos reales del CV en español e inglés.
   - **Palabras de descarte**: lo que de verdad no es suyo. Añade siempre
     `senior,lead`.
3. Si el usuario ya ha dicho "revisar empresas", usa sus criterios y no le preguntes.

Si el usuario no quiere puntuar, omite este paso y el informe solo lista las ofertas.

### Paso 1 — Seleccionar el lote

1. Lee `ofertas/empresas.json`.
2. Selecciona las empresas con `ultima_revision` nula o anterior a hoy − 15 días.
3. Ordena: primero las que no tienen `url_empleo` (para completarlas), luego por
   antigüedad de `ultima_revision` (las más antiguas primero).
4. Toma las primeras `WEBS_POR_EJECUCION` (por defecto 10).

Si no hay empresas pendientes, informa al usuario y termina sin generar informe.

### Paso 2 — Completar `web` y `url_empleo` cuando falten

Para cada empresa del lote que no tenga `web` y/o `url_empleo`:

1. Invoca `company-research` (o `websearch`/`webfetch`) para obtener `web`,
   `actividad` y `ubicacion`.
2. Busca activamente la URL de empleo (`careers`/`empleo`/`trabaja con nosotros`)
   en la web oficial con `webfetch` sobre `web`.
3. Si se encuentra `url_empleo`:
   - `upsert` con `web`, `actividad`, `url_empleo`, `modo_consulta` (según la URL
     encontrada: `playwright` si es portal JS, `webfetch` si es estática, `api` si
     expone JSON).
   - Si además se revisó la web de empleo, anota `ultima_revision` y
     `ultimas_ofertas_vistas`.
4. Si **no** se encuentra:
   - **Primer intento** (no tenía `ultima_revision` previa): `upsert` con
     `ultima_revision = hoy` y `ultimas_ofertas_vistas: []`. Queda pendiente para
     la siguiente ejecución.
   - **Segundo intento** (ya tenía `ultima_revision` previa): `eliminar` del
     registro y anotarla en la sección "Eliminadas" del informe con motivo
     "sin URL de empleo tras 2 intentos".

El resto de pendientes se dejan para la siguiente ejecución.

### Paso 3 — Revisar las webs con `url_empleo`

Para cada empresa del lote que tenga `url_empleo`:

1. `webfetch` sobre `url_empleo`.
2. Extrae las ofertas visibles: `titulo`, `url`, `ubicacion`, `publicada` (si consta).
3. **Genera `instrucciones_agente` y `modo_consulta`**: texto breve y accionable para el próximo
   agente, con:
   - **`modo_consulta`**: herramienta recomendada para la próxima revisión. Valores:
     `webfetch` (webs estáticas), `playwright` (portales JS), `wget`/`curl` (HTML grande,
     filtrar localmente), `navegador` (genérico), `api` (endpoint JSON disponible).
   - URL exacta a consultar.
   - Si hay API/JSON disponible.
   - Selectores CSS o estructura de la página.
   - Paginación (parámetro y última página).
   - Filtros recomendados.
   - Avisos (p. ej. "no cargar imágenes", "requiere JavaScript").
4. `upsert` con:
   - `ultima_revision = hoy`
   - `ultimas_ofertas_vistas` (lista encontrada, o `[]` si no hubo ofertas)
   - `modo_consulta`
   - `instrucciones_agente`
   - `fuentes` (URLs usadas)
5. Normaliza cada oferta al esquema único (`titulo`, `empresa`, `ubicacion`,
   `remoto`, `fecha`, `url`, `fuente = empresa`) y, si se derivaron criterios,
   puntúala con `ofertas.py puntuar`.

Reglas de este paso:
- **Anotar la fecha de revisión siempre**, incluso si no se encontraron ofertas.
- **Generar `instrucciones_agente` siempre**, incluso si la web no tuvo ofertas:
  la forma de consultarla sigue siendo útil para la próxima vez.
- Si el `webfetch` falla, anota el error en `instrucciones_agente` (p. ej.
  "webfetch falló: timeout; probar con navegador") y conserva el valor anterior
  si lo había.
- Si la web exige login para ver ofertas, invoca `account-signup` cuando sea
  necesario para avanzar. Anota el resultado en el informe (sección «Cuentas»),
  **nunca** en `empresas.json`. Sin credenciales en el registro: van en
  `SENSIBLE/credenciales.env`.

### Paso 4 — Generar `ofertas/YYYYMMDD/empresas-HHMM.md`

IMPORTANTE: este paso no es opcional. El usuario espera este documento.

`YYYYMMDD` es la fecha de hoy; `HHMM` permite varias ejecuciones el mismo día.

```markdown
# Revisión de empresas registradas — YYYY-MM-DD

> Búsqueda interna. No se envía a ninguna empresa.

## Criterios usados

- **Derivados de:** `sources/curriculum-base.md` y `sources/criterios-busqueda.md`
- **Palabras clave:** [la lista completa, si se puntuó]
- **Descartes:** [la lista, si se puntuó]
- **Banda de seniority:** [...]
- **Geografía:** [...]
- **Antigüedad máxima:** N días
- **Encaje mínimo para lista corta:** 55
- **Empresas revisadas en este lote:** N (valor de WEBS_POR_EJECUCION)
- **Orden:** Posibilidades descendente (tras filtro de encaje ≥ 55)

## Empresas revisadas

| # | Empresa | url_empleo | Ofertas encontradas | Instrucciones |
|---|---|---|---|---|
| 1 | ... | https://... | 3 | ver campo instrucciones_agente |

## Lista corta (ofertas con encaje ≥ 55)

Filtro: encaje mínimo de 55. Ordenada por Posibilidades (descendente).

| # | Empresa | Puesto | Ubicación | Publicada | Encaje | Posibilidades | Enlace |
|---|---|---|---|---|---|---|---|

> Los valores de la columna **Posibilidades** se escriben con el signo `%`.
> La columna **Encaje** no lleva signo.

## Detalle

### 1. EMPRESA — Puesto

- **Argumento:** [una frase, el eje]
- **Qué cubre:** [requisito → parte del CV]
- **Qué no cubre:** [requisito → por qué]
- **Verificar antes de postular:** [...]
- **Siguiente paso:** `nueva_candidatura.py "EMPRESA"`

## Eliminadas

| Empresa | Motivo |
|---|---|
| ... | sin URL de empleo tras 2 intentos |

## Pendientes para el próximo lote

| Empresa | Motivo |
|---|---|
| ... | sin revisar (lote completo) |

## Cuentas

| Empresa | Dominio | Estado | Uso |
|---|---|---|---|
| [o «Ninguna»] | | | crear \| reutilizar \| pendiente-verificacion |

## Fuentes

| Dato | Fuente | Fecha |
|---|---|---|
| Ofertas | Web de empleo de empresas registradas (`ofertas/empresas.json`) | YYYY-MM-DD |
```

Reglas del fichero:
- **Los criterios van a la cabecera** si se puntuó. Si no se puntuó, omite la sección
  "Criterios usados" y la "Lista corta", y deja solo "Empresas revisadas" y "Detalle".
- **Toda cifra viene del JSON** de la revisión, con su fecha.
- Si un dato no aparece en ninguna fuente, escribe `No consta`. No estimes.
- Marca las ofertas de más de 14 días como probablemente cerradas.
- Nunca escribas credenciales en el informe: van en `SENSIBLE/credenciales.env`.

---

## Estructura de archivos

```
trabajo/
├── sources/
│   ├── criterios-busqueda.md
│   └── curriculum-base.md
├── ofertas/                     # listas de búsqueda, ignoradas por git
│   └── YYYYMMDD/
│       ├── lista-HHMM.md        # job-search
│       └── empresas-HHMM.md      # company-jobs
├── .opencode/skills/
│   ├── account-signup/          # cuentas cuando el portal exige login
│   │   ├── SKILL.md
│   │   └── scripts/cuentas.py
│   ├── company-research/
│   │   └── scripts/empresas.py  # gestión de ofertas/empresas.json
│   ├── company-jobs/
│   │   └── SKILL.md
│   └── job-search/
│       └── scripts/ofertas.py   # subcomando puntuar
└── SENSIBLE/                    # ignorado por git
    ├── credenciales.env
    └── cuentas.json
```

---

## Reglas importantes

1. **Origen exclusivo.** Esta skill solo lee y escribe `ofertas/empresas.json`. No
   consulta LinkedIn, agregadores remotos ni otras fuentes.
2. **Un lote por ejecución.** Se revisan como máximo `WEBS_POR_EJECUCION` webs por
   ejecución. El resto queda para la siguiente.
3. **Anotar siempre.** `ultima_revision` se anota incluso si no se encontraron ofertas.
   Lo mismo aplica a `instrucciones_agente`.
4. **Eliminar con criterio.** Una empresa sin `url_empleo` se elimina solo tras dos
   intentos fallidos (o si el usuario lo pide explícitamente).
5. **Completar antes de revisar.** Si falta `web` o `url_empleo`, se completa primero
   y se revisa después (o se elimina si no se encuentra).
6. **Instrucciones accionables.** `instrucciones_agente` debe ser lo suficientemente
   concreto para que el próximo agente ahorre tokens: URL exacta, selectores,
   paginación, avisos.
7. **Puntuación en dos capas.** La puntuación técnica es del script; el argumento
   y la cualificación son del agente.
8. **Sin commits** sin que el usuario lo pida. `ofertas/` sí se versiona.
9. **Idioma:** castellano para el informe.
10. **Sin datos inventados.** Un dato que no se pueda verificar se deja como `null`
    y se anota como `No consta` en el informe.
11. **Cuentas fuera del registro.** Si hace falta una cuenta para ver ofertas, la
    crea `account-signup`; el resultado se anota en el informe, jamás en
    `empresas.json` y nunca con credenciales.

---

## Detalles de la fuente que ya están comprobados

- `empresas.py` hace upsert por slug: si la empresa ya existe, solo sobrescribe los
  campos presentes y no vacíos.
- `empresas.py pendientes --limite N` devuelve las empresas sin `url_empleo`.
- `ofertas.py puntuar` acepta un fichero JSON con ofertas y aplica los mismos filtros
  que `buscar`.
- La política de dos intentos se infiere de `ultima_revision`: si ya tenía fecha y
  sigue sin `url_empleo`, es el segundo intento.