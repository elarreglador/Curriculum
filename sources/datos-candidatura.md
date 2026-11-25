# Datos para formularios de candidatura

> Interno. Se usa tal cual en los formularios; no se envía como documento.
> Única fuente de respuestas de la skill `auto-apply`. Nunca rellenar con
> estimaciones del agente: un dato que no esté aquí es un dato que no se entrega,
> salvo la regla numérica (`0`) de «Reglas de uso».

## Identidad y contacto

| Campo | Valor |
| --- | --- |
| Nombre completo | David Moreno Bolívar |
| Email | elarreglador@protonmail.com |
| Teléfono | 651 73 77 65 |
| Localidad | Burjassot (Valencia)|

## Experiencia y disponibilidad

| Campo | Valor | Origen |
| --- | --- | --- |
| Experiencia como desarrollador | 18 meses | sources/curriculum-base.md |
| Experiencia con linux (usuario) | desde 1995 | el usuario lo indica 2026-11-25 |
| Experiencia total en hardware e infraestructura | Más de 20 años | sources/curriculum-base.md |
| Experiencia profesional gestionando infraestructuras en AWS y GCP | 0 años | Decisión del usuario, 2026-11-25 |
| Salario pretendido | 24000-30000 EUR anuales según oferta | Decisión del usuario, 2026-11-24 |
| Disponibilidad | Inmediata | Decisión del usuario, 2026-11-24 |
| Permiso de trabajo en España | Sí | Decisión del usuario, 2026-11-24 |
| Movilidad | Valencia base; Barcelona y Madrid desplazable | sources/criterios-busqueda.md |

## Respuestas frecuentes

| Pregunta habitual | Respuesta | Origen |
| --- | --- | --- |
| Por qué te interesa el puesto | Perfil híbrido: software embebido e IoT junto a electricidad, redes y hardware; conecta con el negocio de la empresa | sources/curriculum-base.md |
| Nivel de inglés | B1 | Decisión del usuario, 2026-11-24 |

## Reglas de uso

- Nunca rellenar un dato con una estimación del agente.
- Ante una pregunta no prevista, responder solo si el valor está en este fichero o en el curriculum.
- Una pregunta **obligatoria numérica** sin valor declarado —por ejemplo «¿Cuántos años de experiencia profesional tienes gestionando infraestructuras en AWS y GCP?»— se responde **`0`** (en un desplegable, la opción equivalente: «0 años», «Menos de 1 año»). Es decisión permanente del usuario (2026-11-25), no una estimación: `0` declara que no se tiene experiencia profesional en esa tecnología y evita que un campo vacío bloquee el envío. Se anota literalmente en `envio-EMPRESA.md`, con origen `sources/datos-candidatura.md (regla para preguntas numéricas sin dato, 2026-11-25)`. La candidatura **no se abandona** por este motivo.
- El resto de preguntas **obligatorias** sin valor se dejan en blanco o se elige la opción neutra («Prefiero no decirlo», si existe); se anota literalmente en `envio-EMPRESA.md` y se envía la candidatura igual, sin inventar el dato.
- Una pregunta **opcional** sin valor se deja en blanco o se elige la opción neutra («Prefiero no decirlo», si existe).
- Las cifras de experiencia se entregan tal cual aparecen aquí, sin redondearlas al alza.
