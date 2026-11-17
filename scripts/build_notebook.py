"""
build_notebook.py
Genera el notebook interactivo Actividad8_Monitoreo_Observabilidad.ipynb
"""

import json
import os

def create_notebook():
    nb = {
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "# Actividad 8: Sistema de Monitorización Proactiva y Gobernanza Operativa de IA\n",
                    "## Caso de Estudio: MexBan - Inferencia de DistilBERT en Producción\n",
                    "\n",
                    "**Estudiante:** Juan Manuel Carreón Chávez  \n",
                    "**Matrícula:** AL07182807  \n",
                    "**Materia:** Gestión de Proyectos de IA  \n",
                    "**Fecha:** 16 de Noviembre de 2026  \n",
                    "\n",
                    "---\n",
                    "### 1. Resumen y Objetivos\n",
                    "En este notebook se implementa la arquitectura integral de **observabilidad moderna** (Métricas, Logs Estructurados y Trazas Distribuidas OpenTelemetry) para el modelo de análisis de sentimientos **DistilBERT**, seleccionado en la Actividad 4 y puesto en servicio en producción para la institución bancaria **MexBan**.\n",
                    "\n",
                    "Se abordan los siguientes componentes clave:\n",
                    "1. **Telemetría y Pilares de Observabilidad:** Captura de métricas Golden Signals (latencia percentiles, throughput, errores), logs JSON estructurados con enmascaramiento PII y trazas de spans.\n",
                    "2. **Detección Estadística de Data Drift y Concept Drift:** Implementación de Population Stability Index (PSI), prueba Kolmogorov-Smirnov (KS-test), Distancia de Wasserstein y tasa Out-Of-Vocabulary (OOV).\n",
                    "3. **Motor de Alertas Inteligentes (SLO & Error Budgets):** Definición rigurosa de SLIs/SLOs, cálculo de tasa de quemado (burn rate) y reducción de fatiga con histéresis y persistencia temporal.\n",
                    "4. **Simulación de Incidentes Críticos y Runbooks Automatizados:**\n",
                    "   - *Incidente 1:* Saturación de concurrencia y pico de latencia (Runbook RB-01: Auto-escalado HPA de 2 a 6 réplicas y activación de caché Redis).\n",
                    "   - *Incidente 2:* Data Drift severo y degradación de F1 por lanzamiento de Cripto-Billetera (Runbook RB-02: Fallback seguro, reentrenamiento automatizado con MLflow y Canary deployment de v2.0).\n",
                    "5. **Seguimiento con MLflow:** Registro de experimentos, parámetros, métricas continuas, artefactos y versionado en MLflow Model Registry."
                ]
            },
            {
                "cell_type": "code",
                "execution_count": 1,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# Configuración de entorno e importaciones\n",
                    "import os\n",
                    "import sys\n",
                    "import json\n",
                    "import time\n",
                    "import numpy as np\n",
                    "import pandas as pd\n",
                    "import matplotlib.pyplot as plt\n",
                    "\n",
                    "# Agregar directorio raíz\n",
                    "sys.path.insert(0, os.path.abspath('..'))\n",
                    "\n",
                    "from src.metrics_logger import ObservabilityTelemetry\n",
                    "from src.drift_detector import DriftDetector\n",
                    "from src.alert_engine import SmartAlertEngine\n",
                    "from src.runbook_automation import RunbookAutomationEngine\n",
                    "from src.observability_service import MexBanObservabilityService\n",
                    "\n",
                    "print('Entorno y módulos de observabilidad cargados exitosamente.')"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "### 2. Definición de Indicadores: Logs Estructurados y Trazas Distribuidas\n",
                    "A continuación inspeccionamos el esquema JSON estructurado generado para cada inferencia, garantizando anonimización PII y trazabilidad extremo a extremo mediante IDs de spans compatibles con OpenTelemetry."
                ]
            },
            {
                "cell_type": "code",
                "execution_count": 2,
                "metadata": {},
                "outputs": [],
                "source": [
                    "telemetry = ObservabilityTelemetry()\n",
                    "sample_log = telemetry.record_inference(\n",
                    "    text='Excelente atención en la sucursal Reforma, trámite de tarjeta muy rápido',\n",
                    "    prediction='Positivo',\n",
                    "    confidence=0.962,\n",
                    "    probabilities={'Positivo': 0.962, 'Negativo': 0.018, 'Neutro': 0.020},\n",
                    "    latency_ms=17.4,\n",
                    "    channel='mobile_banking',\n",
                    "    http_status=200\n",
                    ")\n",
                    "print(telemetry.export_sample_json_log())"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "### 3. Ejecución de la Simulación Integral de Producción y Registro en MLflow\n",
                    "Ejecutamos el ciclo continuo de simulación a lo largo de 26 ventanas operativas que abarcan operación normal, los dos incidentes simulados y la intervención automatizada de los Runbooks."
                ]
            },
            {
                "cell_type": "code",
                "execution_count": 3,
                "metadata": {},
                "outputs": [],
                "source": [
                    "from scripts.run_full_simulation import run_simulation\n",
                    "df_sim, alerts_df, incidents_list = run_simulation()\n",
                    "print(f'Total de registros simulados: {len(df_sim)}')\n",
                    "df_sim.head()"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "### 4. Visualización del Dashboard Operativo en Tiempo Real\n",
                    "Mostramos los 4 paneles de control del estado operativo del modelo (Golden Signals y Salud de ML)."
                ]
            },
            {
                "cell_type": "code",
                "execution_count": 4,
                "metadata": {},
                "outputs": [],
                "source": [
                    "from IPython.display import Image, display\n",
                    "display(Image(filename='../dashboards/img1_realtime_operational_dashboard.png'))"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "### 5. Análisis del Incidente 1: Degradación de Latencia y Auto-escalado HPA\n",
                    "Revisión de la curva de latencia p95, saturación de CPU y mitigación ejecutada por el Runbook RB-01."
                ]
            },
            {
                "cell_type": "code",
                "execution_count": 5,
                "metadata": {},
                "outputs": [],
                "source": [
                    "display(Image(filename='../dashboards/img2_incident1_latency_mitigation.png'))"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "### 6. Análisis del Incidente 2: Data Drift y Reentrenamiento MLflow v2.0\n",
                    "Evaluación de la deriva de datos (PSI) tras la introducción del vocabulario de cripto-billetera, degradación de F1-Score y recuperación mediante despliegue de DistilBERT v2.0."
                ]
            },
            {
                "cell_type": "code",
                "execution_count": 6,
                "metadata": {},
                "outputs": [],
                "source": [
                    "display(Image(filename='../dashboards/img3_incident2_datadrift_retraining.png'))"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "### 7. Gobernanza en MLflow Model Registry\n",
                    "Inspección del estado de los modelos versionados en MLflow."
                ]
            },
            {
                "cell_type": "code",
                "execution_count": 7,
                "metadata": {},
                "outputs": [],
                "source": [
                    "display(Image(filename='../dashboards/img5_mlflow_tracking_ui_mockup.png'))"
                ]
            }
        ],
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "name": "python",
                "version": "3.10.6"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 4
    }

    out_file = "notebooks/Actividad8_Monitoreo_Observabilidad.ipynb"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=2)
    print(f"Notebook creado con éxito en: {out_file}")

if __name__ == "__main__":
    create_notebook()
