# CV Generator Skill

Genera CVs y cartas de presentación adaptados a empresas específicas, con
salida en `output/YYYYMMDD-nombreempresa/`.

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
├── curriculum-EMPRESA.md      # fuente editable
├── curriculum-EMPRESA.odt     # entregable ofimática
├── curriculum-EMPRESA.pdf     # entregable para enviar
├── carta-EMPRESA.md           # fuente editable
├── carta-EMPRESA.odt
└── carta-EMPRESA.pdf
```

- `YYYYMMDD` = fecha de generación.
- `nombreempresa` = nombre comercial normalizado a **minúsculas, sin acentos y
  sin espacios** (`CityPrive PSFP` → `cityprive-psfp`).
- Los ficheros internos conservan el nombre de la empresa **en mayúsculas**
  (`curriculum-WECITY.md`), que es como se lee en la carta.

No lo construyas a mano: el script aplica la normalización y reutiliza el
directorio si ya existe (así se puede reejecutar tras revisar el `.md`).

```bash
python3 .opencode/skills/cv-generator/scripts/nueva_candidatura.py "CityPrive"
# -> output/20260929-cityprive
```

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

### Paso 5 — Generar CV adaptado

1. Lee `sources/curriculum-base.md`
2. Crea el directorio de la candidatura (Paso 1 de "Convención de salida")
3. Adapta el CV según la empresa y el puesto:
   - **Perfil profesional:** ajusta el énfasis según el sector de la empresa
   - **Experiencia laboral:** resalta la experiencia más relevante para el puesto
   - **Tecnologías:** prioriza las tecnologías que mencione la oferta
   - **Proyecto destacado:** conecta el proyecto con las necesidades de la
     empresa si es relevante
4. Guárdalo como `output/YYYYMMDD-nombreempresa/curriculum-EMPRESA.md`

**Adapta, no inventes:** todo el contenido debe ser trazable a
`sources/curriculum-base.md`. No añadidas tecnologías, certificaciones ni
responsabilidades que no estén ahí. Si la oferta pide algo que no tienes
(por ejemplo, un lenguaje que no dominas), menciónalo con honestidad en la
carta en lugar de ocultarlo.

**Un argumento, no un listado.** Un CV genérico no destaca. Identifica el eje
que conecta la trayectoria con el negocio de la empresa y narralo en el perfil
profesional. Ver el ejemplo de WeCity: el eje es conocer el edificio
inteligente *y* su software, que es justo lo que aporta a una plataforma
financiera inmobiliaria.

### Paso 6 — Generar carta de presentación

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

### Paso 7 — Convertir a ODT y PDF

Convierte ambos ficheros con el script de la skill:

```bash
python3 .opencode/skills/cv-generator/scripts/md2odt.py output/20260929-nombreempresa/curriculum-EMPRESA.md
python3 .opencode/skills/cv-generator/scripts/md2odt.py output/20260929-nombreempresa/carta-EMPRESA.md
```

Genera `.odt` y `.pdf` junto al `.md`, e imprime el número de páginas. **Devuelve
código de salida 2 si el documento no cabe en una página**: en ese caso hay que
ajustar el contenido, no el formato.

> **Por qué el script y no `libreoffice --convert-to odt` directamente**
> El filtro de importación Markdown de LibreOffice no está disponible en esta
> máquina y degrada el fichero a *texto preformateado*, dejando los `#` y `**`
> literales dentro del ODT. El script va por Markdown → HTML con CSS de
> impresión A4 → ODT, que sí respeta tipografía, márgenes y espaciados.
> Ajusta con `--base-size` (cuerpo, por defecto 8.5) y `--margin` (por defecto
> 1.2 cm) antes de recortar contenido.

### Paso 8 — Confirmar archivos generados

Muestra al usuario un resumen:

```
✅ Archivos generados en output/20260929-nombreempresa/:
- curriculum-EMPRESA.md / .odt / .pdf   (1 página)
- carta-EMPRESA.md / .odt / .pdf        (1 página)
```

## Estructura de archivos del proyecto

```
trabajo/
├── sources/
│   ├── curriculum-base.md          # CV base (fuente para adaptar)
│   └── curriculum-github.md        # CV en formato GitHub
├── output/                         # Candidaturas generadas
│   └── 20260929-wecity/
│       ├── curriculum-WECITY.md
│       ├── curriculum-WECITY.odt
│       ├── curriculum-WECITY.pdf
│       ├── carta-WECITY.md
│       ├── carta-WECITY.odt
│       └── carta-WECITY.pdf
├── assets/
│   ├── foto.jpg
│   └── foto2.jpeg
├── templates/
│   └── curriculum-odt.odt         # Plantilla de referencia
└── .opencode/skills/cv-generator/
    ├── SKILL.md
    └── scripts/
        ├── nueva_candidatura.py    # Crea output/YYYYMMDD-nombreempresa/
        └── md2odt.py               # Markdown -> ODT + PDF, valida 1 página
```

## Reglas importantes

1. **Siempre confirma la empresa con el usuario** antes de generar archivos
   (evita homónimas)
2. **Tono formal** en la carta de presentación (estándar en España)
3. **Adapta, no inventes:** usa solo la información de
   `sources/curriculum-base.md` como base
4. **Idioma:** castellano para CVs y cartas
5. **Formato:** 1 página para el CV, 1 página para la carta
6. **Output:** todo en `output/YYYYMMDD-nombreempresa/`, que **está versionado
   en git** a propósito: guarda el historial de lo enviado a cada empresa. Aun
   así, no hacer commit sin que el usuario lo pida expresamente.
7. **Nada de separadores `---`** en el Markdown del CV: se renderizan como
   doble línea. Las cabeceras `##` ya delimitan las secciones.

## Ejemplo de uso

```
Usuario: "Genera un CV para Inditex"

Skill:
 1. ¿Tienes detalles del puesto? ¿Link a la oferta?
 2. [Busca info de Inditex en web]
 3. Confirma: "He encontrado Inditex, sector retail/textil, ¿es correcto?"
 4. [Si hay link, webfetch; si no, pregunta detalles]
 5. nueva_candidatura.py "Inditex"  ->  output/20260929-inditex/
 6. Escribe output/20260929-inditex/curriculum-INDITEX.md
 7. Escribe output/20260929-inditex/carta-INDITEX.md
 8. md2odt.py sobre ambos  ->  .odt + .pdf, 1 pagina cada uno
 9. Confirma archivos generados
```

## Ejemplo de referencia

`output/20260929-wecity/` es la candidatura de referencia: CV genérico
adaptado a una fintech regulada (crowdfunding inmobiliario) y carta concisa
sin membretes. Úsala como referencia de tono, estructura y encaje cuando no
haya una oferta concreta.
