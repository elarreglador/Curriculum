# SPEC 04 — Candidaturas solo en Markdown

> **Estado:** Aprobado
>
> **Depende de:** 02-cv-generator-skill
>
> **Sustituye a:** 01-curriculum-odt, 02-cv-generator-skill
>
> **Fecha:** 2026-10-23
>
> **Objetivo:** Definir que la skill de generación de CV y carta produce solo archivos de texto Markdown (.md), sin convertir a ODT ni PDF.

---

## Por qué existe esta especificación

El flujo de generación de candidaturas en `output/YYYYMMDD-nombreempresa/` se limita a `pin.png`, `info.md`, `curriculum-EMPRESA.md` y `carta-EMPRESA.md`. Los formatos ofimáticos (ODT/PDF) dejan de generarse automáticamente; si el usuario los necesita, los gestiona fuera de esta skill.

---

## Alcance

**En:**

- `pin.png` — foto de la cabecera del CV.
- `info.md` — datos internos de empresa y oferta.
- `curriculum-EMPRESA.md` — CV adaptado, editable.
- `carta-EMPRESA.md` — carta de presentación adaptada, editable.

**Fuera del alcance:**

- Generación de archivos `.odt`, `.pdf`, `.docx` ni ningún otro formato ofimático.
- Ejecución de `libreoffice` o de `md2odt.py` desde la skill.
- Envío automático de candidaturas.

---

## Criterios de aceptación

- [ ] Una candidatura generada por la skill solo contiene `pin.png`, `info.md`, `curriculum-EMPRESA.md` y `carta-EMPRESA.md`.
- [ ] Ningún script de la skill invoca a LibreOffice ni a `md2odt.py`.
- [ ] `SKILL.md`, `AGENTS.md` y `README.md` describen el estándar solo-.md.

---

## Decisiones

- **Sí:** Solo Markdown como salida de la skill. Los `.md` son fuentes editables y suficientes para el usuario.
- **No:** ODT/PDF como entregables automáticos de la skill. El formato de entrega lo decide el usuario fuera del repositorio.
- **Sí:** Conservar los ficheros locales de `output/`; no se versionan en git ni se publican.
- **No:** Borrar `templates/curriculum-odt.odt`; queda como referencia histórica.

---

## Enmienda (2026-11-24) — Adjuntos para la postulación automática

La spec 08 autoriza una **excepción controlada**: la skill `auto-apply` genera
PDF (y DOCX solo si el portal lo exige) a partir del `.md` adaptado, mediante
`.opencode/skills/auto-apply/scripts/generar_adjuntos.py`. El PDF se produce desde
un HTML temporal con LibreOffice headless; LibreOffice directo sobre `.md` da un
PDF con sintaxis Markdown en texto plano y queda prohibido.

`cv-generator` **no cambia**: sigue entregando solo `pin.png`, `info.md`,
`curriculum-EMPRESA.md` y `carta-EMPRESA.md`. La conversión es responsabilidad
del canal de envío, no de la generación de la candidatura.

---
