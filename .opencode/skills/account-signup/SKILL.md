---
name: account-signup
description: Crea, reutiliza y verifica cuentas de usuario en webs de empresas cuando hace falta para avanzar en una candidatura o en la búsqueda de ofertas. La invocan auto-apply y company-jobs; nunca envía candidaturas. Avisa por Telegram al crear la cuenta y tras verificarla. Úsala cuando un portal exija registro o login.
---

# account-signup

Skill de alta de cuentas en portales de empresa. La invocan `auto-apply` y
`company-jobs` cuando un formulario o una web de empleo exige autenticación para
seguir. **Nunca envía candidaturas**: devuelve el control al llamador con el
resultado de la cuenta.

## Principio de diseño

Los scripts resuelven lo determinista (normalizar dominios, deduplicar, escribir
el índice, comprobar claves sin imprimirlas). El agente resuelve lo cualitativo:
si el registro es necesario, qué pide el formulario y si hay un bloqueo.

Trabaja sin supervisión, como `auto-apply`: ante duda se omite y se registra el
motivo. Ninguna credencial sale de `SENSIBLE/`. No se elude CAPTCHA ni 2FA.

## Cuándo usar esta skill

- Un formulario de candidatura exige iniciar sesión o crear cuenta.
- Una web de `ofertas/empresas.json` exige login para ver sus ofertas.
- El agente lo considera necesario para avanzar en una candidatura o en la
  búsqueda de ofertas, y no sirve ninguna cuenta ya registrada.

No se usa para enviar CV, para puntuar ofertas ni para consultar el correo salvo
para verificar una cuenta recién creada.

## Configuración

> **Sin tope de cuentas por ejecución.**
>
> El freno es la deduplicación por dominio, el ritmo pausado entre formularios y
> **un solo intento de verificación por lote**. Lo pendiente se reintenta en
> ejecuciones futuras consultando `SENSIBLE/cuentas.json`.

## Herramientas

| Herramienta | Uso |
| --- | --- |
| `bash` | ejecutar `cuentas.py` y `notificar_telegram.py` |
| MCP `playwright` | navegar, rellenar el registro, iniciar sesión y abrir el correo |
| `read` | leer `sources/datos-candidatura.md` y `SENSIBLE/credenciales.env` |
| `write` / `edit` | solo los informes del llamador; nunca credenciales |

## Archivos que intervienen

| Archivo | Papel |
| --- | --- |
| `sources/datos-candidatura.md` | nombre, email y teléfono del formulario de registro |
| `SENSIBLE/credenciales.env` | **única fuente** de la contraseña maestra y de la clave de Proton |
| `SENSIBLE/cuentas.json` | índice por dominio, sin contraseñas |
| `SENSIBLE/playwright-profile/` | sesión persistente del navegador |
| `SENSIBLE/credenciales.md`, `SENSIBLE/cuentas-empresas.md` | histórico; ya no son fuente |
| `.opencode/skills/account-signup/scripts/cuentas.py` | helpers deterministas |
| `.opencode/skills/auto-apply/scripts/notificar_telegram.py` | avisos de cuenta |

## Comandos

```bash
A=.opencode/skills/account-signup/scripts/cuentas.py
T=.opencode/skills/auto-apply/scripts/notificar_telegram.py

# 1. ¿Ya hay cuenta para este dominio?
python3 $A buscar --dominio "empresa.com"

# 2. Comprobar que existen las cuatro credenciales, sin imprimir valores
python3 $A verificar-credenciales

# 3. Registrar el alta o su resultado
python3 $A registrar --empresa "EMPRESA" --dominio "empresa.com" \
  --url "URL" --email "elarreglador@protonmail.com" \
  --estado creada --notas "registro completado"

# 4. Actualizar tras verificar el correo
python3 $A registrar --empresa "EMPRESA" --dominio "empresa.com" \
  --estado verificada --fecha-verificacion "YYYY-MM-DDTHH:MM:SS+01:00"

# 5. Avisos: al crear y tras verificar
python3 $T cuenta --empresa "EMPRESA" --dominio "empresa.com" \
  --estado creada --fecha "YYYY-MM-DDTHH:MM:SS+01:00"
python3 $T cuenta --empresa "EMPRESA" --dominio "empresa.com" \
  --estado verificada --fecha "YYYY-MM-DDTHH:MM:SS+01:00"

# 6. Sonda: ver el mensaje sin enviarlo
python3 $T cuenta --empresa "EMPRESA" --dominio "empresa.com" \
  --estado pendiente-verificacion --fecha "YYYY-MM-DDTHH:MM:SS+01:00" --sonda

# 7. Listar el índice (nunca contiene contraseñas)
python3 $A listar
```

Los estados son `creada`, `pendiente-verificacion`, `verificada` y `error`.
`registrar` actualiza la entrada existente si el dominio ya está en el índice y
devuelve JSON. Las credenciales **nunca** se pasan como argumentos de estos
comandos: `--notas` y `--email` son datos visibles, no claves.

## Flujo de interacción

### Paso 0 — Decidir si procede

1. Solo actuar si el registro o el login es necesario para avanzar en una
   candidatura o en la búsqueda de ofertas. No crear cuentas por curiosidad ni
   para newsletters.
