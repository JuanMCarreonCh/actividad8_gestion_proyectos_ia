"""
observability_service.py
Servicio Integral de Observabilidad y Monitoreo Proactivo para MexBan.
Coordina telemetría, detección de drift, alertamiento SLO y simulación de incidentes.
"""

import random
import time
from typing import Dict, List, Any
import numpy as np
import pandas as pd

from src.metrics_logger import ObservabilityTelemetry
from src.drift_detector import DriftDetector
from src.alert_engine import SmartAlertEngine
from src.runbook_automation import RunbookAutomationEngine

# Corpus sintético representativo de MexBan
BASELINE_CORPUS = [
    ("Excelente atención en la sucursal Reforma, trámite de tarjeta muy rápido", "Positivo"),
    ("La aplicación móvil funciona muy bien y las transferencias SPEI caen de inmediato", "Positivo"),
    ("Muy contento con mi crédito hipotecario, la tasa fue la mejor del mercado", "Positivo"),
    ("El cajero automático se tragó mi tarjeta de débito en Perisur y nadie me ayuda", "Negativo"),
    ("Pésimo servicio al cliente, llevo 45 minutos esperando en la línea telefónica", "Negativo"),
    ("Me cobraron comisión por manejo de cuenta indebida y la aclaración fue rechazada", "Negativo"),
    ("Fui a recoger mi nuevo token físico a la sucursal del centro", "Neutro"),
    ("Consulté mi estado de cuenta digital desde el portal web", "Neutro"),
    ("El horario de atención en ventanilla es de 9 a 16 horas", "Neutro"),
    ("La app se cierra sola cuando intento transferir a otros bancos", "Negativo"),
    ("Gran servicio de asesoría patrimonial por parte de la ejecutiva", "Positivo"),
    ("Requiero actualización de mis datos fiscales para facturación", "Neutro"),
]

DRIFT_CORPUS = [
    ("Mi cripto-wallet mexban no sincroniza con polygon y mis tokens se congelaron", "Negativo"),
    ("El gas fee en la transacción de bitcoin fue altísimo y dio error en hash", "Negativo"),
    ("Quiero hacer staking de mis ethereum desde la billetera descentralizada", "Neutro"),
    ("La plataforma de trading cripto de mexban es lentísima, perdí en el arbitraje", "Negativo"),
    ("No me deja transferir USDT a mi cold wallet mediante red lightning", "Negativo"),
    ("Excelente el nuevo servicio de custodia cripto regulada para bitso y binance", "Positivo"),
    ("El smart contract de inversión arrojó un fallo de timeout en la web3 app", "Negativo"),
    ("Compré satoshis en el cajero cripto y se acreditó al segundo, muy bien", "Positivo"),
]

class MexBanObservabilityService:
    """Orquestador de observabilidad en producción."""

    def __init__(self):
        self.telemetry = ObservabilityTelemetry()
        self.drift_detector = DriftDetector()
        self.alert_engine = SmartAlertEngine()
        self.runbook_engine = RunbookAutomationEngine()

        # Inicializar drift detector con baseline
        base_texts = [item[0] for item in BASELINE_CORPUS] * 20
        base_labels = [item[1] for item in BASELINE_CORPUS] * 20
        self.drift_detector.fit_reference(base_texts, base_labels)

    def simulate_traffic_window(
        self,
        num_requests: int = 50,
        scenario: str = "normal",  # 'normal', 'latency_spike', 'data_drift', 'post_recovery'
        error_rate: float = 0.002
    ) -> Dict[str, Any]:
        """Simula una ventana temporal de tráfico bancario y computa telemetría."""
        corpus = DRIFT_CORPUS if scenario == "data_drift" else BASELINE_CORPUS

        texts_window = []
        preds_window = []
        trues_window = []

        for _ in range(num_requests):
            sample_text, true_label = random.choice(corpus)
            texts_window.append(sample_text)
            trues_window.append(true_label)

            # Simulación de latencia según escenario
            if scenario == "latency_spike":
                lat = np.random.normal(loc=125.0, scale=25.0)  # Pico crítico > 100ms
                lat = max(65.0, lat)
            elif scenario == "post_recovery":
                lat = np.random.normal(loc=16.5, scale=3.5)   # Restaurado tras autoescalado
                lat = max(8.0, lat)
            else:
                lat = np.random.normal(loc=18.0, scale=4.0)   # Latencia normal estándar de DistilBERT
                lat = max(10.0, lat)

            # Simulación de predicción y degradación de F1 si hay data drift
            if scenario == "data_drift":
                # Modelo no conoce el léxico cripto -> comete más errores y tiene menor confianza
                if random.random() < 0.35:
                    pred_label = random.choice(["Positivo", "Negativo", "Neutro"])
                    conf = np.random.uniform(0.40, 0.65)
                else:
                    pred_label = true_label
                    conf = np.random.uniform(0.65, 0.82)
            elif scenario == "post_recovery":
                # Modelo v2 reentrenado -> alta precisión
                pred_label = true_label if random.random() > 0.06 else "Neutro"
                conf = np.random.uniform(0.88, 0.98)
            else:
                # Modelo normal
                pred_label = true_label if random.random() > 0.12 else "Neutro"
                conf = np.random.uniform(0.82, 0.95)

            preds_window.append(pred_label)

            # Probabilidades sintéticas
            probs = {"Positivo": 0.1, "Negativo": 0.1, "Neutro": 0.1}
            probs[pred_label] = conf
            rem = (1.0 - conf) / 2.0
            for k in probs:
                if k != pred_label:
                    probs[k] = rem

            status_code = 500 if random.random() < error_rate else 200

            self.telemetry.record_inference(
                text=sample_text,
                prediction=pred_label,
                confidence=conf,
                probabilities=probs,
                latency_ms=lat,
                http_status=status_code
            )

        # Calcular métricas de servicio
        svc_metrics = self.telemetry.get_service_metrics(window_size=num_requests)
        ml_metrics = self.telemetry.compute_ml_metrics(trues_window, preds_window)
        drift_metrics = self.drift_detector.evaluate_text_drift(texts_window, preds_window)

        combined_metrics = {
            "latency_p95": svc_metrics["latency_p95"],
            "latency_p50": svc_metrics["latency_p50"],
            "latency_p99": svc_metrics["latency_p99"],
            "availability_pct": (1.0 - svc_metrics["error_rate"]) * 100.0,
            "f1_score": ml_metrics["f1_score"],
            "accuracy": ml_metrics["accuracy"],
            "max_psi": drift_metrics["max_psi"],
            "psi_length": drift_metrics["psi_length"],
            "psi_classes": drift_metrics["psi_classes"],
            "oov_rate": drift_metrics["oov_rate"]
        }

        alerts = self.alert_engine.evaluate_metrics(combined_metrics)
        budget_status = self.alert_engine.get_error_budget_status()

        return {
            "scenario": scenario,
            "metrics": combined_metrics,
            "drift_evaluation": drift_metrics,
            "active_alerts": alerts,
            "error_budget": budget_status
        }
