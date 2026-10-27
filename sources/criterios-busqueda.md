# Criterios de búsqueda de ofertas

Criterios **permanentes** de las búsquedas de empleo (skill `job-search`). Interno:
no se envía a las empresas ni forma parte del CV.

Se lee en el **Paso 1** de la skill, antes de derivar el resto de criterios de
`sources/curriculum-base.md`. Única fuente de la **banda de seniority** y de la
**geografía**.

## Banda de seniority

- **Admitida:** `junior`, `mid`.
- **Descartada:** `senior`, `lead`.

Motivo: 18 meses trabajando como desarrollador. Aunque el CV menciona más de
20 años en hardware, soporte y gestión de infraestructuras, eso no es
experiencia de desarrollo: un puesto senior no encaja.

## Geografía

- **Valencia** — base, sin mudanza.
- **Barcelona** y **Madrid** — desplazamiento varias veces por semana (sin
  mudarse). Cubre híbrido y presencial en ambas ciudades.
- **Resto de España** — descartado **en presencial e híbrido** (Sevilla, Vigo,
  etc. no aplican). Una oferta **100 % remota** de cualquier punto de España o
  Europa sí entra: lo que descarta es la modalidad, no la sede.
- **Remoto** — sí, Europa.

Tokens de `--ubicacion`:

- Pasadas de España (Valencia, Barcelona, Madrid): `valencia,valencian,barcelona,madrid`
- Pasada remota (además, filtro duro): `spain,worldwide,europe,emea,...` según la consulta

## Revisión

- **Última revisión:** 2026-10-27.
- Cambie este fichero si cambia la banda, la geografía o la disposición a
  desplazarse; no hace falta tocar la skill.
