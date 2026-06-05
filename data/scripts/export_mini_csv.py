"""Exporta uma amostra reduzida do dataset2 para testes dos modelos."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


ROOT_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE = ROOT_DIR / "data" / "processed" / "dataset2.csv"
OUTPUT_FILE = ROOT_DIR / "ml" / "scripts" / "mini.csv"
DEFAULT_ROWS = 240

TEMPERATURE_COLUMNS = {
    "ins": "TEMPERATURA DO AR - BULBO SECO, HORARIA (C)",
    "min": "TEMPERATURA MINIMA NA HORA ANT. (AUT) (C)",
    "max": "TEMPERATURA MAXIMA NA HORA ANT. (AUT) (C)",
}


def export_sample(input_file: Path, output_file: Path, rows: int) -> None:
    df = pd.read_csv(input_file, parse_dates=[0], date_format="%Y-%m-%d")
    sample = df[list(TEMPERATURE_COLUMNS.values())].head(rows)
    sample = sample.rename(
        columns={source: alias for alias, source in TEMPERATURE_COLUMNS.items()}
    )
    sample.to_csv(output_file, index=False)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Exporta as primeiras linhas de temperatura do dataset2."
    )
    parser.add_argument("-i", "--input", type=Path, default=INPUT_FILE)
    parser.add_argument("-o", "--output", type=Path, default=OUTPUT_FILE)
    parser.add_argument("-n", "--rows", type=int, default=DEFAULT_ROWS)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    export_sample(args.input, args.output, args.rows)


if __name__ == "__main__":
    main()
