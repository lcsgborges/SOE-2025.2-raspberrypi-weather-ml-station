# Servidor BME280 para Raspberry Pi

Coletor C++ para o sensor BME280, com registro em CSV e servidor HTTP local para o dashboard web.

## Requisitos

- Raspberry Pi com I2C habilitado.
- Sensor BME280 conectado via I2C.
- `g++`, `make`, `i2c-tools` e WiringPi.

## Instalação Rápida

Na Raspberry Pi, execute a partir da pasta deste módulo:

```bash
cd app/embedded
chmod +x setup_rpi.sh start_server.sh check_status.sh stop_and_clean.sh clear_csv.sh
./setup_rpi.sh
sudo reboot
```

O `setup_rpi.sh` compila o binário localmente e instala o serviço `bme280.service` com o caminho real do repositório.

## Acesso

No navegador de qualquer dispositivo na mesma rede:

```bash
http://<IP_DA_RPI>:8080
```

Para descobrir o IP da Raspberry Pi:

```bash
hostname -I
```

## Scripts

- `setup_rpi.sh`: instala dependências, compila o servidor e configura systemd.
- `start_server.sh`: inicia o servidor BME280 e o servidor Python de predição, quando disponível.
- `check_status.sh`: verifica processos, portas e serviço systemd.
- `stop_and_clean.sh`: para os serviços e remove artefatos locais.
- `clear_csv.sh`: limpa as leituras e mantém o cabeçalho de `app/runtime-data/data.csv`.

## Systemd

```bash
sudo systemctl status bme280
sudo systemctl stop bme280
sudo systemctl start bme280
sudo systemctl restart bme280
sudo systemctl disable bme280
sudo systemctl enable bme280
sudo journalctl -u bme280 -f
```

## Verificação do Sensor

```bash
sudo i2cdetect -y 1
```

O BME280 deve aparecer em `0x76` ou `0x77`.

## Configurações

- Horário das leituras: Brasília (UTC-3).
- Intervalo de leitura: 60 segundos em `main.cpp`.
- Atualização do dashboard: 60 segundos em `app/web/script.js`.
- Linhas exibidas na tabela: 10 registros recentes.