2. Ejecutar `cuentas.py buscar --dominio` con el host de la web.
3. Si no hay dominio, derivarlo de la URL con el sentido común (sin `www.`, sin
   esquema, sin puerto).
4. Si no procede, devolver `no-requerida` al llamador sin tocar nada.

### Paso 1 — Reutilizar una cuenta existente

1. Con estado `verificada` o `creada`: iniciar sesión con la credencial maestra
   de `SENSIBLE/credenciales.env` y devolver `reutilizada`.
2. Con `pendiente-verificacion`: ir al Paso 3 (un intento por lote).
3. Con `error`: no reintentar en el mismo lote; devolver `bloqueada` con el
   motivo guardado en `notas`.
4. Leer las credenciales con `read` desde `SENSIBLE/credenciales.env`. Nunca
   copiarlas a `output/`, a `ofertas/`, a un informe ni a un mensaje de Telegram.

### Paso 2 — Crear la cuenta

1. Rellenar identidad y contacto desde `sources/datos-candidatura.md`; la
   contraseña sale de `CV_PASSWORD` en `credenciales.env`.
2. Aceptar solo los términos legales necesarios para el alta. No marcar casillas
   de marketing ni comunicaciones; la única excepción es «Seguir a [empresa]»,
   que es la preferencia permanente del usuario.
3. Si una pregunta obligatoria no tiene valor en `datos-candidatura.md`, no
   inventarlo: devolver `sin-responder` y registrar la pregunta literal.
4. Si aparece CAPTCHA, 2FA o verificación por SMS: no eludirlo. Registrar
   `error` y avisar con estado `error`.
5. Con registro completado, `cuentas.py registrar --estado creada` y primer
   aviso por Telegram (Paso 4).

### Paso 3 — Verificar en Proton Mail

1. Navegar a `https://account.proton.me/mail`.
2. Si el perfil `SENSIBLE/playwright-profile/` ya tiene la sesión iniciada,
   continuar. Si no, iniciar sesión con `PROTON_EMAIL` y `PROTON_PASSWORD`.
3. Si aparece 2FA, CAPTCHA o cualquier segundo factor: no eludirlo. Dejar la
   cuenta en `pendiente-verificacion` y avisar. Fin del intento en este lote.
4. Buscar el correo de verificación de la empresa por remitente o asunto que
   contenga su dominio. Abrirlo y pulsar el enlace de confirmación.
5. No responder, no reenviar, no descargar adjuntos, no borrar correos y no
   tocar los demás mensajes de la bandeja.
6. Sin correo aún: `pendiente-verificacion`. Con enlace pulsado: `verificada`,
   con `fecha_verificacion` real, y segundo aviso.

### Paso 4 — Registrar y avisar

1. Escribir el estado final con `cuentas.py registrar`. Conservar
   `fecha_creacion` original: una actualización no debe borrarla.
2. Avisar por Telegram en dos momentos distintos:
   - al crear la cuenta: `creada` o `pendiente-verificacion`;
   - tras pulsar el enlace: `verificada`.
3. `notificar_telegram.py` imprime JSON y termina siempre con código 0. Si
   falla, se anota en el informe del llamador y el flujo continúa.
4. Devolver al llamador el estado y si la cuenta se creó, se reutilizó o quedó
   pendiente.

### Paso 5 — Devolver el control

- `verificada` o `creada` → el llamador continúa (rellena el formulario o lee
  las ofertas).
- `reutilizada` → lo mismo, sin registrar alta nueva.
- `pendiente-verificacion` → el llamador bloquea esa oferta y sigue la cola.
- `error` / `sin-responder` → el llamador registra el motivo y sigue la cola.

## Modo seco

Si el llamador ejecuta `--dry-run`, esta skill **no crea cuentas, no abre el
correo y no envía avisos**. Solo comprueba el índice y describe lo que haría.
Ningún registro queda con estado `creada` ni `verificada`.

## Reglas importantes

1. **Sin credenciales fuera de `SENSIBLE/`.** Nada de claves en `sources/`,
   `output/`, `ofertas/`, informes, mensajes ni argumentos de comandos.
2. **Sin elusión.** CAPTCHA, 2FA y SMS se registran como bloqueo; nunca se
   sortean.
3. **Sin duplicados.** Una sola cuenta por dominio normalizado.
4. **Sin tope, con ritmo.** No hay límite de cuentas, pero se mantiene el ritmo
   pausado entre formularios y un solo intento de verificación por lote.
5. **Datos reales.** Identidad desde `datos-candidatura.md`; una pregunta
   obligatoria sin respuesta se anota, nunca se inventa.
6. **Sin correo accesorio.** El webmail se abre solo para la verificación de
   esa cuenta.
7. **Castellano** para documentación e informes.
8. **Sin commits.** `SENSIBLE/` está ignorado por git.

## Estructura de archivos

```
trabajo/
├── sources/
│   └── datos-candidatura.md
├── SENSIBLE/                       # ignorado por git
│   ├── credenciales.env            # fuente única de credenciales
│   ├── cuentas.json                # índice por dominio, sin claves
│   ├── credenciales.md             # histórico
│   ├── cuentas-empresas.md         # histórico (sembró cuentas.json)
│   └── playwright-profile/
└── .opencode/skills/
    ├── account-signup/
    │   ├── SKILL.md
    │   └── scripts/cuentas.py
    └── auto-apply/scripts/notificar_telegram.py
```
