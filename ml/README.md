# Machine Learning

Esta pasta contém os modelos Keras treinados e os scripts auxiliares usados para treinamento, inferência e testes rápidos.

## Arquivos

- `models/t24v1.keras`: modelo para predição de temperatura em 24 passos.
- `models/t120v1.keras`: modelo para predição de temperatura em 120 passos.
- `scripts/train_model.py`: script de treinamento do modelo de 24 passos.
- `scripts/prediction_server.py`: servidor HTTP que carrega os modelos e expõe endpoints de predição.
- `scripts/predict_sample.py`: teste de carregamento e geração de gráfico para o modelo de 120 passos.
- `scripts/mini.csv`: amostra reduzida usada nos testes do modelo de 120 passos.

## Observações

Os modelos dependem da mesma organização de colunas usada durante o treinamento. Antes de retreinar ou substituir um arquivo `.keras`, confira os scripts de tratamento em `data/scripts/` e os nomes das colunas usados em `ml/scripts/`.

O treinamento com TensorFlow pode consumir bastante memória e CPU. Para novos experimentos, prefira rodar em uma máquina com recursos suficientes ou em ambiente como Google Colab.
