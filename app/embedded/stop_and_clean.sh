#!/bin/bash

# Para os serviços do projeto e limpa artefatos gerados localmente.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== Parando Servidores BME280 + Predições ==="
echo ""

# 1. Parar o processo BME280
echo "[1] Parando processo bme280_server..."
if pgrep -x "bme280_server" > /dev/null; then
    sudo pkill bme280_server
    sleep 2
    if pgrep -x "bme280_server" > /dev/null; then
        echo "Processo ainda rodando, forçando..."
        sudo pkill -9 bme280_server
    fi
    echo "Processo BME280 parado"
else
    echo "Processo BME280 não estava rodando"
fi

# 2. Parar o servidor de predições Python
echo ""
echo "[2] Parando servidor de predições..."
if pgrep -f "prediction_server.py" > /dev/null; then
    pkill -f "prediction_server.py"
    sleep 1
    if pgrep -f "prediction_server.py" > /dev/null; then
        echo "Processo ainda rodando, forçando..."
        pkill -9 -f "prediction_server.py"
    fi
    echo "Servidor de predições parado"
else
    echo "Servidor de predições não estava rodando"
fi

# 3. Parar e desabilitar serviço systemd
echo ""
echo "[3] Parando serviço systemd..."
if systemctl is-active bme280.service &>/dev/null; then
    sudo systemctl stop bme280.service
    echo "Serviço parado"
else
    echo "Serviço não estava ativo"
fi

if systemctl is-enabled bme280.service &>/dev/null; then
    sudo systemctl disable bme280.service
    echo "Auto-inicialização desabilitada"
else
    echo "Auto-inicialização já estava desabilitada"
fi

# 4. Remover serviço do systemd (opcional)
echo ""
echo "[4] Removendo configuração do systemd..."
if [ -f /etc/systemd/system/bme280.service ]; then
    sudo rm /etc/systemd/system/bme280.service
    sudo systemctl daemon-reload
    echo "Configuração removida"
else
    echo "Configuração não encontrada"
fi

# 5. Limpar executável (opcional)
echo ""
echo "[5] Limpando executável..."
if [ -f "./bme280_server" ]; then
    make clean
    echo "Executável removido"
else
    echo "Executável não encontrado"
fi

# 6. Limpar logs temporários
echo ""
echo "[6] Limpando logs temporários..."
rm -f /tmp/bme280.log /tmp/prediction_server.log 2>/dev/null
echo "Logs removidos"

echo ""
echo "Limpeza concluída!"
echo ""
echo "Para reinstalar:"
echo "  ./setup_rpi.sh"
echo ""
