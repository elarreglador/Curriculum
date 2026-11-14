# SPEC 07 — Skill local: Revisión de ofertas en webs de empresas registradas

> **Estado:** Aprobado

> **Depende de:** 03-busca-ofertas-skill, 05-salidas-fuera-de-git

> **Fecha:** 2026-11-14

> **Objetivo:** Crear una skill local (`company-jobs`) cuyo único origen sea `ofertas/empresas.json`, que revise las webs de empleo de las empresas registradas que no se hayan visto en los últimos 15 días (o sin fecha de revisión), complete los campos `web` y `url_empleo` cuando falten, elimine las que no tengan apartado de vacantes, registre en cada empresa un campo `instrucciones_agente` con la forma más eficiente de revisarla en el futuro, y genere un informe por lote en `ofertas/YYYYMMDD/empresas-HHMM.md`.

---

## Por qué existe esta especificación

El Paso 2b de `job-search` ya revisa las empresas registradas en `ofertas/empresas.json`, pero lo hace de forma inline, mezclado con la búsqueda de LinkedIn y remotos. Eso dificulta mantener la lógica, probarla y reutilizarla. Extraerla en una skill propia con origen exclusivo en `empresas.json` permite:

- Revisar las webs de empleo de las empresas registradas **sin depender** de una búsqueda de LinkedIn previa.
- Concentrar en un único sitio la política de completado de `web`/`url_empleo`, la eliminación por falta de apartado de vacantes y la anotación de `instrucciones_agente`.
- Generar un informe dedicado (`empresas-HHMM.md`) que se puede consultar de forma independiente.

---

## Alcance

**En:**
- **Skill local en `.opencode/skills/company-jobs/SKILL.md`**
  - Origen exclusivo: `ofertas/empresas.json` (gestionado por `company-research/scripts/empresas.py`).
  - Selección del lote: empresas con `ultima_revision` nula o anterior a hoy − 15 días.
  - Completado de `web` y `url_empleo` cuando falten (delegando en `company-research` y usando `webfetch`).
  - Revisión de `url_empleo` con `webfetch`: extracción de ofertas visibles.
  - Anotación de `ultima_revision`, `ultimas_ofertas_vistas` e `instrucciones_agente` en `empresas.json`.
  - Eliminación de empresas sin `url_empleo` tras dos intentos fallidos.
  - Puntuación del encaje de las ofertas encontradas con `ofertas.py puntuar` (derivando criterios del CV).
  - Generación del informe `ofertas/YYYYMMDD/empresas-HHMM.md` al completar el lote.
- **Campo nuevo en `empresas.json`**: `instrucciones_agente` (string o `null`).
- **Constante configurable** `WEBS_POR_EJECUCION = 10` al principio del `SKILL.md`, editable a mano.
- **Actualización de `job-search`**: el Paso 2b delega en `company-jobs`.

**Fuera del alcance:**
- Script propio para `company-jobs` (se reutilizan `empresas.py` y `ofertas.py`).
- Envío o relleno automático de candidaturas.
- Seguimiento histórico más allá del informe local.
- Traducción de ofertas.
- Normalización de objetivos de la búsqueda en un fichero de perfil permanente (sigue en `sources/criterios-busqueda.md`).

---

## Modelo de datos

### Campo nuevo en `empresas.json`

| Campo | Tipo | Descripción |
|---|---|---|
| `instrucciones_agente` | string o null | Cómo revisar las vacantes de esa web de la forma más eficiente (URL exacta, API/JSON disponible, selectores CSS, paginación, filtros recomendados, avisos). `null` si aún no se ha revisado. |

El resto de campos no cambia. La política de intentos ya existente se mantiene: se infiere de `ultima_revision` (primer fallo → pendiente; segundo fallo → eliminación).

### Esquema de oferta (igual que `job-search`)

