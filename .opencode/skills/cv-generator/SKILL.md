# CV Generator Skill

Genera CVs y cartas de presentación adaptados a empresas específicas, con
salida en `output/YYYYMMDD-nombreempresa/`. Junto a ellos deja `info.md`, el
documento de trabajo con los datos de la empresa y de la oferta.

La estructura del CV es la de `sources/curriculum-base.md`: cabecera con foto,
perfil, experiencia, proyecto destacado, tecnologías, formación y contacto al
final. `nueva_candidatura.py` copia ese base al directorio de la candidatura, y
el agente **adapta el texto** a la empresa.

## Cuándo usar esta skill

Usa esta skill cuando el usuario quiera generar un CV adaptado y/o carta de
presentación para una empresa concreta. El usuario debe proporcionar (o la skill
debe preguntar):

- **Nombre de la empresa** (obligatorio)
- **Detalles del puesto** (opcional, pero recomendado)
- **Link a la oferta** (opcional)

## Convención de salida

Cada candidatura vive en su propio directorio:

```
output/YYYYMMDD-nombreempresa/
├── info.md                    # datos de empresa y oferta (uso interno)
├── pin.png                    # foto de la cabecera del CV
├── curriculum-EMPRESA.md      # fuente editable
└── carta-EMPRESA.md           # fuente editable
```

- `YYYYMMDD` = fecha de generación.
- `nombreempresa` = nombre comercial normalizado a **minúsculas, sin acentos y
  sin espacios** (`CityPrive PSFP` → `cityprive-psfp`).
- Los ficheros internos conservan el nombre de la empresa **en mayúsculas**
  (`curriculum-EDICOM.md`), que es como se lee en la carta.
- `info.md` **no se envía a la empresa**: es el soporte de trabajo que sostiene
  las cifras citadas en el CV y en la carta. Se genera en el Paso 5.

No lo construyas a mano: el script aplica la normalización y reutiliza el
directorio si ya existe (así se puede reejecutar tras revisar el `.md`).

```bash
python3 .opencode/skills/cv-generator/scripts/nueva_candidatura.py "EDICOM"
# -> output/20260930-edicom/
#      pin.png                     (copia de assets/pin.png)
#      curriculum-EDICOM.md         (copia de sources/curriculum-base.md)
#      carta-EDICOM.md              (pendiente de redactar)
```

El script **deja el CV base ya copiado y con su nombre**: el trabajo del agente
consiste en *adaptar esa copia* (Paso 6), no en redactar el CV desde cero. Así la
estructura —cabecera con foto, secciones, contacto al final— es idéntica en todas
las candidaturas y lo único que cambia son las palabras.

Opciones útiles:

```bash
# otra foto para la cabecera (assets/ tiene varias)
python3 .opencode/skills/cv-generator/scripts/nueva_candidatura.py "EDICOM" --foto assets/foto2.jpeg

# CV sin foto (hay que quitar el <img> de la cabecera del .md)
python3 .opencode/skills/cv-generator/scripts/nueva_candidatura.py "EDICOM" --sin-foto
```

El script **no sobrescribe** ni la foto ni el CV si ya existen: reejecutarlo tras
retocar el `.md` no tira el trabajo.

## Flujo de interacción

### Paso 1 — Recopilar información del usuario

Si el usuario no ha proporcionado todos los datos, pregunta:

```
¿Para qué empresa quieres generar el CV?
¿Tienes detalles del puesto? (opcional)
¿Tienes un link a la oferta? (opcional)
```

### Paso 2 — Buscar información de la empresa

Usa `websearch` para buscar información sobre la empresa:

```
websearch("[nombre empresa] [sector/ubicación si se conoce]")
```

Extrae:
- Sector de actividad
- Tamaño aproximado (si está disponible)
- Productos/servicios principales
- Valores o cultura corporativa (si están disponibles)
- Ubicación de la oficina principal

