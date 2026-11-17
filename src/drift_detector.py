"""
drift_detector.py
Módulo de Detección de Data Drift y Concept Drift para MexBan.
Implementa Population Stability Index (PSI), KS-Test, Wasserstein Distance y análisis OOV.
"""

from typing import Dict, List, Tuple, Any
import numpy as np
import pandas as pd
from scipy import stats

class DriftDetector:
    """Motor estadístico para detección de deriva en distribuciones de datos (Data Drift) y conceptos (Concept Drift)."""

    def __init__(self, psi_warning_threshold: float = 0.10, psi_critical_threshold: float = 0.20):
        self.psi_warning_threshold = psi_warning_threshold
        self.psi_critical_threshold = psi_critical_threshold
        self.reference_vocab: set = set()
        self.reference_lengths: np.ndarray = np.array([])
        self.reference_class_dist: Dict[str, float] = {}

    def fit_reference(self, texts: List[str], sentiments: List[str]):
        """Establece la distribución de referencia (Baseline) a partir del dataset de entrenamiento/producción inicial."""
        all_words = " ".join(texts).lower().split()
        self.reference_vocab = set(all_words)
        self.reference_lengths = np.array([len(t.split()) for t in texts])

        df_classes = pd.Series(sentiments).value_counts(normalize=True).to_dict()
        self.reference_class_dist = df_classes

    def calculate_psi_numerical(self, baseline: np.ndarray, target: np.ndarray, num_buckets: int = 10) -> float:
        """
        Calcula el Population Stability Index (PSI) para variables numéricas continuas.
        PSI = sum((Actual% - Baseline%) * ln(Actual% / Baseline%))
        """
        if len(baseline) == 0 or len(target) == 0:
            return 0.0

        # Crear percentiles de referencia
        percentiles = np.linspace(0, 100, num_buckets + 1)
        bins = np.percentile(baseline, percentiles)
        bins[0] = -np.inf
        bins[-1] = np.inf
        bins = np.unique(bins)

        base_counts, _ = np.histogram(baseline, bins=bins)
        target_counts, _ = np.histogram(target, bins=bins)

        base_pct = base_counts / len(baseline)
        target_pct = target_counts / len(target)

        # Suavizado de Laplace para evitar división por cero o log(0)
        base_pct = np.where(base_pct == 0, 0.0001, base_pct)
        target_pct = np.where(target_pct == 0, 0.0001, target_pct)

        psi_val = np.sum((target_pct - base_pct) * np.log(target_pct / base_pct))
        return float(max(0.0, psi_val))

    def calculate_psi_categorical(self, baseline_dist: Dict[str, float], target_dist: Dict[str, float]) -> float:
        """Calcula el Population Stability Index (PSI) para distribuciones categóricas de clases."""
        all_categories = set(baseline_dist.keys()).union(set(target_dist.keys()))
        psi_total = 0.0

        for cat in all_categories:
            b_pct = baseline_dist.get(cat, 0.0001)
            t_pct = target_dist.get(cat, 0.0001)
            b_pct = max(0.0001, b_pct)
            t_pct = max(0.0001, t_pct)
            psi_total += (t_pct - b_pct) * np.log(t_pct / b_pct)

        return float(max(0.0, psi_total))

    def calculate_ks_test(self, baseline: np.ndarray, target: np.ndarray) -> Tuple[float, float]:
        """Ejecuta la prueba de dos muestras Kolmogorov-Smirnov. Retorna estadístico y p-value."""
        res = stats.ks_2samp(baseline, target)
        return float(res.statistic), float(res.pvalue)

    def calculate_wasserstein(self, baseline: np.ndarray, target: np.ndarray) -> float:
        """Calcula la distancia de Wasserstein (Earth Mover's Distance) entre dos distribuciones continuas."""
        return float(stats.wasserstein_distance(baseline, target))

    def evaluate_text_drift(self, current_texts: List[str], current_predictions: List[str]) -> Dict[str, Any]:
        """Evalúa de forma integral la presencia de Data Drift en la ventana de producción actual."""
        cur_lengths = np.array([len(t.split()) for t in current_texts])
        cur_words = " ".join(current_texts).lower().split()

        # OOV (Out Of Vocabulary) Rate
        if cur_words:
            oov_count = sum(1 for w in cur_words if w not in self.reference_vocab)
            oov_rate = oov_count / len(cur_words)
        else:
            oov_rate = 0.0

        # PSI de longitudes
        psi_lengths = self.calculate_psi_numerical(self.reference_lengths, cur_lengths)

        # KS-Test en longitud
        ks_stat, ks_pval = self.calculate_ks_test(self.reference_lengths, cur_lengths)

        # Distancia de Wasserstein en longitud
        wasserstein_dist = self.calculate_wasserstein(self.reference_lengths, cur_lengths)

        # PSI de clases predichas
        cur_class_dist = pd.Series(current_predictions).value_counts(normalize=True).to_dict()
        psi_classes = self.calculate_psi_categorical(self.reference_class_dist, cur_class_dist)

        # Estado global de drift
        max_psi = max(psi_lengths, psi_classes)
        if max_psi >= self.psi_critical_threshold or ks_pval < 0.01:
            drift_status = "CRITICAL_DRIFT"
        elif max_psi >= self.psi_warning_threshold or ks_pval < 0.05:
            drift_status = "MODERATE_DRIFT"
        else:
            drift_status = "STABLE"

        return {
            "psi_length": round(psi_lengths, 4),
            "psi_classes": round(psi_classes, 4),
            "max_psi": round(max_psi, 4),
            "ks_statistic": round(ks_stat, 4),
            "ks_pvalue": round(ks_pval, 6),
            "wasserstein_distance": round(wasserstein_dist, 4),
            "oov_rate": round(oov_rate, 4),
            "status": drift_status,
            "is_drift_detected": drift_status != "STABLE"
        }
