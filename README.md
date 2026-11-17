# Actividad 8: Sistema de Monitorización Proactiva y Gobernanza Operativa de Modelos de IA en Producción

**Gestión de Proyectos de IA**  
**Estudiante:** Juan Manuel Carreón Chávez  
**Matrícula:** AL07182807  
**Fecha:** 16 de Noviembre de 2026  
**Empresa / Caso de Estudio:** MexBan (Institución Bancaria Tradicional en Proceso de Digitalización)  
**Modelo en Producción:** DistilBERT para Clasificación en Tiempo Real de Retroalimentación de Clientes  

---

## 1. Descripción del Proyecto

Este repositorio contiene el diseño, implementación y validación de una arquitectura de **observabilidad moderna, monitorización proactiva y gobernanza operativa MLOps** para el servicio de inferencia del modelo **DistilBERT** (seleccionado en la *Actividad 4*) en la institución bancaria **MexBan**.

El sistema integra de forma sinérgica:
- **Tres Pilares de Observabilidad:** Métricas operativas (Golden Signals) y de ML, Logs estructurados en JSON con enmascaramiento estricto de PII financiera (cumplimiento CNBV y PCI-DSS), y Trazas distribuidas compatibles con OpenTelemetry y MLflow Tracing.
- **Alertamiento Inteligente:** Reglas alineadas con Objetivos de Nivel de Servicio (SLOs) y Presupuestos de Error (*Error Budgets*), priorización operativa (P1, P2, P3), cálculo de tasa de quemado (*Burn Rate*) y técnicas de reducción de fatiga de alertas (persistencia temporal e histéresis).
- **Detección Estadística de Data Drift y Concept Drift:** Cálculo de *Population Stability Index* (PSI), pruebas Kolmogorov-Smirnov (KS-test), distancia de Wasserstein y tasa de términos fuera de vocabulario (*Out-Of-Vocabulary* - OOV).
- **Dashboards Operativos en Tiempo Real:** Visualización en tres niveles de gobierno (Ejecutivo, SRE y MLOps/Data Science).
- **Runbooks de Respuesta a Incidentes Automatizados:**
  - **Runbook RB-01 (P1):** Mitigación automática de saturación de latencia mediante Auto-escalado Horizontal de Pods (HPA) de 2 a 6 réplicas y activación de caché semántica Redis.
  - **Runbook RB-02 (P2):** Respuesta ante deriva severa de datos mediante Fallback seguro a clasificador heurístico, reentrenamiento automatizado registrado en MLflow y despliegue progresivo Canary de la versión **v2.0.0**.
- **Gobernanza con MLflow:** Servidor local de seguimiento de experimentos, registro continuo de parámetros y métricas, y gestión del ciclo de vida en el **MLflow Model Registry** (*DistilBERT-MexBan-Sentiment* v1.0.0 &rarr; v2.0.0).

---

## 2. Arquitectura de Observabilidad y MLOps

```
+---------------------------------------------------------------------------------------+
|                                ARQUITECTURA MEXBAN                                    |
+---------------------------------------------------------------------------------------+
|  [Banca Móvil / Web]                                                                  |
|          |                                                                            |
|          v                                                                            |
|  [API Gateway Kong] ---> [PII Sanitizer] ---> [DistilBERT Pods (Kubernetes HPA)]       |
|                                                      |                                |
|                                                      v                                |
|                        +---------------------------------------------+                |
|                        |          TELEMETRÍA Y OBSERVABILIDAD        |                |
|                        |  - Métricas: Latencia (p95), Errores, CPU   |                |
|                        |  - Logs JSON Estructurados                  |                |
|                        |  - Trazas Distribuidas (Trace & Span IDs)   |                |
|                        +---------------------------------------------+                |
|                                       |               |                               |
|                                       v               v                               |
|                  [Motor Estadístico de Drift]   [Motor Alertas SLO]                   |
|                  (PSI, KS-Test, Wasserstein)    (Error Budget Burn Rate)              |
|                                       |               |                               |
|                                       +-------+-------+                               |
|                                               |                                       |
|                                               v                                       |
|                           [RUNBOOKS AUTOMATIZADOS / GOBERNANZA]                       |
|                           - RB-01: Auto-escalado HPA (2 -> 6 Pods)                    |
|                           - RB-02: Fallback Seguro + Retraining Pipeline              |
|                           - MLflow Model Registry (v1 Archived -> v2 Prod)            |
+---------------------------------------------------------------------------------------+
```

---

## 3. Resumen de Incidentes Simulados y Mitigación

