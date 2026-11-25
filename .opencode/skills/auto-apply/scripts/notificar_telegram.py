#!/usr/bin/env python3
"""Aviso por Telegram de candidaturas enviadas y de cuentas de empresa.

Envía un resumen breve a través de la API pública de Telegram con el bot de
D-Lab. El token se lee en tiempo de ejecución del entorno o del fichero
ignorado por git D-Lab/info_sensible/telegram.env (ruta configurable con
--env). El destino se resuelve en este orden: variable TELEGRAM_CHAT_ID,
fichero local SENSIBLE/telegram-postulacion.env (opción --destino-env) y, como
último recurso, el chat de D-Lab. Así las alertas del clúster no se mudan.

Es un efecto secundario best-effort: nunca impide continuar el lote de
postulación. Toda respuesta, incluidos los fallos, se imprime como JSON.
Los mensajes de cuenta no incluyen nunca credenciales.
"""

from __future__ import annotations

import argparse
import json
import os
import urllib.error
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
ENV_POR_DEFECTO = Path("/home/elarreglador/D-Lab/info_sensible/telegram.env")
DESTINO_POR_DEFECTO = REPO / "SENSIBLE" / "telegram-postulacion.env"
API_TELEGRAM = "https://api.telegram.org"
LIMITE_TEXTO = 4096
TIEMPO_ESPERA = 10


class ErrorAviso(Exception):
    """Fallo al preparar o entregar el aviso; nunca contiene credenciales."""


def leer_pares(ruta: Path) -> dict[str, str]:
    """Lee pares CLAVE=VALOR simples de un .env, sin devolver otras claves."""
    try:
        lineas = ruta.read_text(encoding="utf-8").splitlines()
    except OSError as error:
        raise ErrorAviso(f"no se pudo leer {ruta}: {error.strerror}") from None

    valores: dict[str, str] = {}
    for linea in lineas:
        linea = linea.strip()
        if not linea or linea.startswith("#") or "=" not in linea:
            continue
        clave, valor = linea.split("=", 1)
        clave = clave.strip()
        if clave in ("TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID"):
            valores[clave] = valor.strip().strip('"').strip("'")
    return valores


def leer_credenciales(ruta_env: Path, ruta_destino: Path) -> tuple[str, str]:
    """Devuelve (token, chat_id): entorno > destino local > configuración de D-Lab."""
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "").strip()

    if not token:
        token = leer_pares(ruta_env).get("TELEGRAM_BOT_TOKEN", "")
    if not chat_id:
        if ruta_destino.exists():
            chat_id = leer_pares(ruta_destino).get("TELEGRAM_CHAT_ID", "")
        if not chat_id:
            chat_id = leer_pares(ruta_env).get("TELEGRAM_CHAT_ID", "")

    if not token or not chat_id:
        raise ErrorAviso("faltan TELEGRAM_BOT_TOKEN o TELEGRAM_CHAT_ID")
    return token, chat_id


def truncar(texto: str) -> str:
    if len(texto) <= LIMITE_TEXTO:
        return texto
    return texto[: LIMITE_TEXTO - 20] + "\n...[truncado]"


def formatear_mensaje(datos: argparse.Namespace) -> str:
    lineas = [
        f"📬 Candidatura {datos.estado} — {datos.fecha}",
        f"Empresa: {datos.empresa}",
        f"Puesto: {datos.puesto}",
    ]
    if datos.canal:
        lineas.append(f"Canal: {datos.canal}")
    if datos.url:
        lineas.append(f"URL: {datos.url}")
    if datos.directorio:
        lineas.append(f"Registro: {datos.directorio}")
    return truncar("\n".join(lineas))


def formatear_mensaje_cuenta(datos: argparse.Namespace) -> str:
    """Aviso de alta o verificación de cuenta, sin credenciales."""
    lineas = [
        f"🔐 Cuenta {datos.estado} — {datos.fecha}",
        f"Empresa: {datos.empresa}",
        f"Dominio: {datos.dominio}",
    ]
    if datos.url:
        lineas.append(f"URL: {datos.url}")
    return truncar("\n".join(lineas))


