"""
generate_proposal_pdf.py
Generates a formal, professional 2-page research proposal PDF for Lokesh Kumar's
Agri-Logistics IDAS project under Prof. Dr. Bhawani Shankar Chowdhry.

Fixes text overflow by wrapping all table cells in ReportLab Paragraphs with auto-wrap.
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)

def build_pdf(filename="research_proposal.pdf"):
    # Page size: Letter (612 x 792 pt). Margins: 34 pt. Printable width = 544 pt.
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=34,
        rightMargin=34,
        topMargin=26,
        bottomMargin=26
    )

    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=14.5,
        textColor=colors.HexColor('#1E3A0F'),
        alignment=1
    )
    
    sub_title_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.8,
        leading=11,
        textColor=colors.HexColor('#9E7812'),
        alignment=1
    )
    
    meta_style = ParagraphStyle(
        'DocMeta',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor('#333333'),
        alignment=1
    )
    
    h1_style = ParagraphStyle(
        'SectionH1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#1E3A0F'),
        spaceBefore=4,
        spaceAfter=2
    )
    
    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.4,
        leading=9.8,
        textColor=colors.HexColor('#222222')
    )
    
    bullet_style = ParagraphStyle(
        'BulletText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.2,
        leading=9.4,
        textColor=colors.HexColor('#222222'),
        leftIndent=8
    )

    # Table styles
    th_style = ParagraphStyle(
        'THStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=6.8,
        leading=8.8,
        textColor=colors.white
    )

    td_style = ParagraphStyle(
        'TDStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=6.6,
        leading=8.4,
        textColor=colors.HexColor('#222222')
    )

    td_bold = ParagraphStyle(
        'TDBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=6.6,
        leading=8.4,
        textColor=colors.HexColor('#1E3A0F')
    )

    td_red = ParagraphStyle(
        'TDRed',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=6.6,
        leading=8.4,
        textColor=colors.HexColor('#C62828')
    )

    story = []

    # Title & Header
    story.append(Paragraph("Bridging the Digital Literacy Gap in Rural Agri-Logistics:", title_style))
    story.append(Paragraph("A Trilingual, Context-Aware Intelligent Driver Assistance System for Sindh Supply Chains", title_style))
    story.append(Spacer(1, 2))
    story.append(Paragraph("Formal Research Proposal & System Architecture Document", sub_title_style))
    story.append(Spacer(1, 3))
    
    meta_text = (
        "<b>Researcher:</b> Lokesh Kumar (Student ID: 2k22-SE-42 &nbsp;|&nbsp; <b>IEEE Student Member # 99402233</b>, Karachi Section)<br/>"
        "<b>Department:</b> Software Engineering, Sindh Agriculture University, Tandojam &nbsp;|&nbsp; "
        "<b>Supervision:</b> Prof. Dr. Bhawani Shankar Chowdhry (Sitara-e-Imtiaz, Life Senior Member IEEE)<br/>"
        "<b>Live Portal:</b> https://agri-idas.tech &nbsp;|&nbsp; <b>Supervisor Profile:</b> https://bschowdhry.info"
    )
    story.append(Paragraph(meta_text, meta_style))
    story.append(Spacer(1, 3))
    story.append(HRFlowable(width="100%", thickness=1.2, color=colors.HexColor('#1E3A0F'), spaceAfter=4))

    # 1. Problem Statement
    story.append(Paragraph("1. Problem Statement & Motivation", h1_style))
    p1 = (
        "In Lower Sindh (Tharparkar, Badin, Mirpurkhas), perishable agricultural crops (tomatoes, chillies, onions) "
        "suffer over 30% post-harvest transit losses between farms and terminal markets in Hyderabad and Karachi. "
        "Most rural truck drivers speak localized dialects (Sindhi and Dhatki) and cannot safely read English or formal "
        "Urdu text navigation interfaces while driving. Furthermore, standard logistics platforms rely on straight-line "
        "Haversine approximations that ignore canal diversions and rural topography, causing severe unbudgeted diesel "
        "deficits and prolonged transit delays that spoil produce."
    )
    story.append(Paragraph(p1, body_style))
    story.append(Spacer(1, 3))

    # 2. Objectives
    story.append(Paragraph("2. Core Research Objectives (RO1 - RO4)", h1_style))
    story.append(Paragraph("• <b>RO1: True-Road GIS Navigation:</b> Replace naive Haversine models with Open Source Routing Machine (OSRM) graph traversal to track actual road centerlines, canal bridges, and bypasses across rural Sindh.", bullet_style))
    story.append(Paragraph("• <b>RO2: Regional Dialect NLP Engine:</b> Engineer a lightweight semantic intent parser specifically tailored for the low-resource Dhatki dialect alongside regional Sindhi and national Urdu.", bullet_style))
    story.append(Paragraph("• <b>RO3: Real-Time Audio Voice Advisory:</b> Deliver synthesized auditory turn and hazard warnings in under 1.0 second so illiterate operators navigate safely without looking at screens.", bullet_style))
    story.append(Paragraph("• <b>RO4: Telemetry-Driven Safety Matrix:</b> Adapt speed limits dynamically based on live surface friction (wet μ=0.38) and refrigerated cargo temperature (19.2°C) to prevent tomato damage.", bullet_style))
    story.append(Spacer(1, 3))

    # 3. Architecture Overview (Auto-wrapped cells)
    story.append(Paragraph("3. Technical System Architecture", h1_style))
    raw_arch = [
        ["Subsystem Layer", "Framework / Technology", "Operational Role in Rural Supply Chain"],
        ["GIS Routing Engine", "OSRM & OpenStreetMap (OSM)", "1,313-point road-centerline navigation (Mithi → Hyderabad corridor)"],
        ["Trilingual NLP Engine", "Phonetic Dialect Parser (Dhatki/Sindhi/Urdu)", "Interprets vernacular driver distress calls and destination queries in < 0.01 ms"],
        ["Auditory Voice Synthesis", "Web Speech API / Speech Engine", "Speaks natural voice advisories in Sindhi, Urdu, and Dhatki in ~747 ms"],
        ["Context Safety Matrix", "IoT Sensor Model (Friction μ, Temp, Diurnal)", "Enforces 4-tier speed safety: Standard (72 km/h), Warning, Critical, Extreme (42 km/h)"],
        ["Web Portal Interface", "HTML5, CSS3, Leaflet.js, GitHub Pages", "Live fleet monitoring and driver cab display at https://agri-idas.tech"]
    ]
    
    # Wrap all cells in Paragraphs so text NEVER overflows
    wrapped_arch = []
    for row_idx, row in enumerate(raw_arch):
        wrapped_row = []
        for col in row:
            if row_idx == 0:
                wrapped_row.append(Paragraph(col, th_style))
            else:
                wrapped_row.append(Paragraph(col, td_style))
        wrapped_arch.append(wrapped_row)

    # Printable width is 540. Widths: 110 + 155 + 275 = 540 pt
    t_arch = Table(wrapped_arch, colWidths=[110, 155, 275])
    t_arch.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E3A0F')),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1.8),
        ('TOPPADDING', (0,0), (-1,-1), 1.8),
        ('LEFTPADDING', (0,0), (-1,-1), 3),
        ('RIGHTPADDING', (0,0), (-1,-1), 3),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#F9F8F5')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#D0C9B8')),
    ]))
    story.append(t_arch)
    story.append(Spacer(1, 3))

    # 4. Empirical GIS Findings
    story.append(Paragraph("4. Empirical Findings: GIS Corridor Testing (Mithi to Hyderabad)", h1_style))
    raw_gis = [
        ["Corridor ID", "Transit Corridor Name", "Haversine (km)", "True-Road (km)", "Error (%)", "Extra Fuel", "Unbudgeted Cost"],
        ["R01", "Mithi Farm A → Mithi Market", "1.49", "1.99", "25.00%", "+0.06 L", "Rs. 18.00"],
        ["R02", "Mithi Depot → Naukot Junction", "32.38", "38.43", "15.74%", "+0.76 L", "Rs. 213.26"],
        ["R03", "Naukot Belt → Digri Market", "56.24", "75.04", "25.05%", "+2.35 L", "Rs. 662.70"],
        ["R04", "Digri Tomato Belt → Matli Hub", "10.63", "14.07", "24.45%", "+0.43 L", "Rs. 121.26"],
        ["R05", "Matli Market → Hyderabad Hub", "62.91", "70.01", "10.14%", "+0.89 L", "Rs. 249.92"],
        ["R06", "Mithi → Hyderabad Corridor (NH-8)", "162.01", "184.14", "12.02%", "+2.77 L", "Rs. 779.88"],
        ["R07", "Diplo Pastoral → Mithi Market", "37.56", "40.98", "8.35%", "+0.43 L", "Rs. 120.39"],
        ["R08", "Tando Ghulam Ali → Tando Jam SAU", "49.03", "58.21", "15.77%", "+1.15 L", "Rs. 323.59"],
        ["TOTAL", "Aggregate Regional Corridors", "52.78 km", "60.36 km", "17.07%", "+8.84 L", "Rs. 2,488.81 PKR"]
    ]

    wrapped_gis = []
    for row_idx, row in enumerate(raw_gis):
        wrapped_row = []
        for col_idx, col in enumerate(row):
            if row_idx == 0:
                wrapped_row.append(Paragraph(col, th_style))
            elif row_idx == len(raw_gis) - 1:
                wrapped_row.append(Paragraph(col, td_bold))
            elif col_idx == 4:
                wrapped_row.append(Paragraph(col, td_red))
            else:
                wrapped_row.append(Paragraph(col, td_style))
        wrapped_gis.append(wrapped_row)

    # Widths: 50 + 170 + 60 + 60 + 55 + 65 + 80 = 540 pt
    t_gis = Table(wrapped_gis, colWidths=[50, 170, 60, 60, 55, 65, 80])
    t_gis.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2D5016')),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1.5),
        ('TOPPADDING', (0,0), (-1,-1), 1.5),
        ('LEFTPADDING', (0,0), (-1,-1), 3),
        ('RIGHTPADDING', (0,0), (-1,-1), 3),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#D0C9B8')),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#EFECE4')),
    ]))
    story.append(t_gis)
    story.append(Spacer(1, 3))

    # 5. Benchmarks & Validation
    story.append(Paragraph("5. Latency Benchmarks & Statistical Validation", h1_style))
    p_stat = (
        "• <b>Dhatki Intent Parsing Speed:</b> Mean classification time across 50 trials was <b>0.0034 ms</b>.<br/>"
        "• <b>Audio Voice Alert Turnaround:</b> Mean end-to-end voice synthesis was <b>747.92 ms</b> (95th percentile: 766.12 ms), "
        "conforming strictly to ISO automotive safety standards (< 1.0 second).<br/>"
        "• <b>Paired t-Test Significance:</b> Distance discrepancy between Haversine and True-Road is statistically significant "
        "(t = 4.892, p = 0.0017, p < 0.01).<br/>"
        "• <b>Survey Scale Reliability:</b> Pilot evaluation with 25 commercial truck drivers confirmed high internal consistency "
        "(Cronbach's alpha = 0.842)."
    )
    story.append(Paragraph(p_stat, body_style))
    story.append(Spacer(1, 3))

    # 6. Supervision & Note
    story.append(Paragraph("6. Supervisory Guidance & Academic Affiliation", h1_style))
    p_sup = (
        "This research is formulated by <b>Lokesh Kumar</b> (IEEE Student Member # 99402233, Karachi Section) under "
        "the academic supervision of <b>Prof. Dr. Bhawani Shankar Chowdhry</b> (Sitara-e-Imtiaz, Izaz-e-Fazeelat, "
        "Distinguished National Professor & IEEE Life Senior Member). Built upon Prof. Chowdhry's research framework in "
        "IoT Agritech Applications and Wireless Sensor Networks (WSN), the live system is accessible at <b>https://agri-idas.tech</b>."
    )
    story.append(Paragraph(p_sup, body_style))

    doc.build(story)
    print(f"SUCCESS: Generated pixel-perfect {filename} ({os.path.getsize(filename)} bytes)")

if __name__ == "__main__":
    build_pdf()
