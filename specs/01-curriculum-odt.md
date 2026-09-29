# SPEC 01 — Currículum Vitae en formato ODT

> **Estado:** Aprobado

> **Depende de:** Ninguna

> **Fecha:** 2026-09-29

> **Objetivo:** Crear un currículum vitae de una página en formato .odt que posicione a David Moreno Bolívar como IoT/Embedded Engineer + Full-stack + Hardware, enfocado a startups tecnológicas.

---

## Por qué existe esta especificación

El CV actual en `curriculum.md` está diseñado para GitHub (con badges visuales, secciones desplegables, y extensión web). Para buscar trabajo en startups tecnológicas se necesita un documento editable de una página, en formato .odt, que pueda exportarse a PDF y que comunique de inmediato el perfil híbrido electricidad + programación.

---

## Alcance

**En:**

- **Redacta el contenido del CV en castellano — `curriculum.odt` — documento editable de una página**
  - **Cabecera con datos de contacto — `curriculum.odt` — nombre, título profesional, correo, teléfono, ubicación, LinkedIn, GitHub**
  - **Espacio reservado para fotografía — `curriculum.odt` — cuadro de 3x3 cm en cabecera, vacío, listo para insertar imagen**
  - **Perfil profesional de 3-4 líneas — `curriculum.odt` — síntesis del perfil híbrido FP2 + DAM**
  - **Experiencia laboral en Living Properties S.L. — `curriculum.odt` — dos períodos (CTO + FCT) con bullets de logros**
  - **Párrafo de experiencia anterior — `curriculum.odt` — 1 párrafo breve: Apple, negocio propio, electricidad**
  - **Proyecto destacado: Control de Acceso IoT — `curriculum.odt` — arquitectura ESP32-C6 → Zigbee → MQTT → Node-RED → K8s**
  - **Sección de tecnologías en texto plano — `curriculum.odt` — IoT, infraestructura, desarrollo, herramientas**
  - **Sección de formación — `curriculum.odt` — DAM, FP2, cursos relevantes**

**Fuera del alcance (para futuras especificaciones):**

- Exportación a PDF (se hará manualmente desde LibreOffice)
- CV en inglés (posible versión futura)
- Carta de presentación
- Diseño gráfico avanzado (colores, iconos, layouts complejos)
- Actualización del perfil de LinkedIn
- Actualización del repositorio GitHub

---

## Modelo de datos

Esta especificación no introduce nuevas estructuras de datos. El contenido se redacta directamente en el documento `.odt`.

---

## Plan de implementación

1. Redactar el contenido completo del CV en Markdown como base de referencia.
2. Verificar que `pandoc` está disponible en el sistema (`pandoc --version`).
3. Generar el archivo `.odt` usando `pandoc` desde Markdown: `pandoc curriculum.md -o curriculum.odt`.
4. Si `pandoc` no está disponible, instalarlo o usar `libreoffice --headless --convert-to odt curriculum.md`.
5. Verificar que el documento abre correctamente y cabe en 1 página.
6. Revisar que todos los datos de contacto son correctos.

---

## Criterios de aceptación

- [ ] El archivo `curriculum.odt` existe en `/home/elarreglador/Documentos/trabajo/`.
- [ ] El documento cabe en 1 página.
- [ ] El documento incluye: cabecera con contacto, espacio para foto, perfil profesional, experiencia Living Properties (2 períodos), párrafo experiencia anterior, proyecto destacado IoT, tecnologías, formación.
- [ ] El contenido está en castellano.
- [ ] No contiene badges visuales ni imágenes de GitHub.
- [ ] El formato es texto plano profesional con negritas para títulos.
- [ ] Los datos de contacto son: `elarreglador@protonmail.com`, `651 73 77 65`, Valencia.
- [ ] Incluye enlaces a LinkedIn (`https://www.linkedin.com/in/elarreglador/`) y GitHub (`https://github.com/elarreglador/Curriculum`).

---

## Decisiones

- **Sí:** Formato .odt (OpenDocument Text). Editable en LibreOffice Writer, compatible con Google Docs, exportable a PDF.
- **No:** Google Docs directo. Los badges de GitHub no funcionan bien y el formato es menos portable.
- **Sí:** Una página. Las startups prefieren CVs concisos y directos.
- **No:** Dos páginas. El contenido relevante cabe en una página si es conciso.
- **Sí:** Texto plano profesional. Negritas para títulos, sin colores ni diseños complejos.
- **No:** Diseño gráfico avanzado. El contenido es más importante que la forma para este perfil.
- **Sí:** Proyecto destacado separado. El control de acceso IoT es el diferenciador clave.
- **No:** Incluir toda la experiencia anterior. Solo un párrafo breve para no perder espacio.
- **Sí:** Espacio para fotografía. En España es común y las startups suelen pedirlo.
- **No:** Incluir la foto. Solo el espacio reservado, el usuario la insertará.
- **Sí:** Castellano. El mercado objetivo es España/Valencia.
- **No:** Inglés. Aunque su nivel es suficiente, el CV se dirige al mercado local.

---

## Riesgos

| Riesgo | Mitigación |
| ------------------------------------- | --------------------------------------------------------------------------- |
| El contenido no cabe en 1 página | Redactar de forma concisa, usar bullets cortos, eliminar detalles irrelevantes |
| `pandoc` no está instalado | Instalar con `sudo apt install pandoc` o usar LibreOffice como alternativa |
| El formato .odt no abre correctamente | Verificar con LibreOffice Writer, ajustar si es necesario |

---

## Lo que **no** está en esta especificación

- Exportación a PDF (se hará manualmente desde LibreOffice).
- CV en inglés.
- Carta de presentación.
- Diseño gráfico avanzado (colores, iconos, layouts complejos).
- Actualización del perfil de LinkedIn.
- Actualización del repositorio GitHub.
