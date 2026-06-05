# Dados do Sensor

`data.csv` é preenchido automaticamente pelo coletor BME280 durante a execução na Raspberry Pi.

O arquivo versionado mantém apenas o cabeçalho esperado pela interface web e pelo servidor de predição:

```csv
date,time,temperature,pressure,humidity
```

Leituras reais e logs de execução não devem ser commitados.
