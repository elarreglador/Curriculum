# SPEC 05 — Salidas locales fuera de git

> **Estado:** Aprobado
>
> **Depende de:** 04-candidaturas-solo-markdown
>
> **Sustituye:** decisión de versionado de `output/` y `ofertas/` en specs 02, 03 y 04
>
> **Fecha:** 2026-10-23
>
> **Objetivo:** Mantener `output/` y `ofertas/` como datos locales, ignorados por git y ausentes de la rama publicada.

---

## Por qué existe esta especificación

Las candidaturas y las listas de ofertas son datos de trabajo que no deben publicarse en el repositorio GitHub. Se conservan en disco para el usuario, pero no se versionan ni se envían.

---

## Alcance

**En:**

- `.gitignore` con `/output/` y `/ofertas/`.
- Ficheros locales en `output/` y `ofertas/` (seguibles en disco, no en git).

**Fuera del alcance:**

- Reescritura del historial ya publicado en GitHub.
- Publicación o subida de estas carpetas.
- Copias de seguridad automáticas.

---

## Criterios de aceptación

- [ ] `git ls-files output ofertas` devuelve vacío.
- [ ] `git check-ignore` confirma ambas carpetas.
- [ ] Los directorios `output/` y `ofertas/` siguen existiendo en local.
- [ ] La rama publicada no contiene rutas bajo `output/` u `ofertas/`.

---

## Decisiones

- **Sí:** Ignorar `output/` y `ofertas/` en git.
- **No:** Versionarlas ni publicarlas en GitHub.
- **Sí:** Conservar los ficheros generados en local.
- **No:** Borrar el historial antiguo (fuera del alcance de esta especificación).
