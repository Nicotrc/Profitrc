#!/usr/bin/env bash
# PROFITRC v2 — build & run locally with Docker
# Usage: ./deploy-local.sh [--rebuild] [--logs]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

REBUILD=false
FOLLOW_LOGS=false
for arg in "$@"; do
  case "$arg" in
    --rebuild) REBUILD=true ;;
    --logs)    FOLLOW_LOGS=true ;;
    -h|--help)
      echo "Usage: $0 [--rebuild] [--logs]"
      echo "  --rebuild  Force docker compose build --no-cache"
      echo "  --logs     Follow container logs after start"
      exit 0
      ;;
  esac
done

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker non trovato. Installa Docker Desktop e riprova."
  exit 1
fi

mkdir -p data
touch profitrc.log 2>/dev/null || true

if [ -f .env ]; then
  echo "Caricamento variabili da .env"
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

BUILD_ARGS=()
if $REBUILD; then
  BUILD_ARGS+=(--no-cache)
fi

echo "=== Build immagine PROFITRC ==="
docker compose build "${BUILD_ARGS[@]}"

echo "=== Libera porta 8080 (container vecchi) ==="
for cid in $(docker ps -q --filter "publish=8080"); do
  name=$(docker inspect -f '{{.Name}}' "$cid" | tr -d '/')
  echo "  Stop container $name ($cid) sulla porta 8080"
  docker stop "$cid" >/dev/null || true
done

echo "=== Avvio container (porta 8080) ==="
docker compose down 2>/dev/null || true
docker compose up -d --force-recreate

echo "Attendo healthcheck API..."
for i in $(seq 1 30); do
  if curl -sf "http://localhost:8080/api/regime" >/dev/null 2>&1; then
    echo "API pronta su http://localhost:8080"
    break
  fi
  sleep 2
  if [ "$i" -eq 30 ]; then
    echo "Timeout: API non risponde. Log:"
    docker compose logs --tail=40
    exit 1
  fi
done

echo ""
echo "=== Test rapidi ==="
echo "Regime:"
curl -s "http://localhost:8080/api/regime" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f\"  {d.get('regime')} score={d.get('score')}\")" || true

echo "Analyze ACHV:"
curl -s "http://localhost:8080/api/analyze/ACHV" | python3 -c "
import sys, json
d = json.load(sys.stdin)
sc = d.get('scorecard', {})
print(f\"  verdict={sc.get('verdict')} total={sc.get('total')}\")
r = d.get('risk', {})
print(f\"  entry={r.get('entry_mid')} stop={r.get('stop_loss')} T1={r.get('target1')}\")
" || echo "  (analyze failed — vedi logs)"

echo ""
echo "UI:  http://localhost:8080"
echo "API: http://localhost:8080/api/regime"
echo ""
echo "Scan con bypass NO_TRADE:"
echo "  curl -X POST 'http://localhost:8080/api/scan/2?bypass_regime=true' -H 'Content-Type: application/json' -d '{\"capital\":10000}'"
echo ""

if $FOLLOW_LOGS; then
  docker compose logs -f
fi