| Incidente Simulado | Métrica Afectada | Valor en Crisis | Valor Restaurado | MTTR | Acción / Runbook |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Incidente 1:** Saturación de Latencia por Concurrencia | Latencia p95 de Inferencia | **178.0 ms** | **16.4 ms** | **4.2 min** | **Runbook RB-01:** Auto-escalado HPA de 2 a 6 réplicas y activación de caché Redis. |
| **Incidente 2:** Data Drift por Cripto-Billetera | F1-Score / Índice PSI | **F1: 0.69 \| PSI: 0.28** | **F1: 0.912 \| PSI: 0.05** | **9.5 min** | **Runbook RB-02:** Fallback heurístico seguro + Reentrenamiento MLflow y despliegue Canary v2.0. |

---

## 4. Estructura del Repositorio

```text
actividad8_gestion_proyectos_ia/
├── Actividad4.pdf                                      # PDF base de referencia (Actividad 4)
├── Actividad8_Reporte_Tecnico.pdf                      # Documento técnico oficial final (8 páginas)
├── README.md                                           # Documentación del proyecto
├── requirements.txt                                    # Dependencias de Python
├── mlflow_tracking.db                                  # Base de datos de tracking de MLflow
├── src/                                                # Módulos fuente de observabilidad
│   ├── __init__.py
│   ├── metrics_logger.py                              # Logs estructurados JSON, trazas y métricas
│   ├── drift_detector.py                              # Motor estadístico (PSI, KS-test, Wasserstein, OOV)
│   ├── alert_engine.py                                # Motor de alertas inteligentes SLO y Error Budgets
│   ├── runbook_automation.py                          # Automatización de Runbooks RB-01 y RB-02
│   └── observability_service.py                       # Orquestador del servicio y simulación
├── scripts/                                            # Scripts ejecutables
│   ├── run_full_simulation.py                         # Simulación completa de 26 ciclos con MLflow
│   ├── generate_visuals.py                            # Generación de gráficos y dashboards de alta resolución
│   ├── build_notebook.py                              # Generación del Jupyter Notebook interactivo
│   └── build_report_pdf.py                            # Compilador del reporte técnico oficial en PDF
├── notebooks/
│   └── Actividad8_Monitoreo_Observabilidad.ipynb      # Notebook interactivo con salidas y visualizaciones
└── dashboards/                                         # Artefactos, logs y gráficos generados
    ├── dispatched_alerts_log.csv                      # Registro de alertas despachadas
    ├── incidents_execution_report.json                 # Bitácora detallada de incidentes
    ├── sample_structured_log.json                     # Muestra del esquema JSON de log
    ├── simulation_timeline_metrics.csv                 # Métricas de la simulación ciclo a ciclo
    ├── img1_realtime_operational_dashboard.png         # Dashboard operativo de 4 paneles
    ├── img2_incident1_latency_mitigation.png           # Gráfico de análisis del Incidente 1
    ├── img3_incident2_datadrift_retraining.png         # Gráfico de análisis del Incidente 2
    ├── img4_observability_architecture.png             # Diagrama de arquitectura de observabilidad
    └── img5_mlflow_tracking_ui_mockup.png              # Evidencia de MLflow Tracking y Model Registry
```

---

## 5. Instrucciones de Instalación y Ejecución

### Prerrequisitos
- Python 3.10 o superior instalado.

### 1. Clonar el repositorio y configurar el entorno virtual
```bash
git clone https://github.com/JuanMCarreonCh/actividad8_gestion_proyectos_ia.git
cd actividad8_gestion_proyectos_ia

# Crear entorno virtual
python -m venv .venv

# Activar entorno (Windows PowerShell)
.\.venv\Scripts\Activate.ps1

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Ejecutar la simulación de observabilidad y registro en MLflow
```bash
python scripts/run_full_simulation.py
```

### 3. Generar los dashboards y gráficos de alta resolución
```bash
python scripts/generate_visuals.py
```

### 4. Compilar el reporte técnico oficial en PDF
```bash
python scripts/build_report_pdf.py
```
El documento generado se guardará como `Actividad8_Reporte_Tecnico.pdf`, incluyendo la portada oficial con el diseño idéntico al de la Actividad 4.

### 5. Abrir el Jupyter Notebook interactivo
```bash
jupyter notebook notebooks/Actividad8_Monitoreo_Observabilidad.ipynb
```

### 6. Visualizar la interfaz gráfica de MLflow
```bash
mlflow ui --backend-store-uri sqlite:///mlflow_tracking.db --port 5000
```
Abrir en el navegador: `http://localhost:5000` para explorar las corridas, métricas comparativas y el **Model Registry** con las versiones `v1.0.0` y `v2.0.0`.

---

## 6. Documento Técnico de Entrega

El reporte técnico completo en PDF, estructurado conforme a la rúbrica oficial de la actividad y con la misma portada de la Actividad 4, está disponible en el archivo:
- [Actividad8_Reporte_Tecnico.pdf](Actividad8_Reporte_Tecnico.pdf)
