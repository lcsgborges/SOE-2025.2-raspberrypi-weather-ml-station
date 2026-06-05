"""Treina um modelo convolucional simples para previsão de temperatura."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import tensorflow as tf


ROOT_DIR = Path(__file__).resolve().parents[2]
DEFAULT_DATASET = ROOT_DIR / "data" / "processed" / "dataset1.csv"
DEFAULT_OUTPUT = ROOT_DIR / "ml" / "models" / "t24v1.keras"

FEATURE_COLUMNS = ("Temp. Ins. (C)", "Temp. Max. (C)", "Temp. Min. (C)")
INPUT_WIDTH = 24
OUTPUT_STEPS = 24
CONV_WIDTH = 3
BATCH_SIZE = 32
MAX_EPOCHS = 20
PATIENCE = 5


def load_features(dataset_path: Path) -> pd.DataFrame:
    df = pd.read_csv(dataset_path, parse_dates=[0], date_format="%Y-%m-%d")
    return df.loc[:, FEATURE_COLUMNS]


def split_dataframe(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    total_rows = len(df)
    train_df = df.iloc[: int(total_rows * 0.7)]
    val_df = df.iloc[int(total_rows * 0.7) : int(total_rows * 0.9)]
    test_df = df.iloc[int(total_rows * 0.9) :]
    return train_df, val_df, test_df


def normalize_splits(
    train_df: pd.DataFrame,
    val_df: pd.DataFrame,
    test_df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    mean = train_df.mean()
    std = train_df.std().replace(0, 1)
    return (train_df - mean) / std, (val_df - mean) / std, (test_df - mean) / std


def make_window_dataset(
    data: pd.DataFrame,
    input_width: int,
    label_width: int,
    shift: int,
    batch_size: int = BATCH_SIZE,
    shuffle: bool = True,
) -> tf.data.Dataset:
    values = np.array(data, dtype=np.float32)
    total_window_size = input_width + shift
    label_start = total_window_size - label_width

    dataset = tf.keras.utils.timeseries_dataset_from_array(
        data=values,
        targets=None,
        sequence_length=total_window_size,
        sequence_stride=1,
        shuffle=shuffle,
        batch_size=batch_size,
    )

    def split_window(features):
        inputs = features[:, :input_width, :]
        labels = features[:, label_start:, :]
        inputs.set_shape([None, input_width, None])
        labels.set_shape([None, label_width, None])
        return inputs, labels

    return dataset.map(split_window)


def build_model(
    input_width: int,
    output_steps: int,
    feature_count: int,
    conv_width: int = CONV_WIDTH,
) -> tf.keras.Model:
    crop_left = input_width - conv_width

    model = tf.keras.Sequential(
        [
            tf.keras.layers.Input(shape=(input_width, feature_count)),
            tf.keras.layers.Cropping1D(cropping=(crop_left, 0)),
            tf.keras.layers.Conv1D(256, activation="relu", kernel_size=conv_width),
            tf.keras.layers.Dense(
                output_steps * feature_count,
                kernel_initializer=tf.initializers.zeros(),
            ),
            tf.keras.layers.Reshape([output_steps, feature_count]),
        ]
    )

    model.compile(
        loss=tf.losses.MeanSquaredError(),
        optimizer=tf.optimizers.Adam(),
        metrics=[tf.metrics.MeanAbsoluteError()],
    )
    return model


def train_model(args: argparse.Namespace) -> tf.keras.Model:
    features = load_features(args.dataset)
    train_df, val_df, test_df = normalize_splits(*split_dataframe(features))

    train_ds = make_window_dataset(
        train_df,
        input_width=args.input_width,
        label_width=args.output_steps,
        shift=args.output_steps,
    )
    val_ds = make_window_dataset(
        val_df,
        input_width=args.input_width,
        label_width=args.output_steps,
        shift=args.output_steps,
        shuffle=False,
    )
    test_ds = make_window_dataset(
        test_df,
        input_width=args.input_width,
        label_width=args.output_steps,
        shift=args.output_steps,
        shuffle=False,
    )

    model = build_model(
        input_width=args.input_width,
        output_steps=args.output_steps,
        feature_count=len(FEATURE_COLUMNS),
    )

    model.fit(
        train_ds,
        epochs=args.epochs,
        validation_data=val_ds,
        callbacks=[
            tf.keras.callbacks.EarlyStopping(
                monitor="val_loss",
                patience=args.patience,
                mode="min",
            )
        ],
    )

    print("Validação:", model.evaluate(val_ds, verbose=0, return_dict=True))
    print("Teste:", model.evaluate(test_ds, verbose=0, return_dict=True))

    return model


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Treina um modelo de série temporal.")
    parser.add_argument("-d", "--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("-o", "--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--input-width", type=int, default=INPUT_WIDTH)
    parser.add_argument("--output-steps", type=int, default=OUTPUT_STEPS)
    parser.add_argument("--epochs", type=int, default=MAX_EPOCHS)
    parser.add_argument("--patience", type=int, default=PATIENCE)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    model = train_model(args)
    model.save(args.output)
    print(f"Modelo salvo em: {args.output}")


if __name__ == "__main__":
    main()
