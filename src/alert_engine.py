"""
alert_engine.py
Motor de Alertas Inteligentes basadas en SLOs, Error Budgets y Reducción de Fatiga de Alertas para MexBan.
"""

import time
from dataclasses import dataclass, asdict
from typing import Dict, List, Any, Optional

@dataclass
class AlertDefinition:
    alert_id: str
    name: str
    metric_target: str
    sli_description: str
    slo_target: float
    slo_operator: str  # '<', '>', '<=', '>='
    p1_threshold: float
    p2_threshold: float
    p3_threshold: float
    persistence_required: int  # Debouncing: ciclos consecutivos
    hysteresis_recovery: float  # Deadband para limpiar alerta

@dataclass
class ActiveAlert:
    alert_id: str
    name: str
    severity: str  # 'P1', 'P2', 'P3'
    current_value: float
    slo_target: float
    timestamp: str
    impact: str
    burn_rate: float
    action_required: str

class SmartAlertEngine:
    """Evalúa métricas operativas y de ML contra SLOs, calcula el consumo de Error Budget y despacha alertas inteligentes."""

    def __init__(self, monthly_budget_minutes: float = 43.2):
        self.monthly_budget_minutes = monthly_budget_minutes
        self.error_budget_consumed_pct = 0.0  # 0% a 100%
        self.consecutive_breaches: Dict[str, int] = {}
        self.active_alerts: Dict[str, ActiveAlert] = {}
        self.alert_history: List[Dict[str, Any]] = []

        # Catálogo de Reglas de SLO formalizadas para MexBan
        self.catalog: Dict[str, AlertDefinition] = {
            "latency_p95": AlertDefinition(
                alert_id="ALT-001",
                name="SLO Latencia p95 Inferencia",
                metric_target="latency_p95",
                sli_description="Latencia percentil 95 en ventana de 5 min (ms)",
                slo_target=50.0,
                slo_operator="<",
                p1_threshold=100.0,   # Crítico si supera 100ms
                p2_threshold=70.0,    # Alto si supera 70ms
                p3_threshold=50.0,    # Alerta preventiva si supera 50ms
                persistence_required=2,
                hysteresis_recovery=40.0
            ),
            "availability": AlertDefinition(
                alert_id="ALT-002",
                name="SLO Disponibilidad del Servicio (Uptime)",
                metric_target="availability_pct",
                sli_description="Peticiones exitosas / Peticiones totales (%)",
                slo_target=99.9,
                slo_operator=">=",
                p1_threshold=98.0,
                p2_threshold=99.5,
                p3_threshold=99.85,
                persistence_required=1,
                hysteresis_recovery=99.95
            ),
            "ml_f1_score": AlertDefinition(
                alert_id="ALT-003",
                name="SLO Calidad del Modelo (F1-Score)",
                metric_target="f1_score",
                sli_description="F1-Score ponderado en validación continua",
                slo_target=0.82,
                slo_operator=">=",
                p1_threshold=0.70,   # Caída crítica por debajo de 0.70
                p2_threshold=0.80,   # Caída moderada por debajo de 0.80
                p3_threshold=0.82,   # Advertencia si < 0.82
                persistence_required=2,
                hysteresis_recovery=0.85
            ),
            "data_drift_psi": AlertDefinition(
                alert_id="ALT-004",
                name="SLO Estabilidad de Datos (PSI Data Drift)",
                metric_target="max_psi",
                sli_description="Índice de Estabilidad Poblacional (PSI)",
                slo_target=0.10,
                slo_operator="<",
                p1_threshold=0.25,   # Drift severo
                p2_threshold=0.18,   # Drift alto
                p3_threshold=0.10,   # Drift incipiente
                persistence_required=2,
                hysteresis_recovery=0.08
            )
        }

    def evaluate_metrics(self, current_metrics: Dict[str, float]) -> List[ActiveAlert]:
        """Evalúa las métricas actuales con filtrado de histeresis y persistencia temporal."""
        dispatched: List[ActiveAlert] = []

        for metric_key, rule in self.catalog.items():
            if metric_key not in current_metrics:
                continue

            val = current_metrics[metric_key]
            is_breach = False
            severity = None

            # Determinar severidad según dirección del operador
            if rule.slo_operator == "<":
                if val >= rule.p1_threshold:
                    severity = "P1"
                    is_breach = True
                elif val >= rule.p2_threshold:
                    severity = "P2"
                    is_breach = True
                elif val > rule.p3_threshold:
                    severity = "P3"
                    is_breach = True
            elif rule.slo_operator in (">=", ">"):
                if val <= rule.p1_threshold:
                    severity = "P1"
                    is_breach = True
                elif val <= rule.p2_threshold:
                    severity = "P2"
                    is_breach = True
                elif val < rule.p3_threshold:
                    severity = "P3"
                    is_breach = True

            # Manejo de persistencia temporal (Debouncing)
            current_breaches = self.consecutive_breaches.get(rule.alert_id, 0)
            if is_breach:
                current_breaches += 1
                self.consecutive_breaches[rule.alert_id] = current_breaches
            else:
                # Comprobar si se cumple histeresis para resetear
                can_clear = False
                if rule.slo_operator == "<" and val <= rule.hysteresis_recovery:
                    can_clear = True
                elif rule.slo_operator in (">=", ">") and val >= rule.hysteresis_recovery:
                    can_clear = True

                if can_clear:
                    self.consecutive_breaches[rule.alert_id] = 0
                    if rule.alert_id in self.active_alerts:
                        del self.active_alerts[rule.alert_id]

            # Verificar si se supera el umbral de persistencia
            if is_breach and current_breaches >= rule.persistence_required and severity:
                # Calcular burn rate estimado
                burn_rate = 14.4 if severity == "P1" else (4.5 if severity == "P2" else 1.0)
                
                # Consumo de error budget simulado
                if severity == "P1":
                    self.error_budget_consumed_pct = min(100.0, self.error_budget_consumed_pct + 12.5)
                elif severity == "P2":
                    self.error_budget_consumed_pct = min(100.0, self.error_budget_consumed_pct + 4.0)

                action_map = {
                    "P1": "Ejecución inmediata de Runbook automatizado y llamado a guardia SRE/MLOps (PagerDuty).",
                    "P2": "Notificación a canal de guardia Slack #ops-mlops y creación de ticket Jira prioritario.",
                    "P3": "Notificación informativa en dashboard operativo para revisión en sprint."
                }

                impact_map = {
                    "latency_p95": "Degradación en la experiencia de cliente y riesgo de timeouts en Banca Móvil.",
                    "availability": "Interrupción de servicio e indisponibilidad para clasificar reseñas bancarias.",
                    "ml_f1_score": "Riesgo de clasificaciones erróneas de quejas graves como positivas.",
                    "data_drift_psi": "Divergencia entre los datos de producción y los datos de entrenamiento."
                }

                alert = ActiveAlert(
                    alert_id=rule.alert_id,
                    name=rule.name,
                    severity=severity,
                    current_value=round(val, 3),
                    slo_target=rule.slo_target,
                    timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
                    impact=impact_map.get(metric_key, "Impacto operativo general."),
                    burn_rate=burn_rate,
                    action_required=action_map.get(severity, "Investigación requerida.")
                )

                self.active_alerts[rule.alert_id] = alert
                self.alert_history.append(asdict(alert))
                dispatched.append(alert)

        return dispatched

    def get_error_budget_status(self) -> Dict[str, float]:
        """Calcula el estado remanente del Error Budget mensual."""
        remaining_pct = max(0.0, 100.0 - self.error_budget_consumed_pct)
        remaining_minutes = (remaining_pct / 100.0) * self.monthly_budget_minutes
        return {
            "monthly_budget_minutes": self.monthly_budget_minutes,
            "consumed_pct": round(self.error_budget_consumed_pct, 2),
            "remaining_pct": round(remaining_pct, 2),
            "remaining_minutes": round(remaining_minutes, 2)
        }
