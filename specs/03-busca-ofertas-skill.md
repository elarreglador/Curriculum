# SPEC 03 — Skill local: Buscador de ofertas por encaje

> **Estado:** Aprobado

> **Depende de:** 02-cv-generator-skill

> **Fecha:** 2026-10-01

> **Objetivo:** Crear una skill local que busque ofertas de empleo en las que el perfil descrito en `sources/curriculum-base.md` encaje, las puntúe, y deje una lista corta justificada en `ofertas/YYYYMMDD/` para que el usuario decida a qué empresas presentar su candidatura.

---

## Por qué existe esta especificación

Hasta ahora el flujo es reactivo: el usuario llega a una empresa por un anuncio suelto y entonces se genera el CV y la carta (`cv-generator`). Lo que falta es el paso anterior —**descubrir** ofertas, que es donde más esfuerzo se pierde hoy.

El problema no es encontrar anuncios: es distinguir los que encajan de los que no. Con el perfil actual (backend, cloud e IoT, con Electrical de FP2), una búsqueda de `IoT developer` en España devuelve tanto «Desarrollador de Firmware para Dispositivos IoT» —encaje directo— como «Senior/Principal Cloud Architect» o ofertas redactadas en alemán de empresas filtradas. Sin un filtro explícito, el volumen ahoga a la señal.

La skill debe devolver **pocas ofertas y bien justificadas**, no un volcado de resultados.

---

## Alcance

**En:**

- **Skill local en `.opencode/skills/job-search/SKILL.md`**
  - Deriva del CV los criterios de búsqueda (roles, palabras clave positivas y negativas, geografía, banda de seniority)
  - Interroga fuentes públicas de ofertas sin login ni clave
  - Filtra por frescura, geografía, idioma, seniority y empresas de selección
  - Puntúa el encaje técnico de forma reproducible
  - Devuelve la lista corta en `ofertas/YYYYMMDD/` con justificación, requisitos que no se cubren y descartes con su motivo
- **Script en `.opencode/skills/job-search/scripts/ofertas.py`**
  - Subcomando `buscar`: búsqueda paginada, parseo, deduplicación, filtros y puntuación
  - Subcomando `remoto`: agregadores de empleo remoto
  - Subcomando `detalle`: descripción completa de una oferta concreta

**Fuera del alcance:**

- Envío o relleno automático de candidaturas (se posta a mano)
- Publicación de alertas o suscripción a newsletters
- Carteo de suitability con ofertas a las que el usuario ya se presentó
- Traducción de ofertas
- Base de datos histórica de ofertas (cada búsqueda es una foto del momento)

---

## Modelo de datos

La skill no introduce estructuras persistentes más allá del informe de la búsqueda.

- **Entrada:** criterios derivados del CV, geografía objetivo (Valencia + remoto Europa), antigüedad máxima
- **Intermedia:** respuestas de las APIs de ofertas, cacheadas en `cache/` (TTL corto)
- **Salida:** `ofertas/YYYYMMDD/lista-HHMM.md` con los criterios usados, la tabla de ofertas, el detalle justificado de las mejores y los descartess con motivo

Las ofertas se normalizan a un **esquema único** entre fuentes, con el siguiente registro:

| Campo | Contenido |
|---|---|
| `id` | Identificador de la oferta en su fuente |
| `titulo` | Puesto |
| `empresa` | Nombre comercial |
| `ubicacion` | Localización publicada |
| `remoto` | Booleano |
| `fecha` | Fecha de publicación |
| `antiguedad_dias` | Días transcurridos |
| `url` | Enlace a la oferta original |
| `idioma` | Idioma inferido de la descripción (`es`, `en`, `de`, …) |
| `seniority` | Nivel inferido del título (`junior`, `mid`, `senior`, `staff`) |
| `consultora` | Booleano, heurística de empresa de selección |
| `puntuacion` | Encaje técnico 0-100 |
| `fuente` | Origen del dato |

---

## Plan de implementación

