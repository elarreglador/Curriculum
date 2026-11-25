# TODO

## Features

- [x] Aviso por Telegram de cada oferta enviada (spec 09): helper `notificar_telegram.py` enganchado en el Paso 9 de `auto-apply`.
- [x] Destino propio de los avisos (enmienda de la spec 09): grupo «Busqueda empleo» configurado en `SENSIBLE/telegram-postulacion.env`, sin tocar el chat de las alertas de D-Lab.
- [x] Envío sin tope diario (enmienda de la spec 08): objetivo de al menos 15 candidaturas por ejecución, pisos de encaje 55/45/35/25, reserva en `job-search` y modo ampliado a puestos de técnico.

## Fix

- Ninguno registrado.

## Tareas finalizadas

- [x] Verificación del aviso (2026-11-24): `--sonda`, fallo sin credenciales (salida 0) y mensaje de prueba real entregado (`message_id` 5034).
- [x] Verificación del nuevo destino (2026-11-24): ID `-5333087186` leído con `getUpdates?offset=-1` y mensaje de prueba enviado al grupo.
- [x] Verificación del envío sin tope (2026-11-25): 20 altas aceptadas por `registrar_envio.py`, duplicado por URL actualizado, `contar` informativo y sintaxis de los scripts revisada.
