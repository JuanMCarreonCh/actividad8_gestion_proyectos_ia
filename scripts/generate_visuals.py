"""
generate_visuals.py
Generación de gráficos y dashboards de observabilidad de alta resolución para MexBan.
"""

import os
import sys
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Estilos estéticos profesionales
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams["font.sans-serif"] = "DejaVu Sans"
plt.rcParams["font.size"] = 10
plt.rcParams["axes.titlesize"] = 12
plt.rcParams["axes.labelsize"] = 10

NAVY_BLUE = "#0F3B7A"
TEAL = "#00A896"
CORAL_RED = "#E63946"
AMBER = "#F4A261"
CHARCOAL = "#2B2D42"
LIGHT_BG = "#F8F9FA"

def create_operational_dashboard(df: pd.DataFrame):
    """Genera el Dashboard Operativo en Tiempo Real de 4 paneles."""
    fig, axes = plt.subplots(2, 2, figsize=(15, 10), facecolor="white")
    fig.suptitle("MexBan - Dashboard Operativo en Tiempo Real (Golden Signals & ML Health)", 
                 fontsize=16, fontweight="bold", color=NAVY_BLUE, y=0.98)

    epochs = df["epoch"]

    # 1. Latencia
    ax1 = axes[0, 0]
    ax1.plot(epochs, df["latency_p99"], label="Latencia p99", color="#8338EC", linestyle=":", linewidth=1.8)
    ax1.plot(epochs, df["latency_p95"], label="Latencia p95", color=CORAL_RED, linewidth=2.2)
    ax1.plot(epochs, df["latency_p50"], label="Latencia p50 (Mediana)", color=TEAL, linewidth=2.0)
    ax1.axhline(y=50.0, color="#E76F51", linestyle="--", linewidth=1.5, label="SLO Límite p95 (< 50ms)")
    ax1.axvspan(5.5, 9.5, color=CORAL_RED, alpha=0.15, label="Incidente 1: Saturación")
    ax1.axvspan(9.5, 12.5, color=TEAL, alpha=0.12, label="Mitigación RB-01 (HPA)")
    ax1.set_title("1. Latencia de Inferencia por Ventana (ms)", fontweight="bold", color=CHARCOAL)
    ax1.set_xlabel("Ciclo de Monitoreo (Ventanas de 5 min)")
    ax1.set_ylabel("Latencia (ms)")
    ax1.set_ylim(0, 190)
    ax1.legend(loc="upper right", frameon=True, fontsize=8.5)
    ax1.grid(True, linestyle="--", alpha=0.6)

    # 2. Disponibilidad y Presupuesto de Error
    ax2 = axes[0, 1]
    ax2.plot(epochs, df["budget_remaining_pct"], label="Error Budget Remanente (%)", color=NAVY_BLUE, linewidth=2.5)
    ax2.axhline(y=0.0, color="gray", linestyle="-", linewidth=1)
    ax2.axhline(y=20.0, color=AMBER, linestyle="--", linewidth=1.5, label="Umbral Crítico Budget (< 20%)")
    ax2.fill_between(epochs, df["budget_remaining_pct"], color=NAVY_BLUE, alpha=0.1)
    ax2.set_title("2. Presupuesto de Error (Error Budget) Mensual (%)", fontweight="bold", color=CHARCOAL)
    ax2.set_xlabel("Ciclo de Monitoreo")
    ax2.set_ylabel("Presupuesto Restante (%)")
    ax2.set_ylim(-5, 105)
    ax2.legend(loc="lower left", frameon=True, fontsize=8.5)
    ax2.grid(True, linestyle="--", alpha=0.6)

    # 3. Métricas de Calidad ML (F1 & Accuracy)
    ax3 = axes[1, 0]
    ax3.plot(epochs, df["f1_score"], label="F1-Score Ponderado", color="#2A9D8F", linewidth=2.5, marker="o", markersize=4)
    ax3.plot(epochs, df["accuracy"], label="Exactitud (Accuracy)", color="#457B9D", linewidth=1.8, linestyle="-.")
    ax3.axhline(y=0.82, color=CORAL_RED, linestyle="--", linewidth=1.5, label="SLO Calidad Mínima F1 (>= 0.82)")
    ax3.axvspan(15.5, 19.5, color=AMBER, alpha=0.18, label="Incidente 2: Data Drift Cripto")
    ax3.axvspan(19.5, 22.5, color=TEAL, alpha=0.12, label="Mitigación RB-02 (MLflow v2.0)")
    ax3.set_title("3. Desempeño Continuo de Clasificación ML", fontweight="bold", color=CHARCOAL)
    ax3.set_xlabel("Ciclo de Monitoreo")
    ax3.set_ylabel("Puntuación (0 - 1.0)")
    ax3.set_ylim(0.55, 1.0)
    ax3.legend(loc="lower left", frameon=True, fontsize=8.5)
    ax3.grid(True, linestyle="--", alpha=0.6)

    # 4. Deriva de Datos (Data Drift - PSI)
    ax4 = axes[1, 1]
    ax4.plot(epochs, df["max_psi"], label="Índice de Estabilidad (PSI)", color="#E76F51", linewidth=2.4, marker="s", markersize=4)
    ax4.plot(epochs, df["oov_rate"], label="Tasa Out-of-Vocabulary (OOV)", color="#9D4EDD", linewidth=1.8, linestyle=":")
    ax4.axhline(y=0.10, color=AMBER, linestyle="--", linewidth=1.2, label="Umbral Advertencia PSI (0.10)")
    ax4.axhline(y=0.20, color=CORAL_RED, linestyle="-", linewidth=1.8, label="Umbral Crítico Drift (0.20)")
    ax4.axvspan(15.5, 19.5, color=CORAL_RED, alpha=0.15)
    ax4.set_title("4. Detección de Data Drift (Population Stability Index)", fontweight="bold", color=CHARCOAL)
    ax4.set_xlabel("Ciclo de Monitoreo")
    ax4.set_ylabel("Métrica de Deriva")
    ax4.set_ylim(-0.02, max(0.40, df["max_psi"].max() * 1.15))
    ax4.legend(loc="upper right", frameon=True, fontsize=8.5)
    ax4.grid(True, linestyle="--", alpha=0.6)

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    out_path = "dashboards/img1_realtime_operational_dashboard.png"
    plt.savefig(out_path, dpi=200)
    plt.close()
    print(f"[Graficado] Guardado: {out_path}")

