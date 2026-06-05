"""Gera o dataset2.csv com dados INMET anuais de 2020 a 2024."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


ROOT_DIR = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = ROOT_DIR / "data" / "raw" / "inmet"
PROCESSED_DATA_DIR = ROOT_DIR / "data" / "processed"

INPUT_FILES = (
    RAW_DATA_DIR / "INMET_CO_DF_A001_BRASILIA_01-01-2020_A_31-12-2020.CSV",
    RAW_DATA_DIR / "INMET_CO_DF_A001_BRASILIA_01-01-2021_A_31-12-2021.CSV",
    RAW_DATA_DIR / "INMET_CO_DF_A001_BRASILIA_01-01-2022_A_31-12-2022.CSV",
    RAW_DATA_DIR / "INMET_CO_DF_A001_BRASILIA_01-01-2023_A_31-12-2023.CSV",
    RAW_DATA_DIR / "INMET_CO_DF_A001_BRASILIA_01-01-2024_A_31-12-2024.CSV",
)

OUTPUT_FILE = PROCESSED_DATA_DIR / "dataset2.csv"
DATE_FORMAT = "%Y/%m/%d"
RADIATION_COLUMN = "RADIACAO GLOBAL (Kj/m2)"
DATE_TIME_COLUMNS = {"data", "hora", "hora (utc)"}


def is_date_time_column(column: str) -> bool:
    return column.strip().lower() in DATE_TIME_COLUMNS


def load_inmet_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(
        path,
        sep=";",
        decimal=",",
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


def print_file_summaries(input_files: tuple[Path, ...] = INPUT_FILES) -> None:
    for path in input_files:
        df = load_inmet_csv(path)
        print(f"\n{path.name}")
        print(df.info())
        print(df.describe())


def print_dataset_summary(df: pd.DataFrame) -> None:
    print(df.info())
    print(df.describe())


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Processa os CSVs INMET de 2020-2024 e gera dataset2.csv."
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
    parser.add_argument(
        "--inspect-source",
        action="store_true",
        help="Mostra um resumo dos arquivos de entrada e encerra.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.inspect_source:
        print_file_summaries()
        return

    dataset = build_dataset()
    dataset.to_csv(args.output, index=False)

    if args.inspect:
        print_dataset_summary(dataset)


if __name__ == "__main__":
    main()
