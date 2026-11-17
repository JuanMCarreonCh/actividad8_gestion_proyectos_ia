"""
metrics_logger.py
Módulo de Observabilidad y Telemetría para MexBan: Métricas, Logs Estructurados y Trazas Distribuidas.
"""

import json
import time
import uuid
import logging
from dataclasses import dataclass, asdict
from typing import Dict, List, Any, Optional
import numpy as np
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("MexBanObservability")

@dataclass
class SpanRecord:
    span_id: str
    parent_span_id: Optional[str]
    name: str
    duration_ms: float
    status: str

@dataclass
class StructuredInferenceLog:
    timestamp: str
    request_id: str
    trace_id: str
    model_name: str
    model_version: str
    channel: str
    input_char_len: int
    token_count: int
    prediction: str
    confidence: float
    probabilities: Dict[str, float]
    latency_ms: float
    http_status: int
    pii_masked: bool
    spans: List[Dict[str, Any]]

class ObservabilityTelemetry:
    """Gestiona la captura de trazas, generación de logs JSON estructurados y cálculo de métricas."""

    def __init__(self, model_name: str = "DistilBERT-MexBan-Sentiment", model_version: str = "v1.0.0"):
        self.model_name = model_name
        self.model_version = model_version
        self.logs_history: List[StructuredInferenceLog] = []

    def record_inference(
        self,
        text: str,
        prediction: str,
        confidence: float,
        probabilities: Dict[str, float],
        latency_ms: float,
        channel: str = "mobile_banking",
        http_status: int = 200,
        pii_masked: bool = True,
        spans_breakdown: Optional[Dict[str, float]] = None
    ) -> StructuredInferenceLog:
        """Crea un log estructurado y registra la traza distribuida de la inferencia."""
        trace_id = f"trace-{uuid.uuid4().hex[:12]}"
        root_span_id = f"span-root-{uuid.uuid4().hex[:8]}"

        # Desglose de trazas por componente si no se proporcionan
        if not spans_breakdown:
            spans_breakdown = {
                "api_gateway": max(0.5, latency_ms * 0.05),
                "pii_sanitizer": max(0.4, latency_ms * 0.04),
                "tokenization": max(1.2, latency_ms * 0.12),
                "model_inference": max(10.0, latency_ms * 0.74),
                "postprocessing_rules": max(0.5, latency_ms * 0.05),
            }

        spans_list = []
        for stage, dur in spans_breakdown.items():
            spans_list.append(
                asdict(SpanRecord(
                    span_id=f"span-{uuid.uuid4().hex[:8]}",
                    parent_span_id=root_span_id,
                    name=stage,
                    duration_ms=round(dur, 2),
                    status="OK" if http_status == 200 else "ERROR"
                ))
            )

        token_count = max(1, len(text.split()))

        log_entry = StructuredInferenceLog(
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime()),
            request_id=f"req-{uuid.uuid4().hex[:10]}",
            trace_id=trace_id,
            model_name=self.model_name,
            model_version=self.model_version,
            channel=channel,
            input_char_len=len(text),
            token_count=token_count,
            prediction=prediction,
            confidence=round(confidence, 4),
            probabilities={k: round(v, 4) for k, v in probabilities.items()},
            latency_ms=round(latency_ms, 2),
            http_status=http_status,
            pii_masked=pii_masked,
            spans=spans_list
        )

        self.logs_history.append(log_entry)
        return log_entry

    def get_service_metrics(self, window_size: int = 100) -> Dict[str, float]:
        """Calcula métricas de servicio (latencia percentiles, error rate, throughput)."""
        recent = self.logs_history[-window_size:] if self.logs_history else []
        if not recent:
            return {
                "latency_p50": 0.0,
                "latency_p95": 0.0,
                "latency_p99": 0.0,
                "latency_avg": 0.0,
                "error_rate": 0.0,
                "request_count": 0
            }

        latencies = [log.latency_ms for log in recent]
        errors = [1 for log in recent if log.http_status >= 500]

        return {
            "latency_p50": float(np.percentile(latencies, 50)),
            "latency_p95": float(np.percentile(latencies, 95)),
            "latency_p99": float(np.percentile(latencies, 99)),
            "latency_avg": float(np.mean(latencies)),
            "error_rate": float(len(errors) / len(recent)),
            "request_count": len(recent)
        }

    def compute_ml_metrics(self, y_true: List[str], y_pred: List[str]) -> Dict[str, float]:
        """Calcula métricas de calidad de Machine Learning (Accuracy, Precision, Recall, F1)."""
        acc = accuracy_score(y_true, y_pred)
        prec, rec, f1, _ = precision_recall_fscore_support(
            y_true, y_pred, average="weighted", zero_division=0
        )
        return {
            "accuracy": float(acc),
            "precision": float(prec),
            "recall": float(rec),
            "f1_score": float(f1)
        }

    def export_sample_json_log(self) -> str:
        """Devuelve un ejemplo formateado de log estructurado en JSON."""
        if not self.logs_history:
            return "{}"
        return json.dumps(asdict(self.logs_history[-1]), indent=2)