def enviar(texto: str, token: str, chat_id: str) -> dict:
    url = f"{API_TELEGRAM}/bot{token}/sendMessage"
    cuerpo = json.dumps(
        {
            "chat_id": chat_id,
            "text": texto,
            "disable_notification": False,
        }
    ).encode("utf-8")
    peticion = urllib.request.Request(
        url,
        data=cuerpo,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(peticion, timeout=TIEMPO_ESPERA) as respuesta:
            datos = json.loads(respuesta.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        raise ErrorAviso(f"HTTP {error.code} de Telegram") from None
    except (urllib.error.URLError, TimeoutError, OSError) as error:
        raise ErrorAviso(f"error de red: {getattr(error, 'reason', error)}") from None
    except (ValueError, UnicodeDecodeError) as error:
        raise ErrorAviso(f"respuesta no JSON de Telegram: {type(error).__name__}") from None

    if not isinstance(datos, dict) or not datos.get("ok"):
        motivo = datos.get("description", "respuesta inesperada") if isinstance(datos, dict) else "respuesta inesperada"
        raise ErrorAviso(f"Telegram rechazó el aviso: {motivo}")
    return {"ok": True, "message_id": datos.get("result", {}).get("message_id")}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env", type=Path, default=ENV_POR_DEFECTO, help="fichero .env con las credenciales")
    parser.add_argument("--destino-env", type=Path, default=DESTINO_POR_DEFECTO, help="fichero con el chat ID de esta skill")
    parser.add_argument("--sonda", action="store_true", help="muestra el mensaje sin enviarlo")
    subparsers = parser.add_subparsers(dest="command", required=True)

    oferta = subparsers.add_parser("oferta", help="aviso de una oferta enviada")
    oferta.add_argument("--empresa", required=True)
    oferta.add_argument("--puesto", required=True)
    oferta.add_argument("--canal", default="")
    oferta.add_argument("--url", default="")
    oferta.add_argument("--estado", default="enviada")
    oferta.add_argument("--fecha", required=True, help="ISO 8601; la fecha y hora del envío")
    oferta.add_argument("--directorio", default="", help="directorio del registro en output/")
    # Aceptar las opciones globales también después del subcomando, sin
    # sobrescribir los valores globales cuando no se repiten.
    oferta.add_argument("--env", type=Path, default=argparse.SUPPRESS)
    oferta.add_argument("--destino-env", type=Path, default=argparse.SUPPRESS)
    oferta.add_argument("--sonda", action="store_true", default=argparse.SUPPRESS)

    cuenta = subparsers.add_parser("cuenta", help="aviso de alta o verificación de cuenta")
    cuenta.add_argument("--empresa", required=True)
    cuenta.add_argument("--dominio", required=True)
    cuenta.add_argument(
        "--estado",
        required=True,
        choices=["creada", "pendiente-verificacion", "verificada", "error"],
    )
    cuenta.add_argument("--fecha", required=True, help="ISO 8601; alta o verificación")
    cuenta.add_argument("--url", default="")
    cuenta.add_argument("--env", type=Path, default=argparse.SUPPRESS)
    cuenta.add_argument("--destino-env", type=Path, default=argparse.SUPPRESS)
    cuenta.add_argument("--sonda", action="store_true", default=argparse.SUPPRESS)

    args = parser.parse_args()
    texto = formatear_mensaje_cuenta(args) if args.command == "cuenta" else formatear_mensaje(args)
    if args.sonda:
        print(json.dumps({"sonda": True, "texto": texto}, ensure_ascii=False))
        return 0

    try:
        token, chat_id = leer_credenciales(args.env, args.destino_env)
        resultado = enviar(texto, token, chat_id)
    except ErrorAviso as error:
        resultado = {"ok": False, "motivo": str(error)}
    print(json.dumps(resultado, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