Si la empresa cotiza o tiene datos registrales, la skill `company-research`
resuelve la entidad legal de forma determinista:

```bash
python3 .opencode/skills/company-research/scripts/company_research.py "Wecity" --section identity
```

### Paso 3 — Confirmar con el usuario

**REGLA CRÍTICA:** Antes de generar nada, confirma con el usuario que la
información encontrada corresponde a la empresa correcta:

```
He encontrado información sobre [nombre empresa]:
- Razón social: [razón social]
- Sector: [sector]
- Producto/servicios: [productos]
- Ubicación: [ubicación]

¿Es esta la empresa correcta? (sí/no)
```

Si el usuario dice "no", vuelve al Paso 2 con más detalles.

> Las fuentes se citan con su fecha: el registro de la CNMV, el dominio oficial
> y los directorios de empleo pueden discrepar (p. ej. el número de registro de
> una plataforma de crowdfunding). Ante contradicción, manda la fuente
> oficial y la del regulador.

### Paso 4 — Buscar información de la oferta

Si el usuario proporcionó un link de oferta:

```
webfetch(url="[link de oferta]", format="markdown")
```

Si no hay link pero el usuario dio detalles del puesto, usa esa información.

Si no hay link ni detalles, pregunta:

```
¿Tienes más detalles sobre el puesto? (responsabilidades, requisitos, etc.)
```

Con esto se tiene todo lo necesario para el Paso 5.

### Paso 5 — Redactar `info.md`

Consolida en `output/YYYYMMDD-nombreempresa/info.md` todo lo recogido en los
Pasos 2 y 4. **No repitas búsquedas**: escribe con lo que ya tienes a mano.

Estructura:

```markdown
# Información de la candidatura — EMPRESA

> Documento de trabajo interno. No se envía a la empresa.
> Es la fuente de las cifras citadas en el CV y en la carta.

- **Fecha:** YYYY-MM-DD
- **Puesto:** [nombre del puesto]
- **Link de la oferta:** [url | no facilitado]

## Empresa

| Campo | Valor |
| --- | --- |
| Nombre comercial | |
| Razón social | |
| Sector | |
| Fundación | |
| Tamaño (empleados) | |
| Sede | |
| Producto o servicio principal | |

- **Cifras verificables:** [las que se citarán en la carta, con su año]
- **Cultura o valores:** [solo si son públicos y relevantes para el puesto]

## Oferta

- **Puesto:**
- **Responsabilidades:**
- **Requisitos obligatorios:**
- **Deseables:**
- **Condiciones:** [jornada, ubicación, remoto/presencial, rango si consta]
- **Encaje con el perfil:** [qué parte de `sources/curriculum-base.md`
  cubre cada requisito; y qué requisitos no puedes cubrir]

## Fuentes

| Dato | Fuente | Fecha |
| --- | --- | --- |
| Razón social | Registro Mercantil | 2026-09-29 |
```

De dónde sale cada bloque:

- **Empresa:** salida de `company_research.py` (`--section identity`,
  `--section financials`, `--section registry`) más lo que devuelva `websearch`.
- **Oferta:** el `webfetch` del enlace, o lo que cuenta el usuario.
- **Fuentes:** la URL de cada dato. La oferta va siempre; el resto, solo lo que
  se haya citado de forma verificable.

Reglas del fichero:

- **Si un dato no aparece en ninguna fuente, escribe `No consta`.** Nunca
  completes con estimaciones ni con memoria del modelo: la misma regla de
  verificación que aplica `company-research`.
- **Toda cifra que aparezca en el CV o en la carta debe ser rastreable hasta una
  fila de la tabla `Fuentes`.** Si no lo está, no se cita.
- Si escribes un email o link web debe ser navegable.
- Muestra el fichero al usuario antes de continuar. Es el momento barato de
  detectar que la oferta es de otra empresa o que el puesto no encaja.

