# CV Generator Skill

Skill local para generar CVs y cartas de presentación adaptados a empresas específicas.

## Cuándo usar esta skill

Usa esta skill cuando el usuario quiera generar un CV adaptado y/o carta de presentación para una empresa concreta. El usuario debe proporcionar (o la skill debe preguntar):

- **Nombre de la empresa** (obligatorio)
- **Detalles del puesto** (opcional, pero recomendado)
- **Link de la oferta** (opcional)

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

### Paso 3 — Confirmar con el usuario

**REGLA CRÍTICA:** Antes de generar nada, confirma con el usuario que la información encontrada corresponde a la empresa correcta:

```
He encontrado información sobre [nombre empresa]:
- Sector: [sector]
- Productos/servicios: [productos]
- Ubicación: [ubicación]

¿Es esta la empresa correcta? (sí/no)
```

Si el usuario dice "no", vuelve al Paso 2 con más detalles.

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
2. Adapta el CV según la empresa y el puesto:
   - **Perfil profesional:** ajusta el énfasis según el sector de la empresa
   - **Experiencia laboral:** resalta la experiencia más relevante para el puesto
   - **Tecnologías:** prioriza las tecnologías que mencione la oferta
   - **Proyecto destacado:** conecta el proyecto con las necesidades de la empresa si es relevante
3. Guarda como `output/curriculum-NOMBREEMPRESA.md`

### Paso 6 — Generar carta de presentación

Genera una carta con **tono formal** (estándar en el mercado español):

```
output/carta-NOMBREEMPRESA.md
```

Estructura de la carta:
- Fecha actual
- Nombre del destinatario (si se conoce) o "Equipo de Selección"
- Nombre de la empresa
- Párrafo de apertura: puesto al que se aplica y dónde se encontró la oferta
- Párrafo de motivación: por qué esta empresa (usar info del Paso 2)
- Párrafo de valor: qué aporta el candidato (usar info del CV adaptado)
- Párrafo de cierre: disponibilidad y disposición a entrevista
- Despedida formal: "Atentamente," + nombre completo + contacto

### Paso 7 — Convertir a ODT

Convierte ambos archivos markdown a ODT usando LibreOffice:

```bash
libreoffice --headless --convert-to odt output/curriculum-NOMBREEMPRESA.md --outdir output/
libreoffice --headless --convert-to odt output/carta-NOMBREEMPRESA.md --outdir output/
```

### Paso 8 — Confirmar archivos generados

Muestra al usuario un resumen:

```
✅ Archivos generados:
- output/curriculum-NOMBREEMPRESA.md
- output/curriculum-NOMBREEMPRESA.odt
- output/carta-NOMBREEMPRESA.md
- output/carta-NOMBREEMPRESA.odt
```

## Estructura de archivos del proyecto

```
trabajo/
├── sources/
│   ├── curriculum-base.md          # CV base (fuente para adaptar)
│   └── curriculum-github.md        # CV en formato GitHub
├── output/                         # CVs generados (gitignored)
│   ├── curriculum-EMPRESA.md
│   ├── curriculum-EMPRESA.odt
│   ├── carta-EMPRESA.md
│   └── carta-EMPRESA.odt
├── assets/
│   ├── foto.jpg
│   └── foto2.jpeg
└── templates/
    └── curriculum-odt.odt         # Plantilla de referencia
```

## Reglas importantes

1. **Siempre confirma la empresa con el usuario** antes de generar archivos (evita homónimas)
2. **Tono formal** en la carta de presentación (estándar en España)
3. **Adapta, no inventes:** usa solo la información de `sources/curriculum-base.md` como base
4. **Idioma:** castellano para CVs y cartas
5. **Formato:** 1 página para el CV, 1 página para la carta
6. **Output:** los archivos van en `output/` (ignorado por git)

## Ejemplo de uso

```
Usuario: "Genera un CV para Inditex"

Skill:
1. ¿Tienes detalles del puesto? ¿Link a la oferta?
2. [Busca info de Inditex en web]
3. Confirma: "He encontrado Inditex, sector retail/textil, ¿es correcto?"
4. [Si hay link, webfetch; si no, pregunta detalles]
5. Genera output/curriculum-INDITEX.md
6. Genera output/carta-INDITEX.md
7. Convierte ambos a ODT
8. Confirma archivos generados
```