| Campo | Contenido |
|---|---|
| `titulo` | Puesto |
| `empresa` | Nombre comercial |
| `ubicacion` | Localización publicada |
| `remoto` | Booleano |
| `fecha` | Fecha de publicación |
| `antiguedad_dias` | Días transcurridos |
| `url` | Enlace a la oferta original |
| `idioma` | Idioma inferido de la descripción |
| `seniority` | Nivel inferido del título |
| `puntuacion` | Encaje técnico 0-100 |
| `fuente` | `empresa` |

---

## Plan de implementación

1. Crear `specs/07-company-jobs-skill.md` (este documento).
2. Crear el directorio `.opencode/skills/company-jobs/` con su `.gitignore`.
3. Escribir `.opencode/skills/company-jobs/SKILL.md` con la constante `WEBS_POR_EJECUCION = 10` al principio y el flujo completo.
4. Actualizar `.opencode/skills/job-search/SKILL.md` (Paso 2b) para delegar en `company-jobs`.
5. Documentar el campo `instrucciones_agente` en `company-research/SKILL.md` (sección de registro de empresas).
6. Actualizar `AGENTS.md` con la nueva skill.
7. Probar con un lote real y verificar que se genera `ofertas/YYYYMMDD/empresas-HHMM.md`.

---

## Criterios de aceptación

- [x] La skill existe en `.opencode/skills/company-jobs/SKILL.md`
- [x] La constante `WEBS_POR_EJECUCION = 10` aparece una sola vez, al principio del documento
- [x] El flujo selecciona el lote, completa campos, revisa webs, anota y genera informe
- [x] El campo `instrucciones_agente` se anota en `empresas.json` para cada empresa revisada
- [x] Las empresas sin `url_empleo` se eliminan tras dos intentos fallidos y se anotan en "Eliminadas"
- [x] El informe se genera en `ofertas/YYYYMMDD/empresas-HHMM.md`
- [x] `job-search` Paso 2b delega en `company-jobs`
- [x] `company-research` documenta el campo `instrucciones_agente`
- [x] `AGENTS.md` actualizado

---

## Decisiones

- **Sí:** skill local (`.opencode/skills/`), con el nombre `company-jobs` en inglés como las existentes.
- **Sí:** origen exclusivo en `ofertas/empresas.json`. No se consulta LinkedIn ni agregadores remotos desde esta skill.
- **Sí:** puntuación de encaje con los mismos criterios que `job-search` (derivar del CV + `ofertas.py puntuar`).
- **Sí:** el valor `WEBS_POR_EJECUCION` se indica una sola vez al principio del `SKILL.md`, editable a mano. Por defecto 10.
- **Sí:** delegación desde `job-search` Paso 2b para evitar duplicar lógica.
- **Sí:** campo `instrucciones_agente` en `empresas.json` para facilitar revisiones futuras y ahorrar tokens.
- **No:** script propio. Se reutilizan `empresas.py` y `ofertas.py`.
- **No:** envío o relleno automático de candidaturas.

---

## Riesgos

| Riesgo | Mitigación |
|---|---|
| `instrucciones_agente` desactualizado si la web cambia | Se regenera en cada revisión; si falla el fetch, se anota el error y se conserva el anterior |
| Lote demasiado grande para una ejecución | Constante `WEBS_POR_EJECUCION` editable; por defecto 10 |
| Empresas con `url_empleo` que ya no funciona | Segundo fallo → eliminación; se anota en "Eliminadas" |
| Duplicar lógica con `job-search` | Delegación explícita en Paso 2b |
| Informes no reproducibles | Cabecera con criterios usados, igual que `job-search` |

---

## Lo que **no** está en esta especificación

- Script propio para `company-jobs`.
- Envío o relleno automático de candidaturas.
- Alertas y suscripciones a boletines de empleo.
- Seguimiento histórico de ofertas más allá del informe local.
- Traducción de las ofertas.
- Normalización de objetivos de la búsqueda en un fichero de perfil permanente.