# Curriculum — David Moreno Bolívar

Repositorio personal de CV y portfolio.

## Estructura

- [`sources/`](sources/) — Fuentes de contenido base (editar aquí)
  - `curriculum-github.md` — CV en formato Markdown (GitHub), con badges y secciones desplegables.
  - `curriculum-base.md` — **Plantilla del CV**: contenido base y estructura de
    referencia (cabecera con foto, contacto al final). Es lo que se copia y adapta
    en cada candidatura.
- [`templates/`](templates/) — Plantillas de referencia
  - `curriculum-odt.odt` — Última versión ODT generada como referencia.
- [`output/`](output/) — Candidaturas generadas, una carpeta por empresa con su fecha
  (`output/YYYYMMDD-nombreempresa/`). Cada una lleva el CV y la carta en `.md`, `.odt` y `.pdf`.
  Ver `output/20260930-edicom/` como referencia de formato del CV.
- [`ofertas/`](ofertas/) — Listas de ofertas por encaje, una carpeta por día
  (`ofertas/YYYYMMDD/lista-HHMM.md`). Guardan qué había disponible en cada búsqueda.
- [`archive/`](archive/) — Documentos anteriores a 2026
- [`assets/`](assets/) — Fotografías para el CV (`pin.png` es la de la cabecera)
- [`specs/`](specs/) — Especificaciones de trabajo

## Generar una candidatura

```bash
S=.opencode/skills/cv-generator/scripts

# 1. Crear output/YYYYMMDD-nombreempresa/ con la foto de la cabecera
#    y una copia de sources/curriculum-base.md como curriculum-EMPRESA.md
python3 $S/nueva_candidatura.py "CityPrive"
#    --foto assets/foto2.jpeg   otra imagen
#    --sin-foto                CV sin imagen de cabecera

# 2. Adaptar el texto de curriculum-CITYPRIVE.md a la empresa y escribir
#    carta-CITYPRIVE.md
#    (NO reescribir el CV desde cero: la estructura es la de la plantilla)

# 3. Convertir a ODT + PDF (falla con código 2 si no cabe en 1 página)
python3 $S/md2odt.py output/20260930-cityprive/curriculum-CITYPRIVE.md
python3 $S/md2odt.py output/20260930-cityprive/carta-CITYPRIVE.md
```

La skill `cv-generator` automatiza el proceso completo, incluida la investigación
de la empresa.

## Buscar ofertas a las que presentarse

```bash
S=.opencode/skills/job-search/scripts/ofertas.py

# 1. Buscar (el criterio lo deriva el agente del CV)
python3 $S buscar "IoT" --geo "Valencia, Spain" --dias 21 --minimo 30 \
  --clave "iot,zigbee,embedded,firmware,kubernetes,python" \
  --ubicacion "valencia,valencian" --formato json
python3 $S remoto "backend python" --ubicacion "spain,worldwide,europe"

# 2. Descripción completa de una oferta concreta
python3 $S detalle 4441123182
```

El agente deriva del CV los términos y las palabras clave, puntúa cada oferta y
escribe la lista corta en `ofertas/YYYYMMDD/lista-HHMM.md` con la justificación y
**los requisitos que no cubres**. Ver `ofertas/20261001/` como referencia.

## Perfil

Especialista en IoT, sistemas embebidos e infraestructura. Perfil híbrido: electricidad (FP2) + programación (DAM). Experiencia en arquitectura de soluciones IoT, administración de sistemas Linux y desarrollo full-stack.