### Paso 6 — Generar CV adaptado

1. Crea el directorio con `nueva_candidatura.py` (ver "Convención de salida"). Ya
   deja `pin.png` y una copia de `sources/curriculum-base.md` como
   `curriculum-EMPRESA.md`.
2. **Edita esa copia**, conservando su estructura. La estructura es fija:
   cabecera con foto, `Perfil Profesional`, `Experiencia Laboral`, `Experiencia
   Anterior`, `Proyecto Destacado`, `Tecnologías`, `Formación`, `Contacto` al final.
   Cambia el contenido, no el esqueleto.
3. Adapta el texto según la empresa y el puesto:
   - **Tagline de la cabecera** (`<strong>` bajo el nombre): el rótulo con el que
     te presentas. Ajusta el énfasis según el sector.
   - **Perfil profesional:** cuenta el eje que conecta tu trayectoria con el
     negocio de la empresa. No lo escribas como si sirviera para todas.
   - **Experiencia laboral:** resalta la experiencia más relevante para el puesto.
     La sección `Experiencia Anterior` se puede comprimir más si el puesto es
     junior; desplegarla si el puesto es senior.
   - **Proyecto destacado:** conéctalo con las necesidades de la empresa si es
     relevante.
   - **Tecnologías:** reordena las cuatro líneas para que la primera sea la que
     más pesa en la oferta. No añadas ninguna que no esté en la base.

**Adapta, no inventes:** todo el contenido debe ser trazable a
`sources/curriculum-base.md`. No añadidas tecnologías, certificaciones ni
responsabilidades que no estén ahí. Si la oferta pide algo que no tienes
(por ejemplo, un lenguaje que no dominas), menciónalo con honestidad en la
carta en lugar de ocultarlo.

**Un argumento, no un listado.** Un CV genérico no destaca. Identifica el eje
que conecta la trayectoria con el negocio de la empresa y narralo en el perfil
profesional. Ver el ejemplo de EDICOM: el eje es la conjunción del software y
de la capa física —eliotricidad, redes y hardware—, que es justo lo que aporta a
una empresa que opera sus propios centros de datos.

**Cuida la cabecera.** La tabla HTML de dos columnas lleva la foto. Sus anchos
están en **píxeles absolutos a propósito** (`width="700"`, `90` + `610`): el
importador HTML de LibreOffice ignora los porcentajes y, con `width="100%"`, la
columna del texto se estrecha tanto que el nombre se parte en tres líneas. Si
cambias algo de ahí, conserva los píxeles.

### Paso 7 — Generar carta de presentación

Genera `carta-EMPRESA.md` con **tono formal** (estándar en el mercado español).

Estructura probada (ver `output/20260929-wecity/carta-WECITY.md`):

```markdown
# Carta de presentación — wecity (RAZÓN SOCIAL, S.L.)

Estimado equipo de selección de personal:

[Una frase: a qué puesto se postula y por qué esta empresa.]

QUÉ APORTO:

[Dos o tres párrafos cortos: perfil, evidencia concreta, encaje con el producto.]

MI DISPONIBILIDAD:

[Disponibilidad, ubicación, remoto o presencial, disposición a entrevista.]

Atentamente, David Moreno Bolívar
```

Reglas de estilo:

- **Concisa.** La carta se lee en un minuto. Tres párrafos bastan; si se
  acerca a la carta entera, sobra.
- **Encabezados en mayúsculas y con dos puntos** (`QUÉ APORTO:`) para que se
  lean como un escaneo rápido.
- **Sin membretes ni logotipos** innecesarios. La carta se envía en texto plano
  o pegada en un formulario.
- **Cifras verificables de la empresa, no adjetivos.** En WeCity: 221 proyectos
  financiados, 293 M€ movilizados, 0% de impago. Esos datos demuestran que se
  ha investigado; "empresa líder e-mortaria" no.