1. Crear `specs/03-busca-ofertas-skill.md` (este documento).
2. Crear el directorio `.opencode/skills/job-search/` con su `.gitignore`.
3. Implementar `scripts/ofertas.py`: cliente HTTP con límite de ritmo, caché con TTL corto, parseo de las fuentes, normalización a esquema único, filtros y puntuación.
4. Escribir `SKILL.md` con el flujo: derivar criterios del CV → buscar → puntuar → qualifier → escribir informe.
5. Probar con tres consultas de humo (Valencia, remoto-UE, banda de seniority) y con el caso conocido de ofertas en español mal filtradas.
6. Ejecutar una búsqueda real completa y dejar `ofertas/YYYYMMDD/`.
7. Actualizar `AGENTS.md` y `README.md`.

---

## Criterios de aceptación

- [x] La skill existe en `.opencode/skills/job-search/SKILL.md`
- [x] El script devuelve ofertas con el esquema único, sea cual sea la fuente
- [x] La búsqueda filtra por geografía, antigüedad, idioma y seniority
- [x] La puntuación técnica es reproducible con los mismos criterios
- [x] Los criterios usados quedan escritos en el informe, para poder reconstruir el resultado
- [x] Las empresas de selección se detectan y se pueden descartar
- [x] El informe distingue lo que el CV cubre y lo que no cubre
- [x] Los descartes quedan anotados con su motivo
- [x] El script cachea las respuestas y limita el ritmo de peticiones
- [x] Una búsqueda real produce `ofertas/YYYYMMDD/lista-HHMM.md`

---

## Decisiones

- **Sí:** skill local (`.opencode/skills/`), con el nombre `job-search` en inglés como las existentes.
- **Sí:** el criterio de búsqueda lo deriva el agente del CV **en cada ejecución**, sin fichero de perfil propio. Es lo que pidió el usuario: el criterio no se queda congelado en un fichero que se queda viejo.
  - **Consecuencia asumida:** el resultado solo es reconstruible si los criterios usados quedan escritos en el informe. De ahí la cabecera obligatoria. Registrar el criterio, no configurarlo.
- **Sí:** salida en `ofertas/YYYYMMDD/`, versionada en git, como el historial de lo que había disponible cada día.
  - `YYYYMMDD` es la fecha de la búsqueda. Dentro, `lista-HHMM.md` permite varias búsquedas el mismo día.
- **Sí:** puntuación en dos capas —técnica y determinista en el script, argumental y cualitativa en el agente. Un filtro de palabras no sabe que un puesto de firmware encaja y uno de cloud architect no, aunque ambos contengan las mismas palabras.
- **No:** script que derive el perfil del CV. Esa parte es criterio, y el criterio es del agente. El script recibe los criterios como banderas.
- **No:** relleno automático de candidaturas. La búsqueda produce material; el envío es manual.

---

## Riesgos

| Riesgo | Mitigación |
| --- | --- |
| La fuente cambia el markup o estrangula el ritmo | Parseo aislado en una función por fuente; `--no-cache`; agregadores remotos y búsqueda web como plan B |
| El endpoint consultado es unofficial, aunque público y anónimo | Solo lectura, ritmo limitado, caché, y enlace siempre a la oferta original. No se automatiza la candidatura |
| Sesgo de volumen: 40 ofertas y 3 buenas | Filtros de consultoras, idioma, seniority y frescura antes de mostrar nada |
| Criterio no reproducible entre ejecuciones | Los criterios usados se escriben en la cabecera del informe |
| Ofertas que caducan entre la búsqueda y la candidatura | `fecha` y `antiguedad_dias` en la tabla; el informe avisa de la antigüedad |

---

## Lo que **no** está en esta especificación

- Relleno o envío automático de candidaturas.
- Alertas y suscripciones a boletines de empleo.
- Seguimiento histórico de qué ofertas se publicaron cada día más allá del informe versionado.
- Traducción de las ofertas.
- Normalización de objetivos de la búsqueda en un fichero de perfil permanente.