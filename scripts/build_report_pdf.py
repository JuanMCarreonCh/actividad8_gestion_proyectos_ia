"""
build_report_pdf.py
Generación del Reporte Técnico Oficial en PDF para la Actividad 8.
Reutiliza la portada exacta de Actividad4.pdf y genera un documento técnico exhaustivo con maquetación impecable.
"""

import os
import sys
import io
import json
import pypdf
import pandas as pd

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch, cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, PageBreak
)
from reportlab.pdfgen import canvas

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Colores corporativos basados en Actividad 4
COLOR_NAVY = colors.HexColor("#0F3B7A")
COLOR_CYAN = colors.HexColor("#008899")
COLOR_TEAL = colors.HexColor("#00A896")
COLOR_DARK = colors.HexColor("#1D2D44")
COLOR_MUTED = colors.HexColor("#555555")
COLOR_LIGHT_BG = colors.HexColor("#F8F9FA")
COLOR_BORDER = colors.HexColor("#DDE2E5")
COLOR_CARD_BG = colors.HexColor("#F0F4F8")

class NumberedCanvas(canvas.Canvas):
    """Canvas de dos pasadas para numerar páginas dinámicamente: Página X de Y."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica-Oblique", 9)
        self.setFillColor(COLOR_CYAN)

        page_width, page_height = A4
        self.drawString(45, page_height - 35, "Actividad 8. Sistema de monitorización proactiva y observabilidad.")
        self.setStrokeColor(COLOR_CYAN)
        self.setLineWidth(0.6)
        self.line(45, page_height - 40, page_width - 45, page_height - 40)

        # Pie de página inferior
        self.setFont("Helvetica", 8.5)
        self.setFillColor(COLOR_MUTED)
        self.drawString(45, 30, "MexBan • Gestión de Proyectos de IA • Juan Manuel Carreón Chávez (AL07182807)")
        
        current_page_number = self._pageNumber + 1
        total_pages = page_count + 1
        page_str = f"Página {current_page_number} de {total_pages}"
        self.drawRightString(page_width - 45, 30, page_str)
        self.setStrokeColor(COLOR_BORDER)
        self.setLineWidth(0.5)
        self.line(45, 42, page_width - 45, 42)

        self.restoreState()

def generate_cover_page(output_cover_path: str):
    """Extrae y actualiza la portada de Actividad4.pdf con la nueva titulación y fecha."""
    reader = pypdf.PdfReader("Actividad4.pdf")
    
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=A4)

    can.setFillColor(colors.white)
    can.setStrokeColor(colors.white)
    can.rect(20, 675, 420, 110, fill=True, stroke=False)
    can.rect(470, 182, 115, 25, fill=True, stroke=False)

    can.setFillColor(COLOR_NAVY)
    can.setFont("Helvetica-Bold", 38)
    can.drawString(27.24, 742.18, "Actividad 8")

    can.setFont("Helvetica-Bold", 16)
    can.drawString(27.24, 713.26, "Monitorización y Observabilidad de Modelos de IA.")

    can.setFillColor(COLOR_CYAN)
    can.setFont("Times-Italic", 15.96)
    can.drawRightString(568, 188.90, "16/11/2026")

    can.save()
    packet.seek(0)

    overlay_pdf = pypdf.PdfReader(packet)
    writer = pypdf.PdfWriter()
    p = writer.add_page(reader.pages[0])
    p.merge_page(overlay_pdf.pages[0])

    with open(output_cover_path, "wb") as f:
        writer.write(f)
    print(f"[PDF] Portada generada en: {output_cover_path}")

def build_pdf_document():
    cover_pdf_path = "cover_page_act8.pdf"
    body_pdf_path = "body_content_act8.pdf"
    final_pdf_path = "Actividad8_Reporte_Tecnico.pdf"

    generate_cover_page(cover_pdf_path)

    styles = getSampleStyleSheet()

    body_style = ParagraphStyle(
        "CustomBody",
        parent=styles["Normal"],
        fontName="Times-Roman",
        fontSize=9.5,
        leading=13.5,
        textColor=COLOR_DARK,
        alignment=4,
        spaceAfter=5
    )

    body_bold = ParagraphStyle(
        "CustomBodyBold",
        parent=body_style,
        fontName="Times-Bold"
    )

    h1_style = ParagraphStyle(
        "CustomH1",
        fontName="Helvetica-Bold",
        fontSize=17,
        leading=21,
        textColor=COLOR_NAVY,
        spaceBefore=10,
        spaceAfter=6,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        "CustomH2",
        fontName="Helvetica-Bold",
        fontSize=12.5,
        leading=16,
        textColor=COLOR_NAVY,
        spaceBefore=9,
        spaceAfter=5,
        keepWithNext=True
    )

    h3_style = ParagraphStyle(
        "CustomH3",
        fontName="Times-BoldItalic",
        fontSize=10.5,
        leading=14,
        textColor=COLOR_CYAN,
        spaceBefore=7,
        spaceAfter=3,
        keepWithNext=True
    )

    caption_style = ParagraphStyle(
        "CustomCaption",
        fontName="Helvetica-Oblique",
        fontSize=8,
        leading=10.5,
        textColor=COLOR_MUTED,
        alignment=1,
        spaceBefore=3,
        spaceAfter=8
    )

    code_style = ParagraphStyle(
        "CustomCode",
        fontName="Courier",
        fontSize=7,
        leading=9.2,
        textColor=colors.HexColor("#212529"),
        spaceBefore=2,
        spaceAfter=2
    )

    story = []

    # =========================================================================
    # PÁGINA 2: INTRODUCCIÓN, CONTINUIDAD Y ARQUITECTURA
    # =========================================================================
    story.append(Paragraph("Actividad práctica", h1_style))
    story.append(Paragraph("Problemática Seleccionada: MexBan y Despliegue de DistilBERT en Producción", h2_style))
    
    story.append(Paragraph(
        "Para esta actividad damos continuidad directa a la institución financiera ficticia <b>MexBan</b>, "
        "presentada en la <i>Actividad 4</i>. MexBan es un banco comercial del sector tradicional que, frente a la intensa "
        "competencia de los neobancos y fintechs emergentes, aceleró su transformación digital integrando canales de autoservicio "
        "(Banca Móvil, portal Web y Terminales de Autoservicio en Sucursal). En la fase anterior se evaluaron múltiples modelos "
        "basados en la arquitectura Transformer y se seleccionó <b>DistilBERT</b> debido a su óptimo equilibrio entre precisión "
        "(F1-Score: 0.8759, Exactitud: 88.1%) y baja latencia de inferencia (17.43 ms frente a los más de 30 ms de RoBERTa y BERT-base).",
        body_style
    ))

    story.append(Paragraph(
        "Actualmente, dicho modelo ha sido encapsulado en un microservicio de inferencia en tiempo real contenerizado sobre Kubernetes "
        "(<code>/api/v1/sentiment/predict</code>), consumido por los módulos de experiencia del cliente para categorizar de forma inmediata "
        "opiniones, quejas, recomendaciones y felicitaciones en tres categorías: <b>Positivo</b>, <b>Negativo</b> y <b>Neutro</b>. "
        "Sin embargo, el despliegue en un entorno bancario crítico demanda un marco integral de <b>observabilidad moderna, monitorización "
        "proactiva y gobernanza operativa MLOps</b>, garantizando la detección temprana de anomalías, deriva en los datos (<i>Data Drift</i>), "
        "degradación del modelo (<i>Concept Drift</i>) y el estricto cumplimiento de los Acuerdos de Nivel de Servicio (SLAs y SLOs).",
        body_style
    ))

    story.append(Paragraph("1. Arquitectura de Observabilidad y Gobernanza MLOps", h2_style))
    story.append(Paragraph(
        "Bajo las directrices de la observabilidad moderna, el sistema no se limita a recolectar métricas aisladas de CPU o memoria, "
        "sino que integra de manera sinérgica los tres pilares fundamentales: <b>Métricas de Servicio y ML</b>, <b>Logs Estructurados "
        "con Cumplimiento Regulatorio Financiero</b> y <b>Trazabilidad Distribuida (OpenTelemetry / MLflow Tracing)</b>.",
        body_style
    ))

    if os.path.exists("dashboards/img4_observability_architecture.png"):
        story.append(Image("dashboards/img4_observability_architecture.png", width=7.2*inch, height=3.6*inch))
        story.append(Paragraph("Img1. Diagrama de Arquitectura de Observabilidad Moderna, Alertamiento y Auto-Remediación en MexBan.", caption_style))

    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 3: DEFINICIÓN DE INDICADORES (MÉTRICAS, LOGS, TRAZAS)
    # =========================================================================
    story.append(Paragraph("2. Definición Detallada de Indicadores Técnicos", h2_style))
    
    story.append(Paragraph("A. Métricas Operativas de Infraestructura y Servicio (Golden Signals)", h3_style))
    story.append(Paragraph(
        "Se implementan las cuatro señales doradas recomendadas por la ingeniería de confiabilidad de sitios (SRE de Google):",
        body_style
    ))

    metric_table_data = [
        [Paragraph("<b>Métrica / Indicador</b>", body_bold), Paragraph("<b>Definición Técnica</b>", body_bold), Paragraph("<b>SLO / Umbral</b>", body_bold), Paragraph("<b>Frecuencia</b>", body_bold)],
        [Paragraph("<b>Latencia p50 / p95 / p99</b>", body_style), Paragraph("Tiempo de respuesta extremo a extremo del microservicio medido en percentiles móviles de 5 min.", body_style), Paragraph("p95 &lt; 50 ms<br/>p99 &lt; 90 ms", body_style), Paragraph("Tiempo real (10s)", body_style)],
        [Paragraph("<b>Throughput (RPS)</b>", body_style), Paragraph("Tasa de peticiones concurrentes por segundo procesadas por los pods de inferencia.", body_style), Paragraph("Capacidad 50 a 400 RPS", body_style), Paragraph("Tiempo real (10s)", body_style)],
        [Paragraph("<b>Tasa de Errores (Error Rate)</b>", body_style), Paragraph("Porcentaje de respuestas HTTP fallidas (códigos 5xx, timeouts o abortos de red).", body_style), Paragraph("&lt; 0.1% de errores", body_style), Paragraph("Tiempo real", body_style)],
        [Paragraph("<b>Saturación de Recursos</b>", body_style), Paragraph("Consumo de CPU, memoria RAM y memoria de inferencia por cada réplica de Kubernetes.", body_style), Paragraph("CPU &lt; 75%<br/>RAM &lt; 80%", body_style), Paragraph("Tiempo real (30s)", body_style)]
    ]
    t_svc = Table(metric_table_data, colWidths=[1.8*inch, 2.7*inch, 1.4*inch, 1.3*inch])
    t_svc.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), COLOR_CARD_BG),
        ("GRID", (0, 0), (-1, -1), 0.5, COLOR_BORDER),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(t_svc)

    story.append(Spacer(1, 6))
    story.append(Paragraph("B. Métricas de Desempeño y Calidad de Machine Learning", h3_style))
    story.append(Paragraph(
        "A diferencia del software convencional, los modelos de IA pueden experimentar fallas silenciosas donde la infraestructura "
        "opera con normalidad (código 200) pero la calidad de las predicciones se degrada drásticamente. Se vigilan las siguientes métricas:",
        body_style
    ))

    ml_metrics_data = [
        [Paragraph("<b>Métrica de ML</b>", body_bold), Paragraph("<b>Propósito y Fórmula</b>", body_bold), Paragraph("<b>Línea Base</b>", body_bold), Paragraph("<b>Umbral de Degradación</b>", body_bold)],
        [Paragraph("<b>F1-Score Ponderado</b>", body_style), Paragraph("Media armónica de precisión y recall ponderada por el soporte de cada clase.", body_style), Paragraph("0.8759", body_style), Paragraph("SLO: &gt;= 0.82 (Drop máx. 6%)", body_style)],
        [Paragraph("<b>Exactitud (Accuracy)</b>", body_style), Paragraph("Proporción global de clasificaciones correctas respecto al total auditado.", body_style), Paragraph("88.1%", body_style), Paragraph("Alerta si cae &lt; 83%", body_style)],
        [Paragraph("<b>Confianza Media Softmax</b>", body_style), Paragraph("Promedio de la probabilidad máxima asignada por DistilBERT a la clase predicha.", body_style), Paragraph("0.89", body_style), Paragraph("Alerta preventiva si &lt; 0.72", body_style)],
        [Paragraph("<b>Deriva de Datos (PSI)</b>", body_style), Paragraph("Índice de Estabilidad Poblacional en longitud de texto, tokens y predicciones.", body_style), Paragraph("0.04", body_style), Paragraph("P2 si &gt;= 0.18; P1 si &gt;= 0.25", body_style)]
    ]
    t_ml = Table(ml_metrics_data, colWidths=[1.8*inch, 2.7*inch, 1.3*inch, 1.4*inch])
    t_ml.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), COLOR_CARD_BG),
        ("GRID", (0, 0), (-1, -1), 0.5, COLOR_BORDER),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(t_ml)

    story.append(Spacer(1, 6))
    story.append(Paragraph("C. Logs Estructurados y Anonimización PII (Protección Financiera)", h3_style))
    story.append(Paragraph(
        "Por cumplimiento estricto con las regulaciones de la Comisión Nacional Bancaria y de Valores (CNBV) y el estándar PCI-DSS, "
        "está prohibido almacenar en logs Información Personal Identificable (PII), tales como números de tarjeta de crédito (PAN), "
        "claves de acceso bancario o números de cuenta. El microservicio incorpora un middleware de sanitización que enmascara dichos datos "
        "antes de despachar el log estructurado en formato JSON a OpenSearch:",
        body_style
    ))

    log_sample_text = (
        '{\n'
        '  "timestamp": "2026-11-16T21:03:00.000Z", "request_id": "req-9c84e1b7a2", "trace_id": "trace-4f91ab02e7",\n'
        '  "model_name": "DistilBERT-MexBan-Sentiment", "model_version": "v1.0.0", "channel": "mobile_banking",\n'
        '  "input_char_len": 72, "token_count": 12, "prediction": "Positivo", "confidence": 0.9421,\n'
        '  "probabilities": {"Positivo": 0.9421, "Negativo": 0.0279, "Neutro": 0.0300},\n'
        '  "latency_ms": 17.43, "http_status": 200, "pii_masked": true,\n'
        '  "spans": [\n'
        '    {"name": "api_gateway", "duration_ms": 0.85, "status": "OK"},\n'
        '    {"name": "pii_sanitizer", "duration_ms": 0.65, "status": "OK"},\n'
        '    {"name": "tokenization", "duration_ms": 2.10, "status": "OK"},\n'
        '    {"name": "model_inference", "duration_ms": 12.95, "status": "OK"},\n'
        '    {"name": "postprocessing_rules", "duration_ms": 0.88, "status": "OK"}\n'
        '  ]\n'
        '}'
    )
    t_log_box = Table([[Paragraph(f"<pre>{log_sample_text}</pre>", code_style)]], colWidths=[7.2*inch])
    t_log_box.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F4F6F9")),
        ("BOX", (0, 0), (-1, -1), 1, COLOR_NAVY),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(t_log_box)

    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 4: ALERTAS INTELIGENTES, SLOs Y ERROR BUDGETS
    # =========================================================================
    story.append(Paragraph("3. Diseño de Alertas Inteligentes, SLOs y Error Budgets", h2_style))
    story.append(Paragraph(
        "Para evitar la proliferación de falsos positivos y la <i>fatiga de alertas</i> en los equipos de ingeniería, "
        "el alertamiento se diseña rigurosamente sobre la metodología SRE basada en <b>Service Level Indicators (SLI)</b>, "
        "<b>Service Level Objectives (SLO)</b> y <b>Presupuestos de Error (Error Budgets)</b>.",
        body_style
    ))

    story.append(Paragraph("A. Definición Formal de SLOs y Presupuestos de Error", h3_style))
    story.append(Paragraph(
        "MexBan establece un compromiso de disponibilidad mensual del <b>99.9%</b>. Esto implica un <b>Presupuesto de Error mensual "
        "de 0.1%</b>, equivalente a exactamente <b>43.2 minutos de indisponibilidad o degradación total permitida por mes</b>. "
        "Cada anomalía en latencia o errores consume progresivamente este presupuesto. Se formalizan cuatro reglas inteligentes:",
        body_style
    ))

    slo_table_data = [
        [Paragraph("<b>ID Alerta</b>", body_bold), Paragraph("<b>Objetivo de Servicio (SLO)</b>", body_bold), Paragraph("<b>P1 (Crítico)</b>", body_bold), Paragraph("<b>P2 (Alto)</b>", body_bold), Paragraph("<b>P3 (Advertencia)</b>", body_bold), Paragraph("<b>Acción Requerida</b>", body_bold)],
        [Paragraph("<b>ALT-001</b>", body_style), Paragraph("Latencia p95 &lt; 50 ms en ventanas de 5 min.", body_style), Paragraph("&gt;= 100 ms", body_style), Paragraph("&gt;= 70 ms", body_style), Paragraph("&gt; 50 ms", body_style), Paragraph("Ejecución Runbook RB-01 (Autoescalado HPA). PagerDuty.", body_style)],
        [Paragraph("<b>ALT-002</b>", body_style), Paragraph("Disponibilidad Uptime &gt;= 99.9% mensual.", body_style), Paragraph("&lt; 98.0%", body_style), Paragraph("&lt; 99.5%", body_style), Paragraph("&lt; 99.85%", body_style), Paragraph("Activación de Circuit Breaker. Revisión SRE inmediata.", body_style)],
        [Paragraph("<b>ALT-003</b>", body_style), Paragraph("Calidad ML F1-Score &gt;= 0.82 continuo.", body_style), Paragraph("&lt; 0.70", body_style), Paragraph("&lt; 0.80", body_style), Paragraph("&lt; 0.82", body_style), Paragraph("Activación Runbook RB-02 (Fallback + Reentrenamiento).", body_style)],
        [Paragraph("<b>ALT-004</b>", body_style), Paragraph("Deriva de Datos (PSI) &lt; 0.10 estable.", body_style), Paragraph("&gt;= 0.25", body_style), Paragraph("&gt;= 0.18", body_style), Paragraph("&gt;= 0.10", body_style), Paragraph("Notificación Slack #ops-mlops. Auditoría de vocabulario.", body_style)]
    ]
    t_slo = Table(slo_table_data, colWidths=[0.8*inch, 2.1*inch, 1.0*inch, 1.0*inch, 1.0*inch, 1.3*inch])
    t_slo.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), COLOR_CARD_BG),
        ("GRID", (0, 0), (-1, -1), 0.5, COLOR_BORDER),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 3.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
    ]))
    story.append(t_slo)

    story.append(Spacer(1, 6))
    story.append(Paragraph("B. Monitoreo de Tasa de Quemado (Error Budget Burn Rate) y Reducción de Fatiga", h3_style))
    story.append(Paragraph(
        "El sistema calcula el <i>Burn Rate</i> (tasa de consumo) del presupuesto de error utilizando ventanas múltiples: "
        "un quemado de <b>14.4x en 1 hora</b> consume el 2% del presupuesto mensual, disparando inmediatamente una alerta <b>P1</b> "
        "con notificación por PagerDuty al ingeniero de guardia. Para eliminar ruidos y falsas alarmas, se aplican tres mecanismos clave:<br/>"
        "• <b>Persistencia Temporal (Debouncing):</b> La violación debe persistir por al menos 2 periodos de evaluación consecutivos antes de despachar una alerta.<br/>"
        "• <b>Bandas Muertas e Histéresis:</b> Una alerta de latencia activada en 70 ms no se desactiva hasta que la latencia desciende por debajo de 40 ms, previniendo oscilaciones rápidas.<br/>"
        "• <b>Deduplicación y Agrupación:</b> Cuando ocurre una saturación de CPU, los errores 5xx derivados se agrupan en un único incidente para evitar ráfagas de notificaciones.",
        body_style
    ))

    story.append(Spacer(1, 8))
    story.append(Paragraph("4. Estrategias de Detección de Data Drift y Concept Drift", h2_style))
    story.append(Paragraph(
        "El fenómeno de deriva ocurre cuando las propiedades estadísticas del entorno de producción divergen de las condiciones "
        "con las que se entrenó el modelo. En MexBan se diferencian dos tipos de deriva con impacto operacional:<br/>"
        "• <b>Data Drift (Deriva de Datos - P(X)):</b> Cambio en la distribución de las características de entrada (ej. vocabulario criptográfico no anticipado).<br/>"
        "• <b>Concept Drift (Deriva de Concepto - P(Y|X)):</b> Cambio en la relación entre entradas y etiquetas esperadas.<br/><br/>"
        "<b>Métodos Estadísticos:</b> Se implementa el <b>Population Stability Index (PSI)</b>: "
        "<code>PSI = &Sigma; [(%Actual_i - %Esperado_i) &times; ln(%Actual_i / %Esperado_i)]</code>, donde PSI &lt; 0.10 indica estabilidad, "
        "0.10 a 0.20 deriva moderada y &ge; 0.20 deriva crítica. Adicionalmente se aplican la prueba <b>Kolmogorov-Smirnov (KS-test)</b> "
        "y la <b>Distancia de Wasserstein</b> sobre longitudes y probabilidades softmax, así como el seguimiento de la tasa <b>Out-Of-Vocabulary (OOV)</b>.",
        body_style
    ))

    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 5: DASHBOARDS OPERATIVOS EN TIEMPO REAL
    # =========================================================================
    story.append(Paragraph("5. Descripción de Dashboards Operativos en Tiempo Real", h2_style))
    story.append(Paragraph(
        "Para garantizar una toma de decisiones oportuna y democratizada entre los diferentes interesados del banco, "
        "se implementó una estructura de visualización modular en tiempo real dividida en tres niveles de gobierno:",
        body_style
    ))

    story.append(Paragraph(
        "• <b>Nivel 1: Panel Ejecutivo y Negocio (Product Owner / C-Suite):</b> Muestra el cumplimiento global de los SLOs, el estado "
        "remanente del Error Budget mensual, el volumen consolidado de opiniones procesadas y el índice neto de sentimiento bancario.<br/>"
        "• <b>Nivel 2: Panel SRE y Operaciones de Infraestructura:</b> Supervisa en tiempo real los cuatro Golden Signals (latencia percentil "
        "p50/p95/p99, throughput de peticiones por segundo, códigos de error HTTP 5xx y uso de CPU/RAM de los pods).<br/>"
        "• <b>Nivel 3: Panel MLOps y Científicos de Datos:</b> Presenta el comportamiento técnico del modelo DistilBERT, incluyendo la curva de "
        "F1-Score continuo, matriz de confusión dinámica, valores de PSI por variable y tasa de confianza promedio.",
        body_style
    ))

    if os.path.exists("dashboards/img1_realtime_operational_dashboard.png"):
        story.append(Image("dashboards/img1_realtime_operational_dashboard.png", width=7.2*inch, height=4.2*inch))
        story.append(Paragraph("Img2. Dashboard Operativo en Tiempo Real con los 4 Paneles de Monitoreo (Golden Signals, Presupuesto de Error, Calidad ML y Data Drift).", caption_style))

    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 6: RUNBOOKS DE RESPUESTA A INCIDENTES
    # =========================================================================
    story.append(Paragraph("6. Runbooks de Respuesta a Incidentes (Procedimientos Operativos)", h2_style))
    story.append(Paragraph(
        "Los runbooks son manuales de procedimientos estandarizados que guían al personal on-call (o a los sistemas automáticos) "
        "para diagnosticar, mitigar y resolver incidentes en el menor tiempo posible (MTTR objetivo &lt; 15 minutos).",
        body_style
    ))

    # Runbook RB-01
    rb01_data = [
        [Paragraph("<b>RUNBOOK RB-01: Saturación de Latencia y Capacidad de Cómputo</b>", body_bold), Paragraph("<b>Severidad: P1 (Crítico)</b>", body_bold)],
        [Paragraph("<b>Condición de Activación:</b>", body_bold), Paragraph("Alerta ALT-001 (Latencia p95 &gt;= 100 ms por 2 ciclos consecutivos o saturación de CPU &gt; 85%).", body_style)],
        [Paragraph("<b>Impacto Operacional:</b>", body_bold), Paragraph("Riesgo de timeouts en la app de Banca Móvil y bloqueo en la clasificación de comentarios de usuarios.", body_style)],
        [Paragraph("<b>Paso 1: Diagnóstico:</b>", body_bold), Paragraph("Inspeccionar pods con <code>kubectl top pods -l app=mexban-sentiment</code> y revisar cola de peticiones en Kong.", body_style)],
        [Paragraph("<b>Paso 2: Auto-escalado:</b>", body_bold), Paragraph("Disparar escalamiento horizontal elástico (HPA) incrementando de 2 a 6 réplicas del microservicio.", body_style)],
        [Paragraph("<b>Paso 3: Caché Semántica:</b>", body_bold), Paragraph("Habilitar caché Redis en memoria para respuestas de textos repetidos o idénticos.", body_style)],
        [Paragraph("<b>Paso 4: Verificación:</b>", body_bold), Paragraph("Monitorear en Prometheus que la latencia p95 descienda por debajo del límite de histéresis (&lt; 40 ms).", body_style)],
        [Paragraph("<b>Criterio de Cierre:</b>", body_bold), Paragraph("Latencia estabilizada en ~16 ms durante 15 minutos sin errores 5xx. Documentar post-mortem.", body_style)]
    ]
    t_rb01 = Table(rb01_data, colWidths=[2.2*inch, 5.0*inch])
    t_rb01.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#FCE4EC")),
        ("GRID", (0, 0), (-1, -1), 0.5, COLOR_BORDER),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(t_rb01)

    story.append(Spacer(1, 8))

    # Runbook RB-02
    rb02_data = [
        [Paragraph("<b>RUNBOOK RB-02: Data Drift Crítico y Degradación de Calidad ML</b>", body_bold), Paragraph("<b>Severidad: P2 (Alto) / P1</b>", body_bold)],
        [Paragraph("<b>Condición de Activación:</b>", body_bold), Paragraph("Alerta ALT-004 (PSI &gt;= 0.20) en combinación con ALT-003 (F1-Score &lt; 0.80 en validación continua).", body_style)],
        [Paragraph("<b>Impacto Operacional:</b>", body_bold), Paragraph("El modelo clasifica erróneamente quejas graves como neutras/positivas debido a vocabulario no entrenado.", body_style)],
        [Paragraph("<b>Paso 1: Fallback Seguro:</b>", body_bold), Paragraph("Activar desvío por Circuit Breaker a clasificador heurístico de léxico financiero seguro para quejas.", body_style)],
        [Paragraph("<b>Paso 2: Extracción ETL:</b>", body_bold), Paragraph("Extraer últimos 7 días de feedback bancario anonimizado e incorporar al almacén de reentrenamiento DVC/S3.", body_style)],
        [Paragraph("<b>Paso 3: Retraining MLflow:</b>", body_bold), Paragraph("Ejecutar pipeline automatizado en MLflow. Registrar nuevo modelo candidato <b>DistilBERT-MexBan-v2</b>.", body_style)],
        [Paragraph("<b>Paso 4: Validación Calidad:</b>", body_bold), Paragraph("Correr suite de pruebas de regresión. Exigir F1-Score &gt;= 0.88 sobre el conjunto enriquecido.", body_style)],
        [Paragraph("<b>Paso 5: Despliegue Canary:</b>", body_bold), Paragraph("Despliegue progresivo vía Flagger (10% &rarr; 50% &rarr; 100%). Desactivar fallback una vez verificado.", body_style)],
        [Paragraph("<b>Criterio de Cierre:</b>", body_bold), Paragraph("PSI &lt; 0.08 y F1-Score &gt; 0.90 en producción sostenido por 1 hora.", body_style)]
    ]
    t_rb02 = Table(rb02_data, colWidths=[2.2*inch, 5.0*inch])
    t_rb02.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E0F2F1")),
        ("GRID", (0, 0), (-1, -1), 0.5, COLOR_BORDER),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(t_rb02)

    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 7: SIMULACIÓN DE INCIDENTES Y RESULTADOS OBTENIDOS
    # =========================================================================
    story.append(Paragraph("7. Simulación de Incidentes Críticos y Resultados Obtenidos", h2_style))
    story.append(Paragraph(
        "Se ejecutó una simulación controlada y reproducible de dos incidentes operacionales severos para verificar la eficacia "
        "del sistema de observabilidad y la capacidad de recuperación ante fallas.",
        body_style
    ))

    story.append(Paragraph("A. Incidente 1: Pico Anómalo de Tráfico y Saturación de Latencia", h3_style))
    story.append(Paragraph(
        "<b>Escenario:</b> Durante una campaña de nómina en Banca Móvil, la concurrencia saltó a más de 350 RPS, saturando la CPU al 94% "
        "y elevando la <b>latencia p95 a 178.0 ms</b> (violando el SLO de 50 ms). Tras 2 periodos consecutivos se despachó la alerta crítica <b>ALT-001 (P1)</b>. "
        "El sistema automatizado ejecutó el <b>Runbook RB-01</b>, escalando el clúster a 6 réplicas y activando la caché Redis en memoria. "
        "La latencia p95 se normalizó a <b>16.4 ms</b> y la CPU bajó a 38.0% en <b>4.2 minutos (MTTR)</b>.",
        body_style
    ))

    if os.path.exists("dashboards/img2_incident1_latency_mitigation.png"):
        story.append(Image("dashboards/img2_incident1_latency_mitigation.png", width=7.2*inch, height=2.4*inch))
        story.append(Paragraph("Img3. Curvas de Mitigación del Incidente 1: Normalización de Latencia p95 y Auto-escalado de Pods vs CPU.", caption_style))

    story.append(Spacer(1, 4))
    story.append(Paragraph("B. Incidente 2: Data Drift Crítico por Lanzamiento de Cripto-Billetera MexBan", h3_style))
    story.append(Paragraph(
        "<b>Escenario:</b> Tras lanzar la función 'Cripto-Billetera', la afluencia de nuevo léxico bancario causó una tasa OOV de 28.5% "
        "y un <b>PSI de 0.284</b>, desplomando el <b>F1-Score a 0.69</b>. Se activó el <b>Runbook RB-02</b>: habilitación de fallback seguro, "
        "extracción de 15,400 registros y reentrenamiento automatizado en MLflow. El modelo <b>DistilBERT-MexBan-v2</b> alcanzó un <b>F1-Score de 0.912</b> "
        "y redujo el PSI a <b>0.052 (Estable)</b> tras su despliegue Canary progresivo. MTTR: 9.5 minutos.",
        body_style
    ))

    if os.path.exists("dashboards/img3_incident2_datadrift_retraining.png"):
        story.append(Image("dashboards/img3_incident2_datadrift_retraining.png", width=7.2*inch, height=2.4*inch))
        story.append(Paragraph("Img4. Evolución de Calidad F1 y Detección de Data Drift (PSI) durante el Incidente 2 y Recuperación con v2.0.", caption_style))

    story.append(Spacer(1, 4))

    # Tabla Resumen de Métricas de Incidentes
    incidents_table_data = [
        [Paragraph("<b>Incidente Simulado</b>", body_bold), Paragraph("<b>Métrica Afectada</b>", body_bold), Paragraph("<b>Valor en Crisis</b>", body_bold), Paragraph("<b>Valor Restaurado</b>", body_bold), Paragraph("<b>MTTR</b>", body_bold), Paragraph("<b>Estatus Final</b>", body_bold)],
        [Paragraph("<b>Incidente 1:</b> Saturación de Latencia", body_style), Paragraph("Latencia p95 de Inferencia", body_style), Paragraph("<font color='#C0392B'><b>178.0 ms</b></font>", body_style), Paragraph("<font color='#00A896'><b>16.4 ms</b></font>", body_style), Paragraph("4.2 min", body_style), Paragraph("<b>RESUELTO</b> (RB-01)", body_style)],
        [Paragraph("<b>Incidente 2:</b> Data Drift Cripto", body_style), Paragraph("F1-Score / Índice PSI", body_style), Paragraph("<font color='#C0392B'><b>F1: 0.69 | PSI: 0.28</b></font>", body_style), Paragraph("<font color='#00A896'><b>F1: 0.912 | PSI: 0.05</b></font>", body_style), Paragraph("9.5 min", body_style), Paragraph("<b>RESUELTO</b> (RB-02)", body_style)]
    ]
    t_inc = Table(incidents_table_data, colWidths=[1.8*inch, 1.8*inch, 1.3*inch, 1.3*inch, 0.8*inch, 1.0*inch])
    t_inc.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), COLOR_CARD_BG),
        ("GRID", (0, 0), (-1, -1), 0.5, COLOR_BORDER),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(t_inc)

    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 8: EVIDENCIA EN MLFLOW, ANEXOS Y GITHUB
    # =========================================================================
    story.append(Paragraph("8. Evidencia de Implementación y Gobernanza con MLflow", h2_style))
    story.append(Paragraph(
        "Se configuró un servidor de tracking local de <b>MLflow</b> respaldado por una base de datos relacional SQLite "
        "(<code>mlflow_tracking.db</code>). Durante la ejecución se registraron los parámetros de servicio, las corridas anidadas "
        "de monitoreo continuo y el ciclo de vida de los modelos en el <b>MLflow Model Registry</b>.",
        body_style
    ))

    if os.path.exists("dashboards/img5_mlflow_tracking_ui_mockup.png"):
        story.append(Image("dashboards/img5_mlflow_tracking_ui_mockup.png", width=7.2*inch, height=2.45*inch))
        story.append(Paragraph("Img5. Evidencia de Seguimiento en MLflow: Model Registry (Promoción de v2.0 a Producción) y Registro de Métricas.", caption_style))

    story.append(Paragraph(
        "Como se aprecia en la evidencia de MLflow, la versión original <code>v1.0.0</code> fue transicionada a estado <i>Archived</i> "
        "tras confirmarse su vulnerabilidad al drift de datos, mientras que la nueva versión reentrenada <code>v2.0.0</code> fue formalmente "
        "promovida a la etapa <i>Production</i> tras satisfacer el criterio de aceptación del Runbook RB-02 (F1 &ge; 0.88).",
        body_style
    ))

    story.append(Spacer(1, 6))
    story.append(Paragraph("Anexos", h1_style))
    story.append(Paragraph("Estructura de Scripts y Repositorio de Código", h2_style))
    story.append(Paragraph(
        "Todo el código fuente desarrollado para esta actividad, incluyendo los módulos de telemetría, el motor de alertas, "
        "el detector estadístico de drift, los scripts de simulación automatizada, el notebook interactivo y los dashboards generados, "
        "se encuentran organizados bajo estándares profesionales de ingeniería de software en el siguiente repositorio público de GitHub:",
        body_style
    ))

    github_link = "https://github.com/JuanMCarreonCh/actividad8_gestion_proyectos_ia"
    story.append(Paragraph(f"<b>Enlace al Repositorio de GitHub:</b> <font color='#0F3B7A'><u>{github_link}</u></font>", body_bold))

    story.append(Spacer(1, 4))

    files_table_data = [
        [Paragraph("<b>Directorio / Archivo</b>", body_bold), Paragraph("<b>Descripción y Rol en el Sistema</b>", body_bold)],
        [Paragraph("<code>src/metrics_logger.py</code>", body_style), Paragraph("Módulo de observabilidad: logs JSON estructurados, trazas de spans y métricas Golden Signals.", body_style)],
        [Paragraph("<code>src/drift_detector.py</code>", body_style), Paragraph("Motor de cálculo estadístico de PSI, prueba Kolmogorov-Smirnov, distancia Wasserstein y OOV.", body_style)],
        [Paragraph("<code>src/alert_engine.py</code>", body_style), Paragraph("Motor de alertas inteligentes SLO, Error Budget Burn Rate y reducción de fatiga con histéresis.", body_style)],
        [Paragraph("<code>src/runbook_automation.py</code>", body_style), Paragraph("Automatización de Runbooks RB-01 (Autoescalado HPA) y RB-02 (Fallback, Reentrenamiento MLflow).", body_style)],
        [Paragraph("<code>src/observability_service.py</code>", body_style), Paragraph("Servicio integral que orquesta la simulación de tráfico bancario y los componentes de observabilidad.", body_style)],
        [Paragraph("<code>scripts/run_full_simulation.py</code>", body_style), Paragraph("Script maestro ejecutor de la simulación de 26 ciclos con logging continuo en MLflow.", body_style)],
        [Paragraph("<code>scripts/generate_visuals.py</code>", body_style), Paragraph("Generador de dashboards y gráficos de alta resolución para reportes y visualizaciones.", body_style)],
        [Paragraph("<code>notebooks/Actividad8_Monitoreo_Observabilidad.ipynb</code>", body_style), Paragraph("Notebook interactivo ejecutable con documentación celda por celda y salidas gráficas.", body_style)]
    ]
    t_files = Table(files_table_data, colWidths=[2.5*inch, 4.7*inch])
    t_files.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), COLOR_CARD_BG),
        ("GRID", (0, 0), (-1, -1), 0.5, COLOR_BORDER),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 2.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
    ]))
    story.append(t_files)

    # Construir documento de contenido
    doc = SimpleDocTemplate(
        body_pdf_path,
        pagesize=A4,
        leftMargin=40,
        rightMargin=40,
        topMargin=50,
        bottomMargin=45
    )
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[PDF] Contenido generado en: {body_pdf_path}")

    cover_reader = pypdf.PdfReader(cover_pdf_path)
    body_reader = pypdf.PdfReader(body_pdf_path)
    final_writer = pypdf.PdfWriter()

    final_writer.add_page(cover_reader.pages[0])
    for page in body_reader.pages:
        final_writer.add_page(page)

    with open(final_pdf_path, "wb") as f:
        final_writer.write(f)

    print(f"\n================================================================================")
    print(f"  DOCUMENTO TÉCNICO OFICIAL GENERADO CON ÉXITO: {final_pdf_path}")
    print(f"  Total de páginas: {len(final_writer.pages)}")
    print(f"================================================================================")

if __name__ == "__main__":
    build_pdf_document()
