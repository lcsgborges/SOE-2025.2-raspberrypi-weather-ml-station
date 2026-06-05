#!/bin/bash

# Verifica o status do servidor BME280 e do servidor de predições.
set -euo pipefail

echo "=== Status do Servidor BME280 ==="
echo ""

if pgrep -x "bme280_server" > /dev/null; then
    echo "Servidor está RODANDO"

    PID=$(pgrep -x "bme280_server")
    echo "   PID: $PID"
    echo "   Tempo ativo: $(ps -o etime= -p $PID)"

    IP=$(hostname -I | awk '{print $1}')
    echo ""
    echo "Dashboard: http://$IP:8080"
    echo ""

    if netstat -tuln 2>/dev/null | grep -q ":8080"; then
        echo "Porta 8080 está aberta"
    else
        echo "Porta 8080 pode não estar acessível"
    fi
else
    echo "Servidor NÃO está rodando"
    echo ""
    echo "Para iniciar:"
    echo "  ./start_server.sh"
    echo ""
    echo "Ou verifique o serviço systemd:"
    echo "  sudo systemctl status bme280"
    echo ""
fi

echo ""
echo "--- Status do Servidor de Predições ---"
if pgrep -f "prediction_server.py" > /dev/null; then
    PREDICTION_PID=$(pgrep -f "prediction_server.py")
    echo "Servidor de predições: RODANDO"
    echo "   PID: $PREDICTION_PID"
else
    echo "Servidor de predições: INATIVO"
fi

echo ""
echo "--- Status do Serviço Systemd ---"
if systemctl is-enabled bme280.service &>/dev/null; then
    echo "Auto-inicialização: ATIVADA"
else
    echo "Auto-inicialização: DESATIVADA"
fi

if systemctl is-active bme280.service &>/dev/null; then
    echo "Serviço systemd: ATIVO"
else
    echo "Serviço systemd: INATIVO"
fi

echo ""
echo "Comandos úteis:"
echo "  Ver logs completos: tail -f /tmp/bme280.log"
echo "  Ver logs de IA:     tail -f /tmp/prediction_server.log"
echo "  Parar servidor: sudo pkill bme280_server"
echo "  Status systemd: sudo systemctl status bme280"
