# Raspberry Pi Weather ML Station

Projeto de uma estação meteorológica embarcada baseada em Raspberry Pi e sensor BME280, capaz de coletar dados ambientais, armazenar leituras em CSV, disponibilizar informações por meio de uma interface web local e executar modelos de machine learning para predição de temperatura.

## Sobre o projeto

Este projeto propõe uma solução de baixo custo para coleta e análise de dados meteorológicos, com foco em aplicações de monitoramento climático local.

O sistema utiliza um sensor BME280 conectado a uma Raspberry Pi para realizar leituras de temperatura, umidade e pressão atmosférica. Os dados coletados são armazenados localmente em arquivos CSV e disponibilizados por meio de uma interface web. Além disso, o projeto inclui modelos computacionais treinados para realizar predições de temperatura em janelas futuras de 24 horas e 120 horas.

## Funcionalidades

* Coleta de dados ambientais com sensor BME280
* Comunicação via protocolo I2C
* Armazenamento das leituras em arquivos CSV
* Servidor HTTP local para disponibilização dos dados
* Dashboard web para visualização das medições
* Modelos de machine learning para predição de temperatura
* Scripts auxiliares para execução e gerenciamento do sistema na Raspberry Pi

## Tecnologias utilizadas

* Raspberry Pi 3 Model B
* Sensor BME280
* C++
* Python
* TensorFlow/Keras
* HTML5
* CSS3
* JavaScript
* CSV
* I2C
* Linux/systemd

## Arquitetura geral

O sistema é dividido em três partes principais:

### 1. Coleta embarcada de dados

Responsável pela comunicação com o sensor BME280, leitura dos dados ambientais e armazenamento das medições em arquivos CSV.

### 2. Visualização web

Interface web local que permite acompanhar os dados coletados pelo sensor de forma simples e acessível.

### 3. Predição com machine learning

Modelos treinados em Python para analisar séries temporais de temperatura e gerar previsões futuras.

## Componentes principais

* `SensorBME280`: módulo responsável pela comunicação com o sensor.
* `CSVLogger`: módulo responsável pelo registro das leituras em arquivo CSV.
* `HTTPServer`: servidor responsável por disponibilizar os dados coletados.
* `model/python/`: scripts relacionados ao treinamento e execução dos modelos de predição.
* `src/web/`: arquivos da interface web.

## Modelos de predição

O projeto conta com dois modelos principais:

* `t24v1.keras`: modelo para predição de temperatura das próximas 24 horas.
* `t120v1.keras`: modelo para predição de temperatura das próximas 120 horas.

Os modelos foram desenvolvidos com base em dados meteorológicos históricos e utilizados para avaliar a viabilidade de executar inferências diretamente na Raspberry Pi.

## Como executar

Clone o repositório:

```bash
git clone https://github.com/lcsgborges/raspberrypi-weather-ml-station.git
cd raspberrypi-weather-ml-station
```

Crie e ative um ambiente virtual Python:

```bash
python3 -m venv venv
source venv/bin/activate
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

Execute o servidor de predição, caso deseje utilizar os modelos de machine learning:

```bash
python model/python/prediction_server.py
```

Para executar a aplicação embarcada na Raspberry Pi, verifique os scripts auxiliares disponíveis no diretório do projeto, como:

```bash
./start_server.sh
./check_status.sh
./stop_and_clean.sh
./clear_csv.sh
```

## Resultados

O projeto demonstrou a viabilidade de coletar dados meteorológicos com uma Raspberry Pi e utilizar modelos de machine learning para realizar predições de temperatura.

A execução dos modelos diretamente na placa também foi avaliada, indicando que é possível realizar inferências mesmo em um ambiente com recursos computacionais limitados.

## Limitações e melhorias futuras

Alguns pontos ainda podem ser evoluídos:

* Melhorar a precisão dos modelos de predição
* Integrar completamente o dashboard web com as predições dos modelos
* Adicionar tratamento para médias horárias
* Utilizar também dados de pressão e umidade nos modelos
* Desenvolver uma estrutura física mais robusta para uso em ambiente externo
* Melhorar a estabilidade da conexão física do sensor

## Autores

- Lucas Guimarães Borges
- Ryan Salles
  
## Licença

Este projeto está disponível para fins educacionais e experimentais.
