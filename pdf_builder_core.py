import os
import sys
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY

OUTPUT_DIR_ATHARVA = os.path.abspath(r"e:\vyaparai\dossiers\atharva")
OUTPUT_DIR_VENKATESH = os.path.abspath(r"e:\vyaparai\dossiers\venkatesh")
os.makedirs(OUTPUT_DIR_ATHARVA, exist_ok=True)
os.makedirs(OUTPUT_DIR_VENKATESH, exist_ok=True)

PDF_ATHARVA = os.path.join(OUTPUT_DIR_ATHARVA, "Atharva_Awate_VyaparAI_Talking_Points.pdf")
MD_ATHARVA = os.path.join(OUTPUT_DIR_ATHARVA, "Atharva_Awate_VyaparAI_Talking_Points.md")
PDF_VENKATESH = os.path.join(OUTPUT_DIR_VENKATESH, "Venkatesh_Pai_VyaparAI_Talking_Points.pdf")
MD_VENKATESH = os.path.join(OUTPUT_DIR_VENKATESH, "Venkatesh_Pai_VyaparAI_Talking_Points.md")

def get_custom_styles():
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=18,
        textColor=colors.HexColor('#0F172A'),
        alignment=TA_CENTER,
        spaceAfter=2
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=12,
        textColor=colors.HexColor('#0F766E'),
        alignment=TA_CENTER,
        spaceAfter=3
    )

    badge_style = ParagraphStyle(
        'BadgeBar',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor('#475569'),
        alignment=TA_CENTER,
        spaceAfter=5
    )

    section_header = ParagraphStyle(
        'SectionHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=12,
        textColor=colors.HexColor('#FFFFFF'),
        alignment=TA_LEFT
    )

    h2_style = ParagraphStyle(
        'H2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#0F766E'),
        spaceBefore=3,
        spaceAfter=2
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor('#1E293B'),
        alignment=TA_LEFT,
        spaceAfter=2
    )

    body_bold = ParagraphStyle(
        'BodyBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor('#0F172A'),
        alignment=TA_LEFT,
        spaceAfter=2
    )

    quote_box = ParagraphStyle(
        'QuoteBox',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor('#0F172A'),
        alignment=TA_LEFT
    )

    table_cell = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7,
        leading=9,
        textColor=colors.HexColor('#1E293B')
    )

    table_cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7,
        leading=9,
        textColor=colors.HexColor('#0F172A')
    )

    table_cell_code = ParagraphStyle(
        'TableCellCode',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=6.5,
        leading=8.5,
        textColor=colors.HexColor('#0F766E')
    )

    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=6.5,
        leading=8,
        textColor=colors.HexColor('#64748B'),
        alignment=TA_CENTER
    )

    return {
        'title': title_style,
        'subtitle': subtitle_style,
        'badge': badge_style,
        'section_header': section_header,
        'h2': h2_style,
        'body': body_style,
        'body_bold': body_bold,
        'quote': quote_box,
        'table_cell': table_cell,
        'table_cell_bold': table_cell_bold,
        'table_cell_code': table_cell_code,
        'footer': footer_style
    }

def make_section_banner(title_text, styles, width=539):
    p = Paragraph(f"&nbsp;&nbsp;<b>{title_text}</b>", styles['section_header'])
    t = Table([[p]], colWidths=[width])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#0F172A')),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 2),
        ('RIGHTPADDING', (0,0), (-1,-1), 2),
    ]))
    return t

def make_callout_box(content_p, styles, width=539, bg_color='#F1F5F9', border_color='#0F766E'):
    t = Table([[content_p]], colWidths=[width])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor(bg_color)),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LINEBEFORE', (0,0), (0,-1), 2.5, colors.HexColor(border_color)),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
    ]))
    return t

print("[INIT] PDF Builder library ready.")
