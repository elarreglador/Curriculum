#!/usr/bin/env bash
# Lanzador diario de la skill auto-apply. No instala la línea de crontab.
set -euo pipefail

export HOME="/home/elarreglador"
export PATH="/home/elarreglador/.opencode/bin:/usr/local/bin:/usr/bin:/bin"

# cron no hereda la sesión gráfica: derivar el entorno para el navegador headed.
export DISPLAY="${DISPLAY:-:0}"
export WAYLAND_DISPLAY="${WAYLAND_DISPLAY:-wayland-0}"
export XDG_RUNTIME_DIR="${XDG_RUNTIME_DIR:-/run/user/$(id -u)}"
export DBUS_SESSION_BUS_ADDRESS="unix:path=$XDG_RUNTIME_DIR/bus"
if [[ -z "${XAUTHORITY:-}" ]]; then
  XAUTHORITY="$(ls -1t "$XDG_RUNTIME_DIR"/.mutter-Xwaylandauth.* 2>/dev/null | head -1 || true)"
  [[ -z "$XAUTHORITY" && -r "$HOME/.Xauthority" ]] && XAUTHORITY="$HOME/.Xauthority"
  [[ -n "$XAUTHORITY" ]] && export XAUTHORITY
fi

REPO="/home/elarreglador/Documentos/trabajo"
cd "$REPO"
SCRIPTS="$REPO/.opencode/skills/auto-apply/scripts"

FECHA="$(date +%Y%m%d)"
HORA="$(date +%H%M)"
mkdir -p "ofertas/$FECHA"
LOG="ofertas/$FECHA/postulacion-$HORA.log"

MODO="Ejecuta la skill auto-apply: busca ofertas con job-search y company-jobs (con la reserva de encaje ≥ 25), crea o reutiliza cuentas con account-signup cuando un portal lo exija, prioriza las mejores ofertas y baja el umbral por pasadas (55/45/35/25) hasta enviar al menos 15 candidaturas; si faltan, amplía la búsqueda a empleos de informática afines, incluidos los de técnico. No hay tope diario: sigue hasta agotar la cola y envía las candidaturas que superen los filtros del formulario."
MODO_VALOR="normal"
if [[ "${1:-}" == "--dry-run" ]]; then
  MODO="Ejecuta la skill auto-apply en modo --dry-run: recorre el flujo sin pulsar Enviar, sin crear cuentas ni abrir el correo, y registra cada oferta."
  MODO_VALOR="dry-run"
fi

# El modelo por defecto agotó los créditos del proveedor; se usa uno gratuito.
MODELO="opencode/big-pickle"

INICIO_EPOCA="$(date +%s)"
INICIO_ISO="$(date --iso-8601=seconds)"
echo "$INICIO_ISO Inicio de la postulación diaria" > "$LOG"

# Avisos best-effort: si Telegram falla, el lote sigue. El JSON queda en el log.
python3 "$SCRIPTS/notificar_telegram.py" lote \
  --estado inicio --fecha "$INICIO_ISO" --modo "$MODO_VALOR" --log "$LOG" \
  >> "$LOG" 2>&1 || true

# Sin -e durante la ejecución: aunque falle, se envía el aviso de fin con el código.
set +e
opencode run --auto --archived --model "$MODELO" --title "postulación diaria $FECHA" "$MODO" >> "$LOG" 2>&1
CODIGO=$?
set -e

FIN_ISO="$(date --iso-8601=seconds)"
DURACION=$(( $(date +%s) - INICIO_EPOCA ))
ENVIADAS="$(python3 "$SCRIPTS/registrar_envio.py" contar 2>/dev/null \
  | python3 -c 'import json,sys; print(json.load(sys.stdin).get("enviadas_hoy", ""))' 2>/dev/null || true)"

echo "$FIN_ISO Fin de la postulación diaria (código $CODIGO)" >> "$LOG"

python3 "$SCRIPTS/notificar_telegram.py" lote \
  --estado fin --fecha "$FIN_ISO" --modo "$MODO_VALOR" \
  --duracion "$DURACION" --enviadas "$ENVIADAS" --log "$LOG" --codigo "$CODIGO" \
  >> "$LOG" 2>&1 || true
