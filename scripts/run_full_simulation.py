"""
run_full_simulation.py
Simulación integral de observabilidad, incidentes y automatización para MexBan con MLflow.
"""

import os
import sys
import json
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from typing import Dict, List, Any
import numpy as np
import pandas as pd
import mlflow
from mlflow.tracking import MlflowClient

from src.observability_service import MexBanObservabilityService

def run_simulation():
    print("================================================================================")
    print("  INICIANDO SIMULACIÓN DE OBSERVABILIDAD Y GOBERNANZA OPERATIVA - MEXBAN")
    print("================================================================================")

    # Configuración de MLflow local
    os.environ["MLFLOW_DISABLE_AGENT_HINT"] = "1"
    os.environ["MPLCONFIGDIR"] = os.path.abspath(".mplconfig")
    
    mlflow.set_tracking_uri("sqlite:///mlflow_tracking.db")
    mlflow.set_experiment("MexBan_Production_Observability")
    client = MlflowClient()

    service = MexBanObservabilityService()

    # Timeline de simulación: 26 periodos operativos (ventanas de 5 min simuladas)
    phases = [
        # (Fase, Escenario, Nombre descriptivo, Num Ventanas)
        ("FASE 1", "normal", "Operación Normal Estable (DistilBERT v1.0)", 5),
        ("FASE 2", "latency_spike", "INCIDENTE 1: Pico de Concurrencia y Saturación Latencia", 4),
        ("FASE 3", "post_recovery", "Mitigación RB-01: Auto-escalado HPA y Caché", 3),
        ("FASE 4", "normal", "Operación Normal Post-Incidente 1", 3),
        ("FASE 5", "data_drift", "INCIDENTE 2: Deriva de Datos Crítica (Cripto-Billetera)", 4),
        ("FASE 6", "post_recovery", "Mitigación RB-02: Fallback + Reentrenamiento MLflow v2.0", 3),
        ("FASE 7", "post_recovery", "Operación Normal Estable (DistilBERT v2.0)", 4),
    ]

    history_records = []
    all_dispatched_alerts = []
    incidents_executed = []

    epoch_idx = 1

    with mlflow.start_run(run_name="Produccion_Monitoreo_Continuo") as active_run:
        run_id = active_run.info.run_id
        print(f"\n[MLflow] Iniciada corrida principal: {run_id}")

        mlflow.log_params({
            "model_primary": "DistilBERT-MexBan-Sentiment",
            "model_version_initial": "v1.0.0",
            "slo_latency_p95_limit_ms": 50.0,
            "slo_availability_target_pct": 99.9,
            "slo_f1_score_min": 0.82,
            "slo_psi_drift_max": 0.20,
            "error_budget_monthly_minutes": 43.2
        })

        for phase_id, scenario, desc, num_windows in phases:
            print(f"\n>>> {phase_id}: {desc} ({num_windows} ciclos)")

            for w in range(num_windows):
                # Simular ventana
                win_res = service.simulate_traffic_window(
                    num_requests=40,
                    scenario=scenario,
                    error_rate=0.015 if scenario == "latency_spike" else 0.001
                )

                metrics = win_res["metrics"]
                drift = win_res["drift_evaluation"]
                alerts = win_res["active_alerts"]
                budget = win_res["error_budget"]

                # Loguear métricas en MLflow
                mlflow.log_metric("latency_p50_ms", metrics["latency_p50"], step=epoch_idx)
                mlflow.log_metric("latency_p95_ms", metrics["latency_p95"], step=epoch_idx)
                mlflow.log_metric("latency_p99_ms", metrics["latency_p99"], step=epoch_idx)
                mlflow.log_metric("availability_pct", metrics["availability_pct"], step=epoch_idx)
                mlflow.log_metric("f1_score", metrics["f1_score"], step=epoch_idx)
                mlflow.log_metric("accuracy", metrics["accuracy"], step=epoch_idx)
                mlflow.log_metric("max_psi_drift", metrics["max_psi"], step=epoch_idx)
                mlflow.log_metric("oov_rate", metrics["oov_rate"], step=epoch_idx)
                mlflow.log_metric("error_budget_remaining_pct", budget["remaining_pct"], step=epoch_idx)
                mlflow.log_metric("active_alerts_count", len(alerts), step=epoch_idx)

                # Registrar alertas activas
                for a in alerts:
                    all_dispatched_alerts.append({
                        "epoch": epoch_idx,
                        "phase": phase_id,
                        "alert_id": a.alert_id,
                        "name": a.name,
                        "severity": a.severity,
                        "value": a.current_value,
                        "slo_target": a.slo_target,
                        "burn_rate": a.burn_rate,
                        "action": a.action_required
                    })
                    print(f"    [! ALERTA {a.severity}]: {a.name} | Valor: {a.current_value} (SLO: {a.slo_target})")

                # Disparador de Runbooks al detectar incidentes
                if phase_id == "FASE 2" and w == 1:
                    print("\n    [AUTOMATION] Disparo automático de Runbook RB-01 ante saturación de latencia...")
                    inc1_rep = service.runbook_engine.execute_runbook_rb01_latency_surge(
                        initial_p95=metrics["latency_p95"], current_pods=2
                    )
                    incidents_executed.append(inc1_rep)
                    print(f"    [OK] Runbook RB-01 completado con éxito. MTTR: {inc1_rep.duration_min} min.")

                if phase_id == "FASE 5" and w == 1:
                    print("\n    [AUTOMATION] Disparo automático de Runbook RB-02 ante Data Drift crítico y caída de F1...")
                    inc2_rep = service.runbook_engine.execute_runbook_rb02_data_drift_retraining(
                        initial_psi=metrics["max_psi"], initial_f1=metrics["f1_score"]
                    )
                    incidents_executed.append(inc2_rep)
                    print(f"    [OK] Runbook RB-02 completado con éxito. Modelo v2.0 registrado y desplegado. MTTR: {inc2_rep.duration_min} min.")

                record = {
                    "epoch": epoch_idx,
                    "phase": phase_id,
                    "scenario": scenario,
                    "latency_p50": metrics["latency_p50"],
                    "latency_p95": metrics["latency_p95"],
                    "latency_p99": metrics["latency_p99"],
                    "availability_pct": metrics["availability_pct"],
                    "f1_score": metrics["f1_score"],
                    "accuracy": metrics["accuracy"],
                    "max_psi": metrics["max_psi"],
                    "oov_rate": metrics["oov_rate"],
                    "budget_remaining_pct": budget["remaining_pct"],
                    "alerts_count": len(alerts)
                }
                history_records.append(record)
                epoch_idx += 1

        # Guardar dataset de la simulación
        df_sim = pd.DataFrame(history_records)
        df_sim.to_csv("dashboards/simulation_timeline_metrics.csv", index=False)
        mlflow.log_artifact("dashboards/simulation_timeline_metrics.csv")

        # Guardar muestra de logs estructurados JSON
        sample_log_json = service.telemetry.export_sample_json_log()
        with open("dashboards/sample_structured_log.json", "w", encoding="utf-8") as f:
            f.write(sample_log_json)
        mlflow.log_artifact("dashboards/sample_structured_log.json")

        # Guardar registro de incidentes y alertas
        alerts_df = pd.DataFrame(all_dispatched_alerts)
        alerts_df.to_csv("dashboards/dispatched_alerts_log.csv", index=False)
        mlflow.log_artifact("dashboards/dispatched_alerts_log.csv")

        incidents_data = [
            {
                "incident_id": inc.incident_id,
                "title": inc.title,
                "severity": inc.severity,
                "runbook_id": inc.runbook_id,
                "duration_min": inc.duration_min,
                "initial_metrics": inc.initial_metrics,
                "restored_metrics": inc.restored_metrics,
                "steps": [s.action_name for s in inc.steps_executed]
            }
            for inc in incidents_executed
        ]
        with open("dashboards/incidents_execution_report.json", "w", encoding="utf-8") as f:
            json.dump(incidents_data, f, indent=2)
        mlflow.log_artifact("dashboards/incidents_execution_report.json")

        # Registrar modelos en Model Registry
        with mlflow.start_run(run_name="DistilBERT_MexBan_v1_Baseline", nested=True):
            mlflow.log_params({"architecture": "DistilBERT-base-uncased", "classes": 3, "weights": "finetuned-imdb-mexban"})
            mlflow.log_metrics({"f1_score": 0.8759, "accuracy": 0.881, "latency_p95_ms": 23.3})
            # Etiquetar
            mlflow.set_tag("version", "v1.0.0")
            mlflow.set_tag("stage", "Archived_Post_Incident")

        with mlflow.start_run(run_name="DistilBERT_MexBan_v2_Retrained", nested=True):
            mlflow.log_params({"architecture": "DistilBERT-base-uncased", "classes": 3, "retrained_with_drift": True, "epochs": 3})
            mlflow.log_metrics({"f1_score": 0.912, "accuracy": 0.915, "latency_p95_ms": 16.4})
            mlflow.set_tag("version", "v2.0.0")
            mlflow.set_tag("stage", "Production")

    print("\n================================================================================")
    print("  SIMULACIÓN COMPLETADA EXITOSAMENTE Y REGISTRADA EN MLFLOW")
    print(f"  Total de ventanas simuladas: {len(history_records)}")
    print(f"  Alertas inteligentes despachadas: {len(all_dispatched_alerts)}")
    print(f"  Incidentes críticos resueltos mediante runbooks: {len(incidents_executed)}")
    print("================================================================================")
    return df_sim, alerts_df, incidents_executed

if __name__ == "__main__":
    run_simulation()
