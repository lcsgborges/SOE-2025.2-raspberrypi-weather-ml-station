#!/bin/bash

# Inicia o servidor BME280 e, quando disponível, o servidor de predições.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
ML_DIR="$PROJECT_ROOT/ml"
PREDICTION_SERVER="$ML_DIR/scripts/prediction_server.py"
VENV_DIRS=("$PROJECT_ROOT/.venv" "$ML_DIR/.venv" "$ML_DIR/venv")

cd "$SCRIPT_DIR"

echo "=== Servidor BME280 + Predições IA ==="

if [ ! -f "./bme280_server" ]; then
    echo "Compilando servidor BME280..."
    make
fi

mkdir -p ../runtime-data

if ! ls /dev/i2c-* >/dev/null 2>&1; then
    echo "I2C não detectado. Execute: sudo raspi-config -> Interface Options -> I2C"
    exit 1
fi

echo "Iniciando servidor BME280 em background..."
sudo nohup ./bme280_server > /tmp/bme280.log 2>&1 &
BME280_PID=$!

sleep 2

if command -v python3 >/dev/null 2>&1; then
    if [ -f "$PREDICTION_SERVER" ]; then
        for VENV_DIR in "${VENV_DIRS[@]}"; do
            if [ -f "$VENV_DIR/bin/activate" ]; then
                # shellcheck disable=SC1091
                source "$VENV_DIR/bin/activate"
                break
            fi
        done

        echo "Iniciando servidor de predições (IA) em background..."
        nohup python3 "$PREDICTION_SERVER" > /tmp/prediction_server.log 2>&1 &
        PREDICTION_PID=$!
        sleep 2
        
        if ps -p $PREDICTION_PID > /dev/null 2>&1; then
            echo "Servidor de predições iniciado (PID: $PREDICTION_PID)"
        else
            echo "[AVISO] Servidor de predições falhou ao iniciar"
            echo "        Verifique: tail -f /tmp/prediction_server.log"
        fi
    else
        echo "[AVISO] Servidor de predições não encontrado: $PREDICTION_SERVER"
    fi
else
    echo "[AVISO] Python3 não encontrado - servidor de predições não iniciado"
fi

IP=$(hostname -I | awk '{print $1}')

echo ""
echo "Servidores rodando em background!"
echo "BME280 PID: $BME280_PID"
echo ""
echo "Dashboard:  http://$IP:8080"
echo "API Sensor: http://$IP:8080/api/data"
echo "API IA:     http://$IP:5000/api/predict"
echo ""
echo "Comandos úteis:"
echo "  Logs BME280:    tail -f /tmp/bme280.log"
echo "  Logs Predição:  tail -f /tmp/prediction_server.log"
echo "  Parar tudo:     ./stop_and_clean.sh"
echo ""