def create_incident_detail_charts(df: pd.DataFrame):
    """Genera gráficos detallados de análisis y recuperación para ambos incidentes."""
    # Incidente 1: Latencia
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5), facecolor="white")
    fig.suptitle("MexBan - Simulación Incidente 1: Degradación de Latencia y Autoescalado", 
                 fontsize=14, fontweight="bold", color=NAVY_BLUE)

    inc1_df = df[(df["epoch"] >= 3) & (df["epoch"] <= 14)]
    
    # Latencia p95 antes, durante y después
    ax1.plot(inc1_df["epoch"], inc1_df["latency_p95"], marker="o", color=CORAL_RED, linewidth=2.5, label="Latencia p95 observada")
    ax1.axhline(y=50.0, color="#E76F51", linestyle="--", label="SLO Límite (50 ms)")
    ax1.axhline(y=100.0, color="darkred", linestyle=":", label="Umbral Alerta P1 (100 ms)")
    ax1.axvspan(6, 9, color=CORAL_RED, alpha=0.18, label="Ventana Incidente P1")
    ax1.annotate("Pico de Concurrencia\n(Latencia 178ms)", xy=(6, 178), xytext=(6.5, 150),
                 arrowprops=dict(facecolor="black", arrowstyle="->"), fontweight="bold", color="darkred")
    ax1.annotate("Ejecución Runbook RB-01\n(Escalado HPA: 2 -> 6 Pods)", xy=(9, 158), xytext=(9.2, 110),
                 arrowprops=dict(facecolor=TEAL, arrowstyle="->"), fontweight="bold", color=TEAL)
    ax1.set_title("Curva de Latencia p95 y Recuperación", fontweight="bold")
    ax1.set_xlabel("Ciclo Operativo")
    ax1.set_ylabel("Latencia (ms)")
    ax1.set_ylim(0, 195)
    ax1.legend(loc="upper right", fontsize=8.5)
    ax1.grid(True, linestyle="--", alpha=0.5)

    # Estado de Réplicas y CPU simulado
    epochs_inc1 = inc1_df["epoch"].values
    replicas = [2 if e < 8 else (6 if e < 13 else 4) for e in epochs_inc1]
    cpu_usage = [42 if e < 6 else (94 if e < 8 else (88 if e == 8 else (38 if e < 13 else 45))) for e in epochs_inc1]

    ax2.bar(epochs_inc1 - 0.2, replicas, width=0.4, color=NAVY_BLUE, label="Réplicas Kubernetes Activas", alpha=0.85)
    ax2.set_ylabel("Número de Pods", color=NAVY_BLUE, fontweight="bold")
    ax2.set_ylim(0, 8)
    ax2.set_xlabel("Ciclo Operativo")

    ax2_twin = ax2.twinx()
    ax2_twin.plot(epochs_inc1, cpu_usage, color=AMBER, marker="s", linewidth=2.2, label="Uso CPU Pod Promedio (%)")
    ax2_twin.axhline(y=80.0, color="red", linestyle="--", alpha=0.7, label="Umbral Saturación CPU (80%)")
    ax2_twin.set_ylabel("Uso de CPU (%)", color=AMBER, fontweight="bold")
    ax2_twin.set_ylim(0, 110)
    ax2_twin.grid(False)

    lines_1, labels_1 = ax2.get_legend_handles_labels()
    lines_2, labels_2 = ax2_twin.get_legend_handles_labels()
    ax2.legend(lines_1 + lines_2, labels_1 + labels_2, loc="upper right", fontsize=8)
    ax2.set_title("Capacidad Elástica: Autoescalado de Pods vs CPU", fontweight="bold")

    plt.tight_layout()
    out1 = "dashboards/img2_incident1_latency_mitigation.png"
    plt.savefig(out1, dpi=200)
    plt.close()
    print(f"[Graficado] Guardado: {out1}")

    # Incidente 2: Data Drift y Reentrenamiento
    fig, (ax3, ax4) = plt.subplots(1, 2, figsize=(14, 5.5), facecolor="white")
    fig.suptitle("MexBan - Simulación Incidente 2: Data Drift y Reentrenamiento Automatizado", 
                 fontsize=14, fontweight="bold", color=NAVY_BLUE)

    inc2_df = df[(df["epoch"] >= 13) & (df["epoch"] <= 26)]

    # F1 vs PSI
    ax3.plot(inc2_df["epoch"], inc2_df["f1_score"], color=TEAL, marker="o", linewidth=2.4, label="F1-Score Calidad")
    ax3.axhline(y=0.82, color=CORAL_RED, linestyle="--", label="SLO F1 Mínimo (0.82)")
    ax3.axvspan(16, 19, color=AMBER, alpha=0.2, label="Ventana Data Drift Cripto")
    ax3.annotate("Degradación por Vocabulario Cripto\n(F1 cae a 0.69)", xy=(17, 0.69), xytext=(15.5, 0.60),
                 arrowprops=dict(facecolor=CORAL_RED, arrowstyle="->"), fontweight="bold", color=CORAL_RED)
    ax3.annotate("Despliegue Canary v2.0\n(F1 restaurado a 0.91)", xy=(21, 0.91), xytext=(19.5, 0.95),
                 arrowprops=dict(facecolor=TEAL, arrowstyle="->"), fontweight="bold", color=TEAL)
    ax3.set_title("Evolución de Calidad F1 y Restauración con v2.0", fontweight="bold")
    ax3.set_xlabel("Ciclo Operativo")
    ax3.set_ylabel("F1-Score")
    ax3.set_ylim(0.50, 1.02)
    ax3.legend(loc="lower left", fontsize=8.5)
    ax3.grid(True, linestyle="--", alpha=0.5)

    # PSI y OOV
    ax4.plot(inc2_df["epoch"], inc2_df["max_psi"], color=CORAL_RED, marker="^", linewidth=2.2, label="Índice PSI de Deriva")
    ax4.plot(inc2_df["epoch"], inc2_df["oov_rate"], color="#7209B7", linestyle="-.", linewidth=2.0, label="Tasa Palabras Fuera Vocab (OOV)")
    ax4.axhline(y=0.20, color="darkred", linestyle="-", linewidth=1.5, label="Umbral Crítico Drift (0.20)")
    ax4.axhline(y=0.10, color=AMBER, linestyle="--", label="Umbral Alerta Leve (0.10)")
    ax4.annotate("Disparo RB-02: Retraining Pipeline\n(PSI pico detectado)", xy=(18, inc2_df["max_psi"].max()), 
                 xytext=(16.5, inc2_df["max_psi"].max() * 0.8),
                 arrowprops=dict(facecolor="black", arrowstyle="->"), fontweight="bold")
    ax4.set_title("Monitoreo de Data Drift (PSI) y OOV Rate", fontweight="bold")
    ax4.set_xlabel("Ciclo Operativo")
    ax4.set_ylabel("Métrica de Dispersión")
    ax4.set_ylim(-0.02, max(0.35, inc2_df["max_psi"].max() * 1.15))
    ax4.legend(loc="upper right", fontsize=8.5)
    ax4.grid(True, linestyle="--", alpha=0.5)

    plt.tight_layout()
    out2 = "dashboards/img3_incident2_datadrift_retraining.png"
    plt.savefig(out2, dpi=200)
    plt.close()
    print(f"[Graficado] Guardado: {out2}")