- **Sin excessos ni adornos.** Una frase de despedida basta.
- Firma siempre con "Atentamente," y el nombre completo.

### Paso 8 — Confirmar archivos generados

Muestra al usuario un resumen:

```
✅ Archivos generados en output/20260929-nombreempresa/:
- info.md                 (uso interno, no enviar)
- curriculum-EMPRESA.md   (1 página)
- carta-EMPRESA.md        (1 página)
```

## Estructura de archivos del proyecto

```
trabajo/
├── sources/
│   ├── curriculum-base.md          # CV base: contenido + estructura de referencia
│   └── curriculum-github.md        # CV en formato GitHub
├── output/                         # Candidaturas generadas
│   └── ...
├── assets/
│   ├── pin.png                     # Foto de la cabecera del CV
│   ├── foto.jpg
│   └── foto2.jpeg
├── templates/
│   └── curriculum-odt.odt         # Plantilla de referencia
└── .opencode/skills/cv-generator/
    ├── SKILL.md
    └── scripts/
        ├── nueva_candidatura.py    # Prepara output/YYYYMMDD-nombreempresa/
        └── md2odt.py               # Markdown -> ODT + PDF, valida 1 página
```

## Reglas importantes

1. **Siempre confirma la empresa con el usuario** antes de generar archivos
   (evita homónimas)
2. **Tono formal** en la carta de presentación (estándar en España)
3. **Adapta, no inventes:** usa solo la información de
   `sources/curriculum-base.md` como base
4. **Idioma:** castellano para CVs y cartas
6. **Output:** todo en `output/YYYYMMDD-nombreempresa/`, que **está versionado
   en git** a propósito: guarda el historial de lo enviado a cada empresa. Aun
   así, no hacer commit sin que el usuario lo pida expresamente.
7. **Nada de separadores `---`** en el Markdown del CV: se renderizan como
   doble línea. Las cabeceras `##` ya delimitan las secciones.
8. **Traza de los datos externos:** toda cifra o dato sobre la empresa citado en
   el CV o en la carta debe ser rastreable en `info.md`, con su fuente. Si no
   aparece ahí, no va. Un dato que no se ha podido verificar se escribe como
   `No consta`, nunca estimado.
9. **La estructura del CV es fija.** Se adapta el texto de
   `sources/curriculum-base.md`, no se rehace el esqueleto. En particular, el
   `Contacto` va **al final**, no al principio, y la cabecera conserva su tabla
   de dos columnas con la foto.

## Ejemplo de uso

```
Usuario: "Genera un CV para Inditex"

Skill:
  1. ¿Tienes detalles del puesto? ¿Link a la oferta?
  2. [Busca info de Inditex en web]
  3. Confirma: "He encontrado Inditex, sector retail/textil, ¿es correcto?"
  4. [Si hay link, webfetch; si no, pregunta detalles]
  5. nueva_candidatura.py "Inditex"  ->  output/20260930-inditex/
                                      (copia pin.png y curriculum-base.md)
  6. Escribe output/20260930-inditex/info.md (empresa + oferta + fuentes)
  7. Edita output/20260930-inditex/curriculum-INDITEX.md (adapta, no reescribir)
  8. Escribe output/20260930-inditex/carta-INDITEX.md
  9. md2odt.py sobre ambos  ->  .odt + .pdf, 1 pagina cada uno
 10. Confirma archivos generados
```

## Ejemplos de referencia

- **Formato del CV:** `output/20260929-achm-hotels (Grand Hotel Centenari)/`. Cabecera con foto, contacto al
  final, `Experiencia Anterior` comprimida, proyecto destacado con la cadena
  técnica. Úsala como referencia de estructura y de encaje.
- **Tono de la carta:** `output/20260929-achm-hotels (Grand Hotel Centenari)`. Corta, con
  encabezados en mayúsculas y cifras verificables. Úsala cuando no haya una
  oferta concreta de la que tirar.
