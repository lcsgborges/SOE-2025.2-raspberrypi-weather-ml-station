"""Servidor HTTP para expor predições de temperatura dos modelos Keras."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

import numpy as np
import pandas as pd
import tensorflow as tf


ROOT_DIR = Path(__file__).resolve().parents[2]
MODEL_DIR = ROOT_DIR / "ml" / "models"
DATA_CSV_PATH = ROOT_DIR / "app" / "runtime-data" / "data.csv"

CONV_WIDTH = 3
PREDICTION_PORT = 5000


@dataclass(frozen=True)
class ModelConfig:
    path: Path
    input_width: int
    feature_order: tuple[str, str, str]


MODEL_CONFIGS = {
    "24h": ModelConfig(
        path=MODEL_DIR / "t24v1.keras",
        input_width=24,
        feature_order=("ins", "max", "min"),
    ),
    "120h": ModelConfig(
        path=MODEL_DIR / "t120v1.keras",
        input_width=120,
        feature_order=("ins", "min", "max"),
    ),
}

models: dict[str, tf.keras.Model | None] = {"24h": None, "120h": None}
last_predictions = {
    "temp_24h": None,
    "temp_120h": None,
    "timestamp": None,
    "status": "not_ready",
    "message": "Aguardando dados suficientes",
}


def custom(x):
    """Função usada pelo modelo t120v1.keras ao desserializar a camada Lambda."""
    return x[:, -CONV_WIDTH:, :]


def load_models() -> None:
    tf.keras.config.enable_unsafe_deserialization()

    for name, config in MODEL_CONFIGS.items():
        try:
            if not config.path.exists():
                print(f"[AVISO] Modelo {name} não encontrado: {config.path}")
                continue

            models[name] = tf.keras.models.load_model(
                config.path,
                custom_objects={"custom": custom},
            )
            print(f"[OK] Modelo {name} carregado: {config.path}")
        except Exception as exc:
            models[name] = None
            print(f"[ERRO] Falha ao carregar modelo {name}: {exc}")


def read_sensor_temperatures() -> np.ndarray | None:
    if not DATA_CSV_PATH.exists():
        print(f"[ERRO] Arquivo não encontrado: {DATA_CSV_PATH}")
        return None

    try:
        df = pd.read_csv(DATA_CSV_PATH)
    except Exception as exc:
        print(f"[ERRO] Falha ao ler CSV: {exc}")
        return None

    if df.empty:
        print("[AVISO] CSV vazio")
        return None

    temp_column = next((col for col in df.columns if "temp" in col.lower()), None)
    if temp_column is None and len(df.columns) >= 3:
        temp_column = df.columns[2]

    if temp_column is None:
        print("[ERRO] Coluna de temperatura não encontrada")
        return None

    return df[temp_column].astype(float).to_numpy()


def build_feature_matrix(
    temperatures: np.ndarray,
    input_width: int,
    feature_order: tuple[str, str, str],
) -> tuple[np.ndarray, float, float] | None:
    if len(temperatures) < input_width:
        return None

    temps = temperatures[-input_width:]
    window_size = min(24, len(temps))

    features = {
        "ins": temps,
        "max": np.array(
            [np.max(temps[max(0, i - window_size) : i + 1]) for i in range(len(temps))]
        ),
        "min": np.array(
            [np.min(temps[max(0, i - window_size) : i + 1]) for i in range(len(temps))]
        ),
    }

    matrix = np.column_stack([features[name] for name in feature_order])
    mean = float(matrix.mean())
    std = float(matrix.std()) or 1.0
    normalized = (matrix - mean) / std

    return normalized.reshape(1, input_width, 3), mean, std


def predict_temperature(
    model: tf.keras.Model,
    temperatures: np.ndarray,
    config: ModelConfig,
) -> float | None:
    prepared = build_feature_matrix(
        temperatures,
        input_width=config.input_width,
        feature_order=config.feature_order,
    )

    if prepared is None:
        return None

    input_batch, mean, std = prepared
    prediction = model.predict(input_batch, verbose=0)
    denormalized = (prediction * std) + mean
    return float(np.mean(denormalized[0, :, 0]))


def make_predictions() -> dict:
    global last_predictions

    temperatures = read_sensor_temperatures()
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

    if temperatures is None:
        last_predictions = {
            "temp_24h": None,
            "temp_120h": None,
            "timestamp": timestamp,
            "status": "error",
            "message": "Não foi possível ler os dados do sensor",
        }
        return last_predictions

    results: dict[str, float | None] = {"24h": None, "120h": None}
    messages: list[str] = []

    for name, config in MODEL_CONFIGS.items():
        model = models.get(name)

        if model is None:
            messages.append(f"modelo {name} indisponível")
            continue

        if len(temperatures) < config.input_width:
            messages.append(
                f"{name}: {len(temperatures)}/{config.input_width} leituras"
            )
            continue

        try:
            results[name] = predict_temperature(model, temperatures, config)
            if results[name] is not None:
                print(f"[OK] Predição {name}: {results[name]:.2f} °C")
        except Exception as exc:
            messages.append(f"{name}: {exc}")
            print(f"[ERRO] Predição {name} falhou: {exc}")

    has_prediction = any(value is not None for value in results.values())
    status = "ok" if has_prediction else "insufficient_data"
    message = "Predições atualizadas com sucesso" if has_prediction else "; ".join(messages)

    last_predictions = {
        "temp_24h": round(results["24h"], 2) if results["24h"] is not None else None,
        "temp_120h": round(results["120h"], 2) if results["120h"] is not None else None,
        "timestamp": timestamp,
        "status": status,
        "message": message or "Dados insuficientes para predição",
        "data_points": len(temperatures),
    }
    return last_predictions


class PredictionHandler(BaseHTTPRequestHandler):
    def set_headers(self, content_type: str = "application/json") -> None:
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_OPTIONS(self) -> None:
        self.set_headers()

    def do_GET(self) -> None:
        if self.path in {"/api/predict", "/predict"}:
            self.set_headers()
            self.write_json(make_predictions())
            return

        if self.path in {"/api/status", "/status"}:
            self.set_headers()
            self.write_json(
                {
                    "server": "running",
                    "model_24h": models["24h"] is not None,
                    "model_120h": models["120h"] is not None,
                    "data_path": str(DATA_CSV_PATH),
                    "last_predictions": last_predictions,
                }
            )
            return

        if self.path == "/":
            self.set_headers("text/html; charset=utf-8")
            self.wfile.write(
                """
                <html>
                <head><title>Servidor de Predição</title></head>
                <body>
                    <h1>Servidor de Predição de Temperatura</h1>
                    <ul>
                        <li><a href="/api/predict">/api/predict</a></li>
                        <li><a href="/api/status">/api/status</a></li>
                    </ul>
                </body>
                </html>
                """.encode("utf-8")
            )
            return

        self.send_response(404)
        self.end_headers()
        self.wfile.write(b"Not Found")

    def write_json(self, payload: dict) -> None:
        self.wfile.write(json.dumps(payload, ensure_ascii=False).encode("utf-8"))

    def log_message(self, format: str, *args) -> None:
        print(f"[HTTP] {args[0]}")


def run_server(port: int = PREDICTION_PORT) -> None:
    server = HTTPServer(("", port), PredictionHandler)
    print(f"[OK] Servidor de predição rodando em http://localhost:{port}")
    print("[OK] Endpoints: /api/predict, /api/status")
    server.serve_forever()


if __name__ == "__main__":
    print("=" * 50)
    print("Servidor de Predição de Temperatura - BME280 + IA")
    print("=" * 50)
    load_models()
    print("\n[INFO] Fazendo predição inicial...")
    make_predictions()
    print("\n[INFO] Iniciando servidor HTTP...")
    run_server()
