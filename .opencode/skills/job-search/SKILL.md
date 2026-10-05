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

## Fuentes

| Fuente | Uso | Límite conocido |
|---|---|---|
| LinkedIn (endpoint público de invitado) | **La principal.** Ofertas de España con título, empresa, fecha y descripción completa | Es un endpoint no oficial aunque público y anónimo; ritmo limitado. `f_WT` (filtro de remoto) **no lo respeta**: el remoto se detecta por el texto de la ubicación |
| Remotive, Himalayas | Complemento de **remoto Europa** | Cobertura de España casi nula: filtrar siempre por `--ubicacion` |
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

# descripción completa de una oferta concreta
python3 $S detalle 4441123182
python3 $S detalle "https://es.linkedin.com/jobs/view/...-4441123182" --formato json
```

Opciones que importan:

| Opción | Para qué |
|---|---|
| `--geo` | **Dónde se busca** (texto que entiende LinkedIn: `Valencia, Spain`) |
| `--ubicacion` | **Dónde se puntúa** (tokens; sin acentos: `valencia,valencian`). Con `remoto` es además filtro duro |
| `--clave` | Palabras del perfil que suman. Se casan **por palabra completa**: `go` no casa dentro de `algorithm` |
| `--descartar` | Palabras o empresas que restan 20. Penalizan, **no descartan** |
| `--seniority` | Banda admitida: `junior,mid,senior,lead`. Fuera de banda: −15 |
| `--minimo` | Descarta por debajo de esa puntuación (por defecto 1) |
| `--permitir-sin-clave` | Desactiva el descarte de ofertas sin ni una palabra del perfil |
| `--detalle N` | Cuántas ofertas hidratar con su descripción (por defecto 10). `0` para no hidratar |
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

Tres búsquedas como mínimo, porque cada una encuentra lo que las otras no:

1. **Local** (`--geo "Valencia, Spain"`): lo que se puede ir sin mudanza.
2. **Nacional** (`--geo "Spain"`): lo que ya se vio en candidaturas anteriores (Pozuelo,
   Sevilla, Vigo).
3. **Remoto Europa** (`remoto`): solo tiene sentido con `--ubicacion`.

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