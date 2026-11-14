# SPEC 06 — Estimación de posibilidades de obtener el puesto y ordenación por acceso

> **Estado:** Aprobado

> **Depende de:** 03-busca-ofertas-skill

> **Enmienda a:** 03-busca-ofertas-skill (eliminación de convocatorias de empleo público)

> **Fecha:** 2026-11-08

> **Objetivo:** Añadir al informe `ofertas/YYYYMMDD/lista-HHMM.md` una estimación de las posibilidades reales de obtener el puesto, cambiar la ordenación a dos etapas (encaje mínimo de 55 + posibilidad de acceso ordena), y eliminar las fuentes de empleo público (UPV, UV, GVA, CSIC) para no consumir CPU ni tokens en ellas.

---

## Por qué existe esta especificación

La lista actual ordena por encaje técnico, que mide afinidad pero no probabilidad real de contratación: una oferta con encaje alto puede ser inaccesible (senior, idioma, certificaciones) y una con encaje medio puede ser la que realmente se consigue. Además, las convocatorias de empleo público (UPV, UV, GVA, CSIC) consumen tiempo y tokens en hidratación y puntuación sin aportar vacantes privadas reales, y el usuario ha decidido descartarlas del flujo.

---

## Alcance

**En:**

- Plantilla de la tabla "Lista corta" en `SKILL.md` (Paso 4): nueva columna `Posibilidades` (0-100 o `No consta`).
- Regla en `SKILL.md` (Paso 3): el agente estima `Posibilidades` al cualificar; para convocatorias públicas (si existieran) se escribiría `N/A`, pero tras esta spec no se generan.
- Cambio de ordenación en `SKILL.md` (Paso 4): dos etapas — encaje mínimo de 55 (filtro) + `Posibilidades` ordena (descendente). Cabecera del informe: añadir el umbral de encaje mínimo a los criterios usados.
- Eliminación de fuentes públicas:
  - `SKILL.md`: borrar la sección "Convocatorias (empleo público)", el subcomando `publico` de "Comandos", la fila de fuentes públicas en "Fuentes", y el apartado de convocatorias en "Paso 2" (quedan 4 pasadas: Valencia, Barcelona, Madrid, Remoto).
  - `ofertas.py`: eliminar el subcomando `publico` y la lógica asociada (hidratación de fichas, reglas de convocatoria).
  - `AGENTS.md` y `README.md`: actualizar el estándar (eliminar referencias a `publico`, `--fuentes`, UPV/UV/GVA/CSIC).
  - `sources/criterios-busqueda.md`: eliminar la mención a convocatorias públicas y a la antigüedad de 14 días para ellas.

**Fuera del alcance:**

- Cambios en el esquema único de `ofertas.py` (no se añade campo `posibilidades`).
- Estimación determinista en el script (sigue siendo cualitativa del agente).
- Generación de candidaturas (skill `cv-generator`).
- Envío o relleno automático de candidaturas.

---

## Modelo de datos

La skill no introduce estructuras persistentes nuevas. El campo nuevo es conceptual y solo vive en el informe:

| Campo (informe) | Contenido |
|---|---|
| `posibilidades` | Estimación 0-100 de las posibilidades reales de obtener el puesto, o `No consta` si no hay base para estimar. Para convocatorias públicas (no generadas tras esta spec) se escribiría `N/A`. |

No se añade al esquema único del script (`id`, `titulo`, `empresa`, …, `puntuacion`). La `puntuacion` (encaje técnico) sigue siendo la señal determinista del script; `posibilidades` es el juicio cualitativo del agente.

---

## Plan de implementación

1. Crear `specs/06-estimacion-posibilidades-ofertas.md` (este documento).
2. Editar `.opencode/skills/job-search/SKILL.md`:
   - Paso 3: añadir la estimación de `Posibilidades` al cualificar.
   - Paso 4: actualizar la plantilla de la tabla (columna `Posibilidades`), la ordenación por `Posibilidades` descendente con encaje mínimo 55, y la cabecera con el umbral.
   - Eliminar la sección "Convocatorias (empleo público)", el subcomando `publico` y la fila de fuentes públicas.
   - Ajustar "Paso 2" a 4 pasadas (sin convocatorias).
3. Editar `.opencode/skills/job-search/scripts/ofertas.py`: eliminar el subcomando `publico` y su lógica.
4. Actualizar `AGENTS.md` y `README.md` (eliminar referencias a convocatorias públicas).
5. Actualizar `sources/criterios-busqueda.md` (eliminar la línea de convocatorias públicas y la antigüedad de 14 días para ellas).

---

## Criterios de aceptación

- [x] La spec existe en `specs/06-estimacion-posibilidades-ofertas.md`
- [x] La tabla "Lista corta" del informe incluye la columna `Posibilidades` (0-100 o `No consta`)
- [x] Solo pasan a la lista corta las ofertas privadas con encaje ≥ 55
- [x] El orden es por `Posibilidades` descendente
- [x] No se generan convocatorias públicas (UPV, UV, GVA, CSIC)
- [x] `SKILL.md` documenta el cálculo (Paso 3), el umbral 55 (Paso 4) y la eliminación de públicos
- [x] `ofertas.py` ya no contiene el subcomando `publico`
- [x] `AGENTS.md` y `README.md` no referencian convocatorias públicas
- [x] No se modifican el esquema único ni se añaden campos al script

---

## Decisiones

- **Sí:** añadir la columna `Posibilidades` como juicio cualitativo del agente (Paso 3), no como señal del script. Consistente con el principio de diseño: la puntuación ordena, el argumento decide.
- **Sí:** cambiar la ordenación a dos etapas — encaje mínimo de 55 (filtro) + `Posibilidades` ordena (descendente). El encaje deja de ordenar y pasa a filtrar.
- **Sí:** umbral de encaje mínimo fijado en **55 puntos**.
- **Sí:** eliminar las fuentes de empleo público (UPV, UV, GVA, CSIC) del flujo: no se ejecuta el subcomando `publico`, no se hidratan fichas públicas, no se consumen tokens en ellas.
- **Sí:** para convocatorias públicas (no generadas tras esta spec) la columna se rellenaría con `N/A`; la regla se mantiene por si se reintroducen en el futuro.
- **No:** no se añade un campo `posibilidades` al esquema único del script ni una señal determinista. La estimación es del agente.
- **No:** no se usa `Posibilidades` para filtrar, solo para ordenar dentro de los que superan el umbral.
- **No:** no se modifican los criterios permanentes de `sources/criterios-busqueda.md` salvo la eliminación de la línea de convocatorias públicas.

---

## Riesgos

| Riesgo | Mitigación |
|---|---|
| Subjetividad del agente en la estimación | La estimación se justifica en el argumento del detalle; se escribe `No consta` si no hay base |
| Confusión entre encaje técnico y posibilidades | Columnas separadas y regla explícita de que el encaje filtra (≥55) y la probabilidad ordena |
| Pérdida de convocatorias públicas | Decisión explícita del usuario; se documenta en la spec y en la enmienda a la spec 03 |
| Inconsistencia entre búsquedas | Los criterios usados (incluido el umbral 55) se escriben en la cabecera del informe |
| Lista corta demasiado corta | El umbral 55 es un compromiso; si queda vacía, se baja el umbral y se anota en la cabecera |

---

## Lo que **no** está en esta especificación

- Relleno o envío automático de candidaturas.
- Alertas y suscripciones a boletines de empleo.
- Traducción de las ofertas.
- Reintroducción de convocatorias públicas (fuera de alcance tras esta spec).
- Normalización de objetivos de la búsqueda en un fichero de perfil permanente (ya fijado en `sources/criterios-busqueda.md`).