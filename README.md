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

## Perfil

Especialista en IoT, sistemas embebidos e infraestructura. Perfil híbrido: electricidad (FP2) + programación (DAM). Experiencia en arquitectura de soluciones IoT, administración de sistemas Linux y desarrollo full-stack.