def create_architecture_diagram():
    """Genera un diagrama de arquitectura integral de observabilidad moderna para MexBan."""
    fig, ax = plt.subplots(figsize=(14, 8), facecolor="white")
    ax.axis("off")
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)

    # Título
    ax.text(50, 96, "Arquitectura de Observabilidad Moderna y Gobernanza MLOps - MexBan",
            ha="center", va="center", fontsize=15, fontweight="bold", color=NAVY_BLUE)
    ax.text(50, 92, "Integración de Métricas, Logs Estructurados, Trazas OpenTelemetry, MLflow y Auto-Remediación",
            ha="center", va="center", fontsize=10, fontstyle="italic", color=CHARCOAL)

    # Cajas principales
    def draw_box(x, y, w, h, title, items, color_header, color_body):
        rect_bg = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.5",
                                        facecolor=color_body, edgecolor=color_header, linewidth=1.8)
        ax.add_patch(rect_bg)
        rect_head = patches.FancyBboxPatch((x, y + h - 4.5), w, 4.5, boxstyle="round,pad=0.2",
                                          facecolor=color_header, edgecolor=color_header)
        ax.add_patch(rect_head)
        ax.text(x + w / 2, y + h - 2.3, title, ha="center", va="center",
                fontsize=10.5, fontweight="bold", color="white")
        
        y_text = y + h - 7.5
        for item in items:
            ax.text(x + 1.5, y_text, f"• {item}", ha="left", va="center", fontsize=8.8, color="#1D3557")
            y_text -= 3.2

    # Columnas:
    # 1. Ingesta y Seguridad
    draw_box(4, 52, 26, 34, "1. INGESTA & SEGURIDAD", [
        "Canales: Banca Móvil, Web, Call Center",
        "API Gateway Kong (mTLS, Auth)",
        "Rate Limiting & Queue Buffer",
        "PII Sanitizer: Enmascaramiento RFC/Cuentas",
        "Generación OpenTelemetry Trace/Span IDs"
    ], NAVY_BLUE, "#EDF2F7")

    # 2. Inferencia y Servicio
    draw_box(37, 52, 26, 34, "2. INFERENCIA & SERVICIO", [
        "Kubernetes Cluster (EKS/GKE)",
        "Microservicio: /api/v1/sentiment",
        "Modelo Activo: DistilBERT v1.0 / v2.0",
        "Circuit Breaker (Respaldo Léxico)",
        "In-Memory Cache Redis (Sub-5ms)",
        "Sidecar OpenTelemetry Collector"
    ], "#1D3557", "#EDF2F7")

    # 3. Gobernanza & MLflow
    draw_box(70, 52, 26, 34, "3. GOBERNANZA & MLFLOW", [
        "MLflow Tracking Server",
        "MLflow Model Registry (Staging/Prod)",
        "Versionado de Datasets DVC / S3",
        "Monitoreo Continuo de Métricas",
        "Delayed Feedback Human-in-the-Loop",
        "Auditoría y Trazabilidad Regulatoria"
    ], "#028090", "#E0F2F1")

    # Fila Inferior
    # 4. Observabilidad: Métricas, Logs, Trazas
    draw_box(4, 8, 42, 36, "4. PILARES DE OBSERVABILIDAD EN TIEMPO REAL", [
        "MÉTRICAS (Prometheus + Grafana):",
        "  - Golden Signals: Latencia (p50, p95, p99), Throughput, Errores 5xx",
        "  - Recursos: CPU, Memoria, Saturación de Pods",
        "LOGS ESTRUCTURADOS (OpenSearch / Elasticsearch):",
        "  - Esquema JSON: request_id, model_version, probs, latency_ms",
        "TRAZAS DISTRIBUIDAS (Jaeger / OpenTelemetry):",
        "  - Propagación de contexto por Gateway -> Tokenizer -> Inferencia",
        "DETECTOR DE DRIFT: PSI, KS-test, Wasserstein, OOV Rate"
    ], "#E76F51", "#FFF3E0")

    # 5. Alertamiento y Auto-Remediación
    draw_box(52, 8, 44, 36, "5. ALERTAMIENTO INTELIGENTE & AUTO-REMEDIACIÓN", [
        "MOTOR DE ALERTAS SLO & ERROR BUDGETS:",
        "  - Burn Rate Multi-Window (14.4x -> P1 Inmediato)",
        "  - P1: PagerDuty On-Call (MTTR < 5 min)",
        "  - P2: Slack #ops-mlops + Ticket Jira Prioritario",
        "ACCIONES AUTOMATIZADAS (RUNBOOKS):",
        "  - Runbook RB-01: Auto-escalado Horizontal (HPA 2 -> 6 Pods)",
        "  - Runbook RB-02: Fallback Seguro + Retraining Automático",
        "  - Flagger Canary Deployment (10% -> 50% -> 100%) con Rollback"
    ], "#2A9D8F", "#E8F8F5")

    # Flechas conectores
    arrow_style = dict(arrowstyle="->", lw=2, color="#457B9D")
    ax.annotate("", xy=(37, 69), xytext=(30, 69), arrowprops=arrow_style)
    ax.annotate("", xy=(70, 69), xytext=(63, 69), arrowprops=arrow_style)
    ax.annotate("", xy=(25, 44), xytext=(25, 52), arrowprops=arrow_style)
    ax.annotate("", xy=(74, 44), xytext=(74, 52), arrowprops=arrow_style)
    ax.annotate("", xy=(52, 26), xytext=(46, 26), arrowprops=arrow_style)

    plt.tight_layout()
    out3 = "dashboards/img4_observability_architecture.png"
    plt.savefig(out3, dpi=200)
    plt.close()
    print(f"[Graficado] Guardado: {out3}")

