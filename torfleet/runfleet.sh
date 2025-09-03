#!/bin/bash
set -euo pipefail

BASE_DIR="$(cd "$(dirname "$0")" && pwd)"
PID_DIR="$BASE_DIR/pids"
LOG_DIR="$BASE_DIR/log"
DATA_DIR="$BASE_DIR/data/tor"
TORRC_DIR="$BASE_DIR/torrcs"
PRIVOXY_DIR="$BASE_DIR/privoxy_configs"

NUM_INSTANCES=100
BASE_SOCKS_PORT=19050   # Tor SOCKS5
BASE_HTTP_PORT=15000    # Privoxy HTTP

PRIVOXY_BASE_CONFIG="$PRIVOXY_DIR/config"
mkdir -p "$DATA_DIR" "$PID_DIR" "$LOG_DIR" "$TORRC_DIR" "$PRIVOXY_DIR"

command -v tor >/dev/null 2>&1 || { echo "tor not found"; exit 1; }
command -v privoxy >/dev/null 2>&1 || { echo "privoxy not found"; exit 1; }
[[ -f "$PRIVOXY_BASE_CONFIG" ]] || { echo "Missing $PRIVOXY_BASE_CONFIG"; exit 1; }

echo "Starting $NUM_INSTANCES Tor + Privoxy pairs"

for ((i=0; i<NUM_INSTANCES; i++)); do
  socks_port=$((BASE_SOCKS_PORT + i))
  http_port=$((BASE_HTTP_PORT + i))

  inst_dir="$DATA_DIR/tor$i"
  mkdir -p "$inst_dir"

  pid_file="$PID_DIR/tor$i.pid"
  log_notice="$LOG_DIR/tor${i}_notice.log"
  log_warn="$LOG_DIR/tor${i}_warn.log"
  log_err="$LOG_DIR/tor${i}_err.log"
  log_stdout="$LOG_DIR/tor_${i}.stdout.log"
  torrc="$TORRC_DIR/tor$i.torrc"

  cat > "$torrc" <<EOF
SocksPort 127.0.0.1:$socks_port IsolateSOCKSAuth
ClientOnly 1
ControlPort 0
CookieAuthentication 0
DataDirectory $inst_dir
PidFile $pid_file
NewCircuitPeriod 15
MaxCircuitDirtiness 15
NumEntryGuards 8
Log notice file $log_notice
Log warn file $log_warn
Log err file $log_err
EOF

  nohup tor -f "$torrc" > "$log_stdout" 2>&1 &

  sleep 0.1

  privoxy_conf="$PRIVOXY_DIR/config_$http_port"
  cp -f "$PRIVOXY_BASE_CONFIG" "$privoxy_conf"
  {
    echo "forward-socks5t / 127.0.0.1:$socks_port ."
    echo "listen-address 127.0.0.1:$http_port"
  } >> "$privoxy_conf"

  nohup privoxy "$privoxy_conf" > "$LOG_DIR/privoxy_$i.log" 2>&1 &

  sleep 0.1

done

sleep 1

echo "HTTP proxies (Privoxy) running: $(ps aux | grep '[p]rivoxy .*privoxy_configs' | wc -l)"
echo "Tor processes running:           $(ps aux | grep '[t]or' | grep "$DATA_DIR/tor" | wc -l)"

echo "Example HTTP proxy:  http://127.0.0.1:$BASE_HTTP_PORT"
echo "Example SOCKS proxy: socks5h://127.0.0.1:$BASE_SOCKS_PORT"
