#!/bin/bash

# Remove apenas o CSV gerado pelas leituras do sensor.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CSV_PATH="$SCRIPT_DIR/../runtime-data/data.csv"

echo "=== Limpeza do CSV ==="

if [ -f "$CSV_PATH" ]; then
    echo "Removendo arquivo CSV..."
    echo "date,time,temperature,pressure,humidity" > "$CSV_PATH"
    echo "CSV removido com sucesso!"
else
    echo "CSV não encontrado em $CSV_PATH"
fi

echo ""
echo "O CSV será preenchido novamente na próxima leitura do sensor."
