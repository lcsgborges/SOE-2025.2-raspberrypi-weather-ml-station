"""Gera o dataset1.csv a partir dos recortes INMET de 2023 e 2024."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


ROOT_DIR = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = ROOT_DIR / "data" / "raw" / "inmet"
PROCESSED_DATA_DIR = ROOT_DIR / "data" / "processed"

INPUT_FILES = (
    RAW_DATA_DIR / "data1-01012023-29062023.csv",
    RAW_DATA_DIR / "data2-30062023-30122023.csv",
    RAW_DATA_DIR / "data3-01012024-29062024.csv",
    RAW_DATA_DIR / "data4-30062024-30122024.csv",
)

OUTPUT_FILE = PROCESSED_DATA_DIR / "dataset1.csv"
DATE_FORMAT = "%d/%m/%Y"
RADIATION_COLUMN = "Radiacao (KJ/m²)"
DATE_TIME_COLUMNS = {"data", "hora (utc)", "hora"}


def is_date_time_column(column: str) -> bool:
    return column.strip().lower() in DATE_TIME_COLUMNS


def load_inmet_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(
        path,
        sep=";",
        decimal=",",
        encoding="utf-8-sig",
        parse_dates=[0],
        date_format=DATE_FORMAT,
    )


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = df.copy()

    if RADIATION_COLUMN in cleaned.columns:
        cleaned[RADIATION_COLUMN] = cleaned[RADIATION_COLUMN].fillna(0)

    for column in cleaned.columns:
        if not is_date_time_column(column):
            cleaned[column] = pd.to_numeric(cleaned[column], errors="coerce")

    numeric_columns = cleaned.select_dtypes(include="number").columns
    cleaned[numeric_columns] = cleaned[numeric_columns].interpolate(
        limit_direction="both"
    )

    return cleaned


def build_dataset(input_files: tuple[Path, ...] = INPUT_FILES) -> pd.DataFrame:
    frames = [clean_dataframe(load_inmet_csv(path)) for path in input_files]
    return pd.concat(frames, ignore_index=True)


def print_dataset_summary(df: pd.DataFrame) -> None:
    print(df.info())
    print(df.describe())


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Processa os CSVs INMET de 2023-2024 e gera dataset1.csv."
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=OUTPUT_FILE,
        help="Arquivo CSV de saída.",
    )
    parser.add_argument(
        "--inspect",
        action="store_true",
        help="Mostra um resumo estatístico após o processamento.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    dataset = build_dataset()
    dataset.to_csv(args.output, index=False)

    if args.inspect:
        print_dataset_summary(dataset)


if __name__ == "__main__":
    main()
