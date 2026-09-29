# Curriculum — David Moreno Bolívar

Repositorio personal de CV y portfolio.

## Estructura

- [`sources/`](sources/) — Fuentes de contenido base (editar aquí)
  - `curriculum-github.md` — CV en formato Markdown (GitHub), con badges y secciones desplegables.
  - `curriculum-base.md` — CV 1 página base en Markdown (para generar ODT).
- [`templates/`](templates/) — Plantillas de referencia
  - `curriculum-odt.odt` — Última versión ODT generada como referencia.
- [`output/`](output/) — Candidaturas generadas, una carpeta por empresa con su fecha
  (`output/YYYYMMDD-nombreempresa/`). Cada una lleva el CV y la carta en `.md`, `.odt` y `.pdf`.
  Ver `output/20260929-wecity/` como referencia de estilo.
- [`archive/`](archive/) — Documentos anteriores a 2026
- [`assets/`](assets/) — Fotografías para el CV
- [`specs/`](specs/) — Especificaciones de trabajo

## Generar una candidatura

```bash
S=.opencode/skills/cv-generator/scripts

# 1. Crear el directorio output/YYYYMMDD-nombreempresa/
python3 $S/nueva_candidatura.py "CityPrive"

# 2. Escribir el CV y la carta a partir de sources/curriculum-base.md
#    en output/20260929-cityprive/curriculum-CITYPRIVE.md y carta-CITYPRIVE.md

# 3. Convertir a ODT + PDF (falla con código 2 si no cabe en 1 página)
python3 $S/md2odt.py output/20260929-cityprive/curriculum-CITYPRIVE.md
python3 $S/md2odt.py output/20260929-cityprive/carta-CITYPRIVE.md
```

La skill `cv-generator` automatiza el proceso completo, incluida la investigación
de la empresa.

## Perfil

Especialista en IoT, sistemas embebidos e infraestructura. Perfil híbrido: electricidad (FP2) + programación (DAM). Experiencia en arquitectura de soluciones IoT, administración de sistemas Linux y desarrollo full-stack.