def create_mlflow_dashboard_mockup():
    """Genera una imagen representativa del dashboard y Model Registry de MLflow."""
    fig, ax = plt.subplots(figsize=(14, 7), facecolor="#F5F7FA")
    ax.axis("off")
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)

    # Cabecera MLflow UI
    header = patches.Rectangle((2, 88), 96, 10, facecolor="#014B75", edgecolor="none")
    ax.add_patch(header)
    ax.text(5, 93, "mlflow", fontsize=20, fontweight="bold", color="white")
    ax.text(17, 93, "Tracking  |  Model Registry  |  Experiments  |  Artifacts", fontsize=11, color="#E2E8F0")
    ax.text(82, 93, "Workspace: MexBan-Production", fontsize=10, color="#CBD5E1")

    # Panel Central: Model Registry
    box_registry = patches.FancyBboxPatch((2, 48), 96, 36, boxstyle="round,pad=0.5",
                                         facecolor="white", edgecolor="#CBD5E1", linewidth=1.5)
    ax.add_patch(box_registry)
    ax.text(5, 80, "MLflow Model Registry - Registered Model: DistilBERT-MexBan-Sentiment", 
            fontsize=12, fontweight="bold", color=CHARCOAL)

    # Tabla de modelos
    table_y = 74
    headers = ["Version", "Stage", "F1-Score", "Accuracy", "Latencia p95", "Fecha Despliegue", "Estado Gobernanza"]
    col_x = [6, 18, 30, 42, 54, 68, 83]
    for x, h in zip(col_x, headers):
        ax.text(x, table_y, h, fontsize=9.5, fontweight="bold", color="#4A5568")
    
    line = patches.Rectangle((5, 71.5), 90, 0.8, facecolor="#E2E8F0")
    ax.add_patch(line)

    # Fila 1: v2.0.0
    r1_y = 66
    ax.text(col_x[0], r1_y, "v2.0.0", fontsize=9.5, fontweight="bold", color=NAVY_BLUE)
    badge1 = patches.Rectangle((col_x[1] - 1, r1_y - 2), 10, 4.5, facecolor="#D1FAE5", edgecolor="#10B981")
    ax.add_patch(badge1)
    ax.text(col_x[1], r1_y, "Production", fontsize=8.5, fontweight="bold", color="#065F46")
    ax.text(col_x[2], r1_y, "0.912", fontsize=9.5, color="#1F2937")
    ax.text(col_x[3], r1_y, "0.915", fontsize=9.5, color="#1F2937")
    ax.text(col_x[4], r1_y, "16.4 ms", fontsize=9.5, color="#1F2937")
    ax.text(col_x[5], r1_y, "2026-11-16 21:03", fontsize=9, color="#4B5563")
    ax.text(col_x[6], r1_y, "APROBADO (RB-02)", fontsize=9, fontweight="bold", color="#059669")

    # Fila 2: v1.0.0
    r2_y = 57
    ax.text(col_x[0], r2_y, "v1.0.0", fontsize=9.5, fontweight="bold", color="#64748B")
    badge2 = patches.Rectangle((col_x[1] - 1, r2_y - 2), 9.5, 4.5, facecolor="#F1F5F9", edgecolor="#94A3B8")
    ax.add_patch(badge2)
    ax.text(col_x[1], r2_y, "Archived", fontsize=8.5, color="#475569")
    ax.text(col_x[2], r2_y, "0.875", fontsize=9.5, color="#64748B")
    ax.text(col_x[3], r2_y, "0.881", fontsize=9.5, color="#64748B")
    ax.text(col_x[4], r2_y, "23.3 ms", fontsize=9.5, color="#64748B")
    ax.text(col_x[5], r2_y, "2026-10-11 20:35", fontsize=9, color="#64748B")
    ax.text(col_x[6], r2_y, "SUPERADO POR DRIFT", fontsize=9, color="#DC2626")

    # Panel Inferior: Corridas y Artefactos de MLflow
    box_runs = patches.FancyBboxPatch((2, 4), 96, 40, boxstyle="round,pad=0.5",
                                      facecolor="white", edgecolor="#CBD5E1", linewidth=1.5)
    ax.add_patch(box_runs)
    ax.text(5, 39, "MLflow Experiment Tracking - Corrida: Produccion_Monitoreo_Continuo (ID: b2a37d19...)", 
            fontsize=11.5, fontweight="bold", color=CHARCOAL)

    metrics_summary = [
        ("SLO Latencia p95:", "< 50.0 ms (Cumplido 96.2%)"),
        ("Error Budget Mensual:", "43.2 min (Restante: 71.0%)"),
        ("Métrica Drift PSI:", "Max: 0.28 (Incidente 2 resuelto)"),
        ("Total Infecciones Monitoreadas:", "1,040 consultas bancarias"),
        ("Estatus Servicio:", "100% OPERACIONAL / EN LÍNEA"),
        ("Alertas Despachadas:", "3 Inteligentes (1 P1, 2 P2)")
    ]

    for idx, (label, val) in enumerate(metrics_summary):
        row = idx // 2
        col = idx % 2
        px = 6 if col == 0 else 52
        py = 32 - row * 7.5
        ax.text(px, py, label, fontsize=9.5, fontweight="bold", color=NAVY_BLUE)
        ax.text(px + 22, py, val, fontsize=9.5, color=CHARCOAL)

    out4 = "dashboards/img5_mlflow_tracking_ui_mockup.png"
    plt.savefig(out4, dpi=200)
    plt.close()
    print(f"[Graficado] Guardado: {out4}")

if __name__ == "__main__":
    df = pd.read_csv("dashboards/simulation_timeline_metrics.csv")
    create_operational_dashboard(df)
    create_incident_detail_charts(df)
    create_architecture_diagram()
    create_mlflow_dashboard_mockup()
    print("Todos los gráficos generados satisfactoriamente.")
