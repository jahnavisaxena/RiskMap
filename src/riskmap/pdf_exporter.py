from typing import List
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.platypus.flowables import HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime
from .risk_manager import Risk


def _get_severity_level(score: int) -> str:
    """Map risk score to severity level."""
    if score >= 20:
        return "Critical"
    elif score >= 15:
        return "High"
    elif score >= 10:
        return "Medium"
    else:
        return "Low"


def _get_severity_color(severity: str) -> colors.Color:
    """Get color based on severity level."""
    color_map = {
        "Critical": colors.red,
        "High": colors.orange,
        "Medium": colors.yellow,
        "Low": colors.lightgreen
    }
    return color_map.get(severity, colors.white)


def export_to_pdf(risks: List[Risk], filepath: str):
    """
    Export risk register to a professional PDF report.
    
    Args:
        risks: List of Risk objects to export
        filepath: Output PDF file path
    """
    if not risks:
        return
    
    # Create PDF document
    doc = SimpleDocTemplate(
        filepath,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=18,
    )
    
    # Container for PDF elements
    elements = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#333333'),
        spaceAfter=12,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#444444'),
        spaceAfter=6
    )
    
    # === COVER PAGE ===
    elements.append(Spacer(1, 1.5 * inch))
    elements.append(Paragraph("Risk Register Report", title_style))
    elements.append(Spacer(1, 0.3 * inch))
    elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#0066CC')))
    elements.append(Spacer(1, 0.5 * inch))
    
    # Summary statistics
    total_risks = len(risks)
    severity_counts = {
        "Critical": 0,
        "High": 0,
        "Medium": 0,
        "Low": 0
    }
    
    for risk in risks:
        severity = _get_severity_level(risk.score)
        severity_counts[severity] += 1
    
    # Summary table
    summary_data = [
        ["Total Risks", str(total_risks)],
        ["Critical", str(severity_counts["Critical"])],
        ["High", str(severity_counts["High"])],
        ["Medium", str(severity_counts["Medium"])],
        ["Low", str(severity_counts["Low"])],
        ["Generated", datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
    ]
    
    summary_table = Table(summary_data, colWidths=[3 * inch, 2 * inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E8E8E8')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ]))
    
    elements.append(Paragraph("Executive Summary", heading_style))
    elements.append(summary_table)
    elements.append(PageBreak())
    
    # === DETAILED RISK REGISTER ===
    elements.append(Paragraph("Detailed Risk Register", heading_style))
    elements.append(Spacer(1, 0.2 * inch))
    
    # Create risk table
    table_data = [[
        "ID",
        "Risk Name",
        "Likelihood",
        "Impact",
        "Score",
        "Severity",
        "Controls"
    ]]
    
    for risk in risks:
        severity = _get_severity_level(risk.score)
        controls_text = ", ".join(risk.controls) if risk.controls else "None"
        
        # Wrap long text
        if len(controls_text) > 40:
            controls_text = controls_text[:37] + "..."
        
        table_data.append([
            str(risk.id),
            risk.name[:30] if len(risk.name) > 30 else risk.name,
            str(risk.likelihood),
            str(risk.impact),
            str(risk.score),
            severity,
            controls_text
        ])
    
    # Create table with custom styling
    risk_table = Table(table_data, colWidths=[
        0.4 * inch,  # ID
        2.2 * inch,  # Name
        0.7 * inch,  # Likelihood
        0.6 * inch,  # Impact
        0.6 * inch,  # Score
        0.8 * inch,  # Severity
        2.2 * inch   # Controls
    ])
    
    # Apply table styling
    table_style = [
        # Header row
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0066CC')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, 0), 12),
        
        # Data rows
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # ID column
        ('ALIGN', (2, 1), (4, -1), 'CENTER'),  # Numeric columns
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        
        # Grid
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        
        # Alternating row colors
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')]),
    ]
    
    # Add color coding for severity column
    for i, risk in enumerate(risks, start=1):
        severity = _get_severity_level(risk.score)
        severity_color = _get_severity_color(severity)
        table_style.append(('BACKGROUND', (5, i), (5, i), severity_color))
        table_style.append(('TEXTCOLOR', (5, i), (5, i), colors.black))
    
    risk_table.setStyle(TableStyle(table_style))
    elements.append(risk_table)
    
    # Add detailed risk descriptions if available
    elements.append(Spacer(1, 0.3 * inch))
    elements.append(Paragraph("Risk Details", heading_style))
    
    for risk in risks:
        if risk.description:
            elements.append(Spacer(1, 0.1 * inch))
            risk_detail = f"<b>Risk {risk.id}: {risk.name}</b><br/>{risk.description}"
            elements.append(Paragraph(risk_detail, normal_style))
    
    # Build PDF
    doc.build(elements)
