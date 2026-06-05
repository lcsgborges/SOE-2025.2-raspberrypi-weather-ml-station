"""Carrega o modelo de 120h e gera um gráfico de predição para uma amostra."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import tensorflow as tf


BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR.parent / "models" / "t120v1.keras"
SAMPLE_CSV = BASE_DIR / "mini.csv"
CONV_WIDTH = 3
INPUT_WIDTH = 120
FEATURE_COLUMNS = ("ins", "min", "max")


def custom(x):
    """Função usada pelo modelo salvo na camada Lambda."""
    return x[:, -CONV_WIDTH:, :]


def load_sample(path: Path, rows: int = INPUT_WIDTH) -> tuple[np.ndarray, float, float]:
    df = pd.read_csv(path)
    values = df.loc[: rows - 1, FEATURE_COLUMNS].to_numpy(dtype=np.float32)

    mean = float(values.mean())
    std = float(values.std()) or 1.0
    normalized = (values - mean) / std

    return normalized.reshape(1, rows, len(FEATURE_COLUMNS)), mean, std


def plot_prediction(values: np.ndarray, output_path: Path) -> None:
    series = values.reshape(-1, values.shape[-1])

    for index, label in enumerate(FEATURE_COLUMNS):
        plt.plot(series[:, index], label=label)

    plt.xlabel("Passo previsto")
    plt.ylabel("Temperatura (C)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Testa o carregamento do modelo t120.")
    parser.add_argument("-m", "--model", type=Path, default=MODEL_PATH)
    parser.add_argument("-i", "--input", type=Path, default=SAMPLE_CSV)
    parser.add_argument("-o", "--output", type=Path, default=BASE_DIR / "prediction.png")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    tf.keras.config.enable_unsafe_deserialization()
    model = tf.keras.models.load_model(args.model, custom_objects={"custom": custom})

    input_batch, mean, std = load_sample(args.input)
    prediction = model.predict(input_batch, verbose=0)
    prediction = (prediction * std) + mean

    plot_prediction(prediction, args.output)


if __name__ == "__main__":
    main()
