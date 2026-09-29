# Curriculum — David Moreno Bolívar

Repositorio personal de CV y portfolio.

## Estructura

- [`sources/`](sources/) — Fuentes de contenido base (editar aquí)
  - `curriculum-github.md` — CV en formato Markdown (GitHub), con badges y secciones desplegables.
  - `curriculum-base.md` — CV 1 página base en Markdown (para generar ODT).
- [`templates/`](templates/) — Plantillas de referencia
  - `curriculum-odt.odt` — Última versión ODT generada como referencia.
- [`output/`](output/) — CVs generados por empresa (ignorado por git)
- [`archive/`](archive/) — Documentos anteriores a 2026 (referencia, ignorado por git)
- [`assets/`](assets/) — Fotografías para el CV
- [`specs/`](specs/) — Especificaciones de trabajo

## Generar ODT por empresa

```bash
cp sources/curriculum-base.md output/curriculum-NOMBREEMPRESA.md
# editar output/curriculum-NOMBREEMPRESA.md
libreoffice --headless --convert-to odt output/curriculum-NOMBREEMPRESA.md --outdir output/
```

## Perfil

Especialista en IoT, sistemas embebidos e infraestructura. Perfil híbrido: electricidad (FP2) + programación (DAM). Experiencia en arquitectura de soluciones IoT, administración de sistemas Linux y desarrollo full-stack.
