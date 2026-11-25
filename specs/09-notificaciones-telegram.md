# SPEC 09 — Aviso por Telegram de cada oferta enviada

> **Estado:** Aprobado

> **Depende de:** 08-postulacion-automatica-mcp

> **Fecha:** 2026-11-24

> **Objetivo:** Avisar por Telegram, en el momento del envío, de cada oferta que la postulación automática haya registrado con estado `enviada`, con un resumen breve basado en datos ya existentes en `output/` y `ofertas/envios.json`.

---

## Por qué existe esta especificación

La rutina diaria es silenciosa: `postular-diario.sh` escribe un log y un informe en `ofertas/YYYYMMDD/`, pero nadie se entera de lo enviado hasta que abre el repositorio. D-Lab ya tiene un bot de Telegram operativo; esta spec reutiliza su **bot y su chat** para recibir un aviso por cada candidatura enviada, sin exponer el bot a Internet ni copiar credenciales a este repositorio.

El aviso es un efecto secundario, no una condición del envío: si Telegram falla, la candidatura ya está presentada y el lote debe continuar.

---

## Alcance

**En:**

- **Crear el helper — `.opencode/skills/auto-apply/scripts/notificar_telegram.py` — con una sola responsabilidad: entregar el aviso.**
  - Python 3 con biblioteca estándar (`urllib`, `json`, `argparse`); sin dependencias ni build.
  - `POST https://api.telegram.org/bot<TOKEN>/sendMessage` con `chat_id` y `text`, timeout de 10 s.
  - Credenciales resueltas en tiempo de ejecución: primero `TELEGRAM_BOT_TOKEN` / `TELEGRAM_CHAT_ID` del entorno; si no están, lectura de `/home/elarreglador/D-Lab/info_sensible/telegram.env` (ruta sustituible con `--env`).
  - Nunca imprime ni guarda el token; los motivos de error no incluyen la URL completa.
  - Modo `--sonda`: construye y muestra el mensaje como JSON sin abrir red.
  - Toda salida es JSON (`{"ok":true,...}` o `{"ok":false,"motivo":...}`) y el código de salida es siempre 0.
- **Avisar una vez por oferta enviada — enganchado en el Paso 9 de `auto-apply` — inmediatamente después de `registrar_envio.py registrar`.**
  - Solo si el estado final es `enviada`; `descartada-por-filtro`, `bloqueada`, `sin-responder` y `error` no avisan.
  - `--dry-run` no llama al helper en ningún caso.
  - Un `ok:false` se anota como `telegram: error` en el informe diario y el lote sigue.
- **Documentar el cambio — `SKILL.md`, esta spec, `AGENTS.md` y `TODO.md`.**

**Fuera del alcance:**

- Modificar D-Lab: ni el `app.py` del bot, ni sus manifiestos, ni su Deployment.
- Exponer el bot de D-Lab mediante Ingress ni abrirlo a Internet.
- Escribir credenciales en `output/`, en informes, en el repositorio ni en los logs.
- Avisar del resto de estados, de las ofertas encontradas ni de las descartadas.
- Reenviar avisos, hilos de seguimiento ni gestión de respuestas.

---

## Modelo de datos

### 1. Mensaje

Campos básicos; todo procede de los argumentos que la skill ya tiene al registrar el envío.

```
📬 Candidatura enviada — 2026-11-24T09:12:07+01:00
Empresa: EDICOM
Puesto: Desarrollador IoT
Canal: LinkedIn Easy Apply
URL: https://...
Registro: output/20261124-edicom
```

- El estado se incluye en la cabecera (`Candidatura {estado}`).
- `canal`, `url` y `directorio` se omiten si están vacíos.
- El texto se trunca a 4096 caracteres con el marcador `...[truncado]`, límite del API de Telegram.

### 2. Credenciales y destino

- **Token:** variable `TELEGRAM_BOT_TOKEN` → `/home/elarreglador/D-Lab/info_sensible/telegram.env` (ruta sustituible con `--env`).
- **Chat de destino:** variable `TELEGRAM_CHAT_ID` → `SENSIBLE/telegram-postulacion.env` (ruta sustituible con `--destino-env`) → chat privado de D-Lab como último recurso.

Los ficheros se analizan como pares `CLAVE=VALOR` simples, con comillas opcionales y sin procesar otras claves. El `.env` de D-Lab **no se modifica**: las alertas del clúster siguen en su conversación privada. Si falta el token o el destino, el helper devuelve `{"ok":false,"motivo":"faltan TELEGRAM_BOT_TOKEN o TELEGRAM_CHAT_ID"}`.

---

## Plan de implementación

1. [x] Crear `specs/09-notificaciones-telegram.md` con estado `Aprobado`.
2. [x] Implementar `notificar_telegram.py`: resolución de credenciales, formato del mensaje, envío con `urllib`, modo `--sonda` y salida JSON best-effort.
3. [x] Aceptar `--sonda` y `--env` tanto antes como después del subcomando, para que la invocación de la skill no dependa del orden de las opciones.
4. [x] Enganchar el helper en el Paso 9 de `auto-apply/SKILL.md`, prohibirlo en `--dry-run` y documentar el tratamiento de `ok:false` en el informe.
5. [x] Actualizar la tabla de comandos, la de archivos, las reglas y el árbol de ficheros de la skill.
6. [x] Crear `TODO.md` y añadir una línea en `AGENTS.md` bajo la sección de postulación automática.
7. [x] Verificar con `--sonda`, con credenciales ausentes y con un mensaje real de prueba (autorizado por el usuario).

