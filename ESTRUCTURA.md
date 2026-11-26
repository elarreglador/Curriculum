# Estructura del repositorio

Repositorio personal de CV y portfolio de David Moreno Bolívar.

## Estructura

- [`sources/`](sources/) — Fuentes de contenido base (editar aquí)
  - `curriculum-github.md` — CV en formato Markdown (GitHub), con badges y secciones desplegables.
  - `curriculum-base.md` — **Plantilla del CV**: contenido base y estructura de
    referencia (cabecera con foto, contacto al final). Es lo que se copia y adapta
    en cada candidatura.
  - `criterios-busqueda.md` — **Criterios permanentes de búsqueda** de ofertas
    (banda de seniority, geografía, remoto). Interno; no va en el CV. El resto
    de España se descarta en presencial/híbrido; el remoto admite cualquier
    sede.
  - `datos-candidatura.md` — **Respuestas permanentes a formularios** (años de
    experiencia, salario, disponibilidad, permiso de trabajo, idioma). La skill
    `auto-apply` no inventa ningún dato que no esté aquí.
- [`templates/`](templates/) — Plantillas de referencia
  - `curriculum-odt.odt` — Plantilla de referencia histórica (no usada por el flujo actual).
- [`output/`](output/) — Candidaturas generadas, una carpeta por empresa con su fecha
  (`output/YYYYMMDD-nombreempresa/`). Cada una lleva el CV y la carta en `.md`, sus
  PDF y `envio-EMPRESA.md` si se intentó el envío. **Ignoradas por git:** permanecen solo en local.
  Ver `output/20260930-edicom/` como referencia de formato del CV.
- [`ofertas/`](ofertas/) — Listas de ofertas por encaje, una carpeta por día
  (`ofertas/YYYYMMDD/lista-HHMM.md`) y el informe diario de envíos
  (`ofertas/YYYYMMDD/postulacion-HHMM.md`). `ofertas/envios.json` es el índice de
  candidaturas ya enviadas. **Ignorado por git:** permanece solo en local.
- [`SENSIBLE/`](SENSIBLE/) — Perfil persistente del navegador y temporales de
  conversión. **Ignorado por git.**
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

```

La skill `cv-generator` automatiza el proceso completo, incluida la investigación
de la empresa.

## Buscar ofertas a las que presentarse

```bash
S=.opencode/skills/job-search/scripts/ofertas.py

# 1. Buscar (banda y geografía en sources/criterios-busqueda.md; términos y
#    palabras clave los deriva el agente del CV)
python3 $S buscar "IoT" --geo "Valencia, Spain" --dias 21 --minimo 30 \
  --seniority "junior,mid" \
  --clave "iot,zigbee,embedded,firmware,kubernetes,python" \
  --ubicacion "valencia,valencian,barcelona,madrid" --formato json
python3 $S remoto "backend python" --ubicacion "spain,worldwide,europe"
# 2. Descripción completa de una oferta concreta
python3 $S detalle 4441123182

# 3. Puntuar ofertas recogidas de la web de empleo de empresas registradas
python3 $S puntuar --ofertas-file ofertas-empresas.json --clave "iot,zigbee,embedded" \
  --ubicacion "valencia,valencian,barcelona,madrid" --dias 14 --formato json
```

El agente lee `sources/criterios-busqueda.md` (banda y geografía), deriva del CV
los términos y las palabras clave, puntúa cada oferta y
escribe la lista corta en `ofertas/YYYYMMDD/lista-HHMM.md` con la justificación y
**los requisitos que no cubres**. Ver `ofertas/20261001/` como referencia.

## Presentarse de forma automática

```bash
A=.opencode/skills/auto-apply/scripts

# Lanzador diario (el crontab no se instala desde el repositorio)
$A/postular-diario.sh             # envío real
$A/postular-diario.sh --dry-run   # prueba sin pulsar «Enviar»

# Ambos avisan por Telegram al inicio y al fin; en --dry-run van marcados como tal.
# Para ver el mensaje sin enviarlo:
python3 $A/notificar_telegram.py lote --estado fin --fecha 2026-11-25T09:42:11+01:00 \
  --modo normal --duracion 2530 --enviadas 15 --log ofertas/20261125/postulacion-0900.log --sonda

# Gestión del índice de envíos
python3 $A/registrar_envio.py contar
python3 $A/registrar_envio.py registrar --empresa "X" --puesto "Y" \
  --url "https://..." --estado bloqueada --directorio output/YYYYMMDD-x
```

El estado `enviada` solo lo escribe la skill después de ver la pantalla de
confirmación del formulario; no se usa en ejemplos manuales.

La skill `auto-apply` (spec 08) toma las ofertas de los informes de `job-search`
y `company-jobs`, detecta los desajustes de filtro del formulario (no excluyentes)
y prioriza al menos 15 candidaturas por ejecución, ordenadas por encaje con pisos
55/45/35/25 y búsqueda ampliada a puestos de informática y de técnico si faltan
ofertas. No hay tope diario. Toda respuesta procede de `sources/datos-candidatura.md`;
lo preguntado, lo entregado y los desajustes se conservan en
`output/YYYYMMDD-nombreempresa/envio-EMPRESA.md`.

## Perfil

Especialista en IoT, sistemas embebidos e infraestructura. Perfil híbrido: electricidad (FP2) + programación (DAM). Experiencia en arquitectura de soluciones IoT, administración de sistemas Linux y desarrollo full-stack.
