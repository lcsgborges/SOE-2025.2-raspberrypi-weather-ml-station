#!/bin/bash

# Instala dependências, compila o coletor e registra o serviço systemd.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
SERVICE_FILE="/etc/systemd/system/bme280.service"

echo "╔═══════════════════════════════════════════════╗"
echo "║  Instalação Automática - Servidor BME280      ║"
echo "║  Raspberry Pi 3 Model B                       ║"
echo "╚═══════════════════════════════════════════════╝"
echo ""

if [ ! -f /proc/device-tree/model ]; then
    echo "Aviso: Pode não estar rodando em uma Raspberry Pi"
fi

echo "[1/7] Instalando dependências..."
sudo apt-get update -qq
sudo apt-get install -y git build-essential g++ i2c-tools net-tools > /dev/null 2>&1

echo "[2/7] Instalando WiringPi..."
if [ ! -d "/tmp/WiringPi" ]; then
    cd /tmp
    git clone https://github.com/WiringPi/WiringPi.git > /dev/null 2>&1
    cd WiringPi
    sudo ./build > /dev/null 2>&1
fi

echo "[3/7] Habilitando I2C..."
sudo raspi-config nonint do_i2c 0
sudo usermod -a -G i2c pi

echo "[4/7] Criando diretórios..."
mkdir -p "$PROJECT_ROOT/app/runtime-data"

echo "[5/7] Compilando servidor..."
cd "$SCRIPT_DIR"
make clean > /dev/null 2>&1
make > /dev/null 2>&1

if [ ! -f "./bme280_server" ]; then
    echo "Erro na compilação!"
    exit 1
fi

echo "[6/7] Configurando inicialização automática..."
sed "s|@PROJECT_ROOT@|$PROJECT_ROOT|g" bme280.service | sudo tee "$SERVICE_FILE" > /dev/null
sudo systemctl daemon-reload
sudo systemctl enable bme280.service

echo "[7/7] Configurando scripts..."
chmod +x setup_rpi.sh start_server.sh check_status.sh stop_and_clean.sh clear_csv.sh

echo ""
echo "Instalação concluída com sucesso!"
echo ""
echo "═══════════════════════════════════════════════════"
echo "  PRÓXIMOS PASSOS:"
echo "═══════════════════════════════════════════════════"
echo ""
echo "OPÇÃO 1 - Iniciar automaticamente no boot:"
echo "  sudo reboot"
echo ""
echo "OPÇÃO 2 - Iniciar agora manualmente:"
echo "  ./start_server.sh"
echo ""
echo "Para verificar se está rodando:"
echo "  ./check_status.sh"
echo ""
echo "═══════════════════════════════════════════════════"
