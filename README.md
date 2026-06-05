# Raspberry Pi Weather ML Station

Estação meteorológica embarcada com Raspberry Pi e sensor BME280 para coleta de temperatura, pressão e umidade, armazenamento em CSV, visualização em dashboard web local e predição de temperatura com modelos de machine learning.

## Sobre o Projeto

O projeto propõe uma solução de baixo custo para monitoramento climático local. A Raspberry Pi lê o sensor BME280 via I2C, registra as medições em CSV, disponibiliza os dados por um servidor HTTP local e permite executar modelos Keras para estimar temperaturas futuras.

Para entender melhor a motivação, arquitetura, escolhas de hardware/software e resultados do projeto, leia o relatório final em [`relatorio.pdf`](relatorio.pdf). Os arquivos editáveis usados na elaboração do relatório estão em [`docs/report-source/`](docs/report-source/).

## Funcionalidades

- Coleta de temperatura, pressão e umidade com o sensor BME280.
- Comunicação I2C na Raspberry Pi.
- Registro das leituras em [`app/runtime-data/data.csv`](app/runtime-data/data.csv).
- Servidor HTTP local para servir os dados coletados.
- Dashboard web em [`app/web/`](app/web/).
- Modelos Keras para predição de temperatura em janelas de 24 e 120 passos.
- Scripts para tratamento dos dados históricos do INMET.

## Estrutura

```text
relatorio.pdf          Relatório final do projeto
app/                   Aplicação embarcada, dashboard web e dados de runtime
app/embedded/          Código C++ do sensor, servidor HTTP e scripts da Raspberry Pi
app/runtime-data/      CSV gerado pelo coletor embarcado
app/web/               Dashboard web
data/                  Dados históricos do INMET e scripts de processamento
data/raw/inmet/        CSVs brutos do INMET
data/processed/        Datasets tratados
docs/                  Referências, datasheets e fontes do relatório
ml/                    Modelos treinados e scripts Python de treinamento/inferência
```

## Tecnologias

- Raspberry Pi 3 Model B
- Sensor BME280
- C++17
- Python
- TensorFlow/Keras
- Pandas e NumPy
- HTML, CSS e JavaScript
- Linux/systemd

## Modelos

- [`ml/models/t24v1.keras`](ml/models/t24v1.keras): predição de temperatura para 24 passos.
- [`ml/models/t120v1.keras`](ml/models/t120v1.keras): predição de temperatura para 120 passos.

Os scripts relacionados aos modelos ficam em [`ml/scripts/`](ml/scripts/). O treinamento usa dados históricos tratados em [`data/processed/dataset1.csv`](data/processed/dataset1.csv) e [`data/processed/dataset2.csv`](data/processed/dataset2.csv).

## Execução em Ambiente Python

Crie e ative um ambiente virtual:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

Execute o servidor de predição:

```bash
python ml/scripts/prediction_server.py
```

Treine novamente o modelo de 24 passos, se necessário:

```bash
python ml/scripts/train_model.py
```

Endpoints principais:

- `http://localhost:5000/api/predict`
- `http://localhost:5000/api/status`

## Tratamento de Dados

Gerar o dataset de 2023-2024:

```bash
python data/scripts/process_2023_2024.py
```

Gerar o dataset de 2020-2024:

```bash
python data/scripts/process_2020_2024.py
```

Exportar a amostra usada para teste do modelo de 120 passos:

```bash
python data/scripts/export_mini_csv.py
```

## Execução na Raspberry Pi

Na Raspberry Pi, acesse a pasta do coletor:

```bash
cd app/embedded
chmod +x setup_rpi.sh start_server.sh check_status.sh stop_and_clean.sh clear_csv.sh
./setup_rpi.sh
```

Após reiniciar, o dashboard pode ser acessado na rede local:

```bash
http://<IP_DA_RPI>:8080
```

Comandos úteis:

```bash
./start_server.sh
./check_status.sh
./stop_and_clean.sh
./clear_csv.sh
```

## Resultados

O projeto demonstrou a viabilidade de coletar dados meteorológicos com uma Raspberry Pi e utilizar modelos de machine learning para predições de temperatura. A execução dos modelos na placa também foi avaliada, indicando que inferências simples são possíveis mesmo em um ambiente com recursos computacionais limitados.

## Limitações e Melhorias Futuras

- Melhorar a precisão dos modelos de predição.
- Integrar completamente o dashboard web com as predições dos modelos.
- Adicionar tratamento específico para médias horárias.
- Usar pressão e umidade como entradas adicionais nos modelos.
- Desenvolver uma estrutura física mais robusta para uso externo.
- Melhorar a estabilidade da conexão física do sensor.

## Autores

- Lucas Guimarães Borges
- Ryan Salles

## Licença

Este projeto está disponível para fins educacionais e experimentais.
