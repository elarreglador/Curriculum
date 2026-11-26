# TODO

## Features

- [x] Aviso por Telegram de cada oferta enviada (spec 09): helper `notificar_telegram.py` enganchado en el Paso 9 de `auto-apply`.
- [x] Destino propio de los avisos (enmienda de la spec 09): grupo «Busqueda empleo» configurado en `SENSIBLE/telegram-postulacion.env`, sin tocar el chat de las alertas de D-Lab.
- [x] Envío sin tope diario (enmienda de la spec 08): objetivo de al menos 15 candidaturas por ejecución, pisos de encaje 55/45/35/25, reserva en `job-search` y modo ampliado a puestos de técnico.
- [x] Filtros del formulario blandos (enmienda de la spec 08): experiencia, salario, permiso de trabajo, ubicación, seniority, disponibilidad e inglés dejan de descartar; se anotan solo en `envio-EMPRESA.md` y se envía el CV con los datos reales. `sin-responder` también pasa a ser blando (en blanco o neutro y envío).
- [x] Avisos de inicio y fin del lote (enmienda de la spec 09): subcomando `lote` de `notificar_telegram.py` enganchado en `postular-diario.sh`; el fin incluye duración, envíos registrados hoy, log y código de salida; en `--dry-run` ambos avisos van marcados como modo seco.

## Fix

- Ninguno registrado.

## Tareas finalizadas

- [x] Verificación del aviso (2026-11-24): `--sonda`, fallo sin credenciales (salida 0) y mensaje de prueba real entregado (`message_id` 5034).
- [x] Verificación del nuevo destino (2026-11-24): ID `-5333087186` leído con `getUpdates?offset=-1` y mensaje de prueba enviado al grupo.
- [x] Verificación del envío sin tope (2026-11-25): 20 altas aceptadas por `registrar_envio.py`, duplicado por URL actualizado, `contar` informativo y sintaxis de los scripts revisada.
- [x] Verificación de los filtros blandos (2026-11-25): skill, spec 08, AGENTS.md, ESTRUCTURA.md y `datos-candidatura.md` alineados; plantillas de informe y registro actualizadas; estados de filtro conservados como legacy; sintaxis Python comprobada.
- [x] Verificación de los avisos de lote (2026-11-25): mensajes de inicio y fin probados con `--sonda` en modo normal y seco, con código de salida 7, y lanzador probado con `opencode run` sustituido por un stub; `py_compile` y `bash -n` correctos.
