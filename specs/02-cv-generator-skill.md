# SPEC 02 — Skill local: Generador de CV + Carta de Presentación

> **Estado:** Aprobado

> **Depende de:** 01-curriculum-odt

> **Fecha:** 2026-09-29

> **Objetivo:** Crear una skill local que, dado el nombre de una empresa y detalles del puesto, genere automáticamente un CV adaptado y una carta de presentación personalizada, ambos en formato .md y .odt.

---

## Por qué existe esta especificación

El usuario aplicará a múltiples empresas y necesita generar CVs y cartas de presentación adaptados a cada una. Hacerlo manualmente es repetitivo y propenso a errores. Una skill local que automatice este proceso garantiza consistencia y ahorra tiempo.

---

## Alcance

**En:**

- **Skill local en `.opencode/skills/cv-generator/SKILL.md`**
  - Recibe nombre de empresa + detalles del puesto (o pregunta al usuario si no se los dan)
  - Busca información de la empresa en web y confirma con el usuario si es la empresa correcta (no homónima)
  - Busca información de la oferta (si hay link, intenta acceder; si no, usa MCP disponible)
  - Genera `output/curriculum-EMPRESA.md` adaptado (énfasis en lo relevante para esa empresa)
  - Genera `output/curriculum-EMPRESA.odt` desde el markdown
  - Genera `output/carta-EMPRESA.md` (tono formal, información del usuario + empresa)
  - Genera `output/carta-EMPRESA.odt` desde el markdown

**Fuera del alcance:**

- Envío automático de correos
- Generación de CVs en otros formatos (PDF, DOCX)
- Almacenamiento de datos de empresas en base de datos
- Traducción automática a otros idiomas

---

## Modelo de datos

La skill no introduce estructuras de datos persistentes. Toda la información se obtiene en tiempo de ejecución:

- **Entrada:** nombre de empresa, detalles del puesto (opcional), link de oferta (opcional)
- **Intermedia:** información de la empresa (web), información de la oferta (web/MCP)
- **Salida:** 4 archivos en un directorio con este nombre (fecha actual + nombre de empresa): YYYYMMDD-nombreEmpresa

---

## Plan de implementación

1. Crear directorio `.opencode/skills/cv-generator/`
2. Crear `SKILL.md` con las instrucciones de la skill
3. Definir el flujo de interacción: pregunta empresa → busca web → confirma con usuario → busca oferta → genera archivos
4. Implementar la lógica de búsqueda de información de empresa (websearch)
5. Implementar la lógica de búsqueda de oferta (webfetch o MCP)
6. Implementar la generación de CV adaptado desde `sources/curriculum-base.md`
7. Implementar la generación de carta de presentación (tono formal)
8. Implementar la conversión a ODT vía LibreOffice
9. Probar la skill con una empresa de ejemplo

---

## Criterios de aceptación

- [ ] La skill existe en `.opencode/skills/cv-generator/SKILL.md`
- [ ] La skill pregunta el nombre de empresa y detalles del puesto si no se los dan
- [ ] La skill busca información de la empresa en web
- [ ] La skill confirma con el usuario si la información encontrada corresponde a la empresa correcta
- [ ] La skill busca información de la oferta (link o MCP)
- [ ] La skill genera `output/curriculum-EMPRESA.md` adaptado
- [ ] La skill genera `output/curriculum-EMPRESA.odt`
- [ ] La skill genera `output/carta-EMPRESA.md` con tono formal
- [ ] La skill genera `output/carta-EMPRESA.odt`
- [ ] Los archivos se guardan en `output/` (gitignored)

---

## Decisiones

- **Sí:** Skill local (`.opencode/skills/`). Solo disponible en este repo.
- **No:** Skill global. No es necesario en otros proyectos.
- **Sí:** Búsqueda web de empresa. Necesario para personalizar el CV y la carta.
- **Sí:** Confirmación con el usuario. Evita errores con empresas homónimas.
- **Sí:** Tono formal en la carta. Estándar en el mercado español.
- **Sí:** Generar 4 archivos (.md + .odt para CV y carta). El .md es editable, el .odt es el entregable.
- **No:** Envío automático. El usuario envía manualmente.

---

## Riesgos

| Riesgo | Mitigación |
| ------------------------------------- | --------------------------------------------------------------------------- |
| Empresa homónima | Confirmación explícita con el usuario antes de generar |
| Link de oferta no accesible | Usar MCP disponible o pedir datos manualmente |
| Información de empresa desactualizada | Usar websearch con fecha actual |
| ODT no cabe en 1 página | Ajustar contenido, usar formato compacto |

---

## Lo que **no** está en esta especificación

- Envío automático de correos.
- Generación de CVs en otros formatos.
- Almacenamiento de datos de empresas.
- Traducción automática.