---

## Criterios de aceptación

- [x] Existe `notificar_telegram.py` y compila con `python3 -m py_compile`.
- [x] `--sonda` imprime el mensaje completo y no realiza ninguna llamada de red.
  - `verificado 2026-11-24`: `python3 .opencode/skills/auto-apply/scripts/notificar_telegram.py oferta --empresa EDICOM --puesto "Desarrollador IoT" --canal "LinkedIn Easy Apply" --url https://www.linkedin.com/jobs/view/ejemplo --fecha 2026-11-24T09:12:07+01:00 --directorio output/20261124-edicom --sonda` → JSON con `"sonda": true` y las seis líneas.
- [x] Sin credenciales devuelve `ok:false` y código de salida 0.
  - `verificado 2026-11-24`: `env -u TELEGRAM_BOT_TOKEN -u TELEGRAM_CHAT_ID python3 ... --env /tmp/no-existe.env` → `{"ok": false, "motivo": "no se pudo leer /tmp/no-existe.env: No such file or directory"}`, `exit=0`.
- [x] El mensaje real llega al chat de D-Lab.
  - `verificado 2026-11-24`: invocación de prueba con `--estado "de prueba"` → `{"ok": true, "message_id": 5034}`.
- [x] Ningún fichero del repositorio contiene el token ni el chat ID; se leen en tiempo de ejecución.
- [x] La skill avisa solo tras un estado `enviada` y nunca en `--dry-run`.
- [x] D-Lab y el bot de `cluster-ave` permanecen intactos.

---

## Decisiones

- **Sí:** API directa de Telegram, elegida por el usuario. Funciona aunque el clúster D-Lab esté apagado.
- **Sí:** reutilizar el bot y el chat de D-Lab, leyendo sus credenciales en tiempo de ejecución desde su fichero ignorado por git.
- **Sí:** helper separado. Es el único módulo que conoce Telegram; `registrar_envio.py` sigue ocupándose solo del índice.
- **Sí:** best-effort. Un fallo del aviso se anota en el informe, pero no cambia el estado de la candidatura ni detiene el lote.
- **Sí:** campos básicos. No se cruzan informes de `job-search` ni se copian las preguntas del formulario al mensaje.
- **Sí:** `--sonda` para comprobar el formato sin molestar al chat.
- **No:** tocar D-Lab ni exponer su bot mediante Ingress.
- **No:** credenciales en el repositorio, en `output/` ni en los logs.
- **No:** avisar de estados distintos de `enviada` ni de ofertas aún no enviadas.

---

## Riesgos

| Riesgo | Mitigación |
| --- | --- |
| Cambian el token o el chat de D-Lab | Se leen en cada ejecución; basta con exportar las variables o actualizar el `.env` de D-Lab |
| Telegram caída o limitado (HTTP 429) | `ok:false` con motivo, `exit 0`, anotación en el informe; el envío ya realizado no se rehace |
| Falta de red desde la máquina que postula | Timeout de 10 s y tratamiento best-effort idéntico al de cualquier otro error |
| El fichero de credenciales se mueve | Opción `--env` para indicar otra ruta; variables de entorno como alternativa |
| El mensaje incluye datos sensiblemente largos | Truncado a 4096 caracteres con marcador explícito |
| Se filtra el token en un log | Los motivos de error nunca incluyen la URL de la petición ni el token; solo `HTTP <code>`, red o descripción de Telegram |
| El aviso confunde a una candidatura real | La prueba se envió con `--estado "de prueba"` y el texto lo identifica como prueba |

---

## Lo que **no** está en esta especificación

- Modificación del bot, los manifiestos ni el despliegue de D-Lab.
- Ingress, autenticación nueva ni exposición pública del `/notify` del bot.
- Avisos de ofertas encontradas, descartadas o bloqueadas.
- Reenvíos, seguimiento de candidaturas ni gestión de respuestas de empresas.
- Credenciales versionadas ni copiadas a `output/`.

---

## Enmienda de 2026-11-24 — destino en un grupo propio

El primer mensaje de prueba llegó a la conversación privada del bot (`type: private`, «El Arreglador»), la misma donde caen las alertas del clúster. El usuario creó después el grupo privado **Busqueda empleo** y añadió al bot `@Dlab_mrbot`. El ID se obtuvo con `getUpdates?offset=-1`: `-5333087186` (`type: group`).

Cambios:

- `SENSIBLE/telegram-postulacion.env` (ignorado por git, modo 600) contiene **solo** `TELEGRAM_CHAT_ID=-5333087186`; nunca el token.
- El helper resuelve el destino en este orden: variable `TELEGRAM_CHAT_ID` → fichero local (opción `--destino-env`) → chat privado de D-Lab. El token sigue leyéndose del entorno o del `.env` de D-Lab. `postular-diario.sh` no necesita cambios porque hereda el entorno del proceso.
- `SKILL.md` y `AGENTS.md` documentan el nuevo destino.

Criterios verificados:

- [x] Resolución de credenciales: token leído de D-Lab y `chat_id=-5333087186` desde el fichero local, sin imprimir el token.
- [x] D-Lab y su `.env` permanecen intactos: las alertas del clúster siguen en su conversación privada.
- [x] Mensaje de prueba entregado en el grupo: `{"ok": true, "message_id": 5038}` (`verificado 2026-11-24`).
