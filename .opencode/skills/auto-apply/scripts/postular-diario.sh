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

FECHA="$(date +%Y%m%d)"
HORA="$(date +%H%M)"
mkdir -p "ofertas/$FECHA"
LOG="ofertas/$FECHA/postulacion-$HORA.log"

MODO="Ejecuta la skill auto-apply: busca ofertas con job-search y company-jobs, selecciona hasta el tope diario y envía las candidaturas que superen los filtros del formulario."
if [[ "${1:-}" == "--dry-run" ]]; then
  MODO="Ejecuta la skill auto-apply en modo --dry-run: recorre el flujo sin pulsar Enviar y registra cada oferta."
fi

# El modelo por defecto agotó los créditos del proveedor; se usa uno gratuito.
MODELO="opencode/big-pickle"

echo "$(date --iso-8601=seconds) Inicio de la postulación diaria" > "$LOG"
opencode run --auto --archived --model "$MODELO" --title "postulación diaria $FECHA" "$MODO" >> "$LOG" 2>&1
echo "$(date --iso-8601=seconds) Fin de la postulación diaria" >> "$LOG"
