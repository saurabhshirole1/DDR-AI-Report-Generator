# pdf_export.py
# ---------------------------------------------------------------------------
# This file converts our generated report into a downloadable PDF file.
#
# We use the 'reportlab' library to create PDFs in Python.
# ReportLab lets us control fonts, colors, spacing, and layout.
#
# The PDF will look professional with:
# - A cover page with title and document info
# - Properly formatted sections with headers
# - Page numbers
# - Clean typography
# ---------------------------------------------------------------------------

from reportlab.lib.pagesizes import A4            # Standard A4 page size
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch              # For measurements
from reportlab.lib import colors                  # For colors
from reportlab.platypus import (
    SimpleDocTemplate,    # Main PDF document builder
    Paragraph,           # For text blocks
    Spacer,              # For adding empty space
    HRFlowable,         # For horizontal lines
    PageBreak            # For page breaks
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
import io                # For creating files in memory (not on disk)
import re                # For cleaning markdown formatting


def clean_markdown(text: str) -> str:
    """
    Removes markdown formatting from text so it looks clean in PDF.
    
    For example:
    **bold text** → bold text
    ### Header → Header
    - bullet point → bullet point
    
    ReportLab handles formatting differently from markdown,
    so we need to clean it first.
    """
    
    if not text:
        return ""
    
    # Remove **bold** markers (keep the text inside)
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    
    # Remove *italic* markers
    text = re.sub(r"\*(.*?)\*", r"\1", text)
    
    # Remove ### headers (keep text)
    text = re.sub(r"###\s+", "", text)
    
    # Remove ## headers (keep text)
    text = re.sub(r"##\s+", "", text)
    
    # Remove # headers (keep text)
    text = re.sub(r"#\s+", "", text)
    
    return text.strip()


def create_pdf_styles():
    """
    Creates custom styles for our PDF.
    
    Styles control font, size, color, spacing for different
    parts of the document (title, headings, body text, etc.)
    
    Returns:
    - A dictionary of named styles
    """
    
    # Get default styles as a starting point
    styles = getSampleStyleSheet()
    
    # Custom style for the main report title (big, centered, dark blue)
    title_style = ParagraphStyle(
        name="ReportTitle",
        fontSize=24,
        fontName="Helvetica-Bold",
        textColor=colors.HexColor("#1a237e"),   # Dark blue
        alignment=TA_CENTER,
        spaceAfter=12
    )
    
    # Custom style for subtitle (smaller, centered, gray)
    subtitle_style = ParagraphStyle(
        name="Subtitle",
        fontSize=11,
        fontName="Helvetica",
        textColor=colors.HexColor("#666666"),   # Gray
        alignment=TA_CENTER,
        spaceAfter=6
    )
    
    # Custom style for section headers (medium, left aligned, blue)
    section_header_style = ParagraphStyle(
        name="SectionHeader",
        fontSize=14,
        fontName="Helvetica-Bold",
        textColor=colors.HexColor("#1565c0"),   # Blue
        spaceBefore=16,
        spaceAfter=8
    )
    
    # Custom style for document info (small, left aligned)
    info_style = ParagraphStyle(
        name="InfoStyle",
        fontSize=10,
        fontName="Helvetica",
        textColor=colors.HexColor("#333333"),
        spaceAfter=4
    )
    
    # Custom style for body text (normal size, justified)
    body_style = ParagraphStyle(
        name="BodyText",
        fontSize=10,
        fontName="Helvetica",
        textColor=colors.HexColor("#212121"),
        alignment=TA_JUSTIFY,    # Justified = aligned on both sides
        spaceAfter=8,
        leading=14               # Line height
    )
    
    # Custom style for bullet points
    bullet_style = ParagraphStyle(
        name="BulletStyle",
        fontSize=10,
        fontName="Helvetica",
        textColor=colors.HexColor("#212121"),
        leftIndent=20,           # Indent bullet points from left
        spaceAfter=4,
        leading=14
    )
    
    return {
        "title": title_style,
        "subtitle": subtitle_style,
        "section_header": section_header_style,
        "info": info_style,
        "body": body_style,
        "bullet": bullet_style
    }


def process_content_to_paragraphs(content: str, styles: dict) -> list:
    """
    Converts a block of text into ReportLab Paragraph objects.
    
    We need to handle different line types:
    - Bullet points (lines starting with -)
    - Regular text
    - Empty lines (we add small spacing)
    
    Returns:
    - List of ReportLab flowable objects (Paragraphs and Spacers)
    """
    
    elements = []
    
    # Split content into individual lines
    lines = content.split("\n")
    
    for line in lines:
        line = line.strip()
        
        # Skip empty lines but add a small space
        if not line:
            elements.append(Spacer(1, 4))
            continue
        
        # Skip lines that are just dashes (markdown horizontal rules)
        if line.startswith("---") or line.startswith("==="):
            elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.lightgrey))
            continue
        
        # Handle bullet points (lines starting with - or *)
        if line.startswith("- ") or line.startswith("* "):
            # Remove the bullet marker and clean markdown
            bullet_text = clean_markdown(line[2:])
            if bullet_text:
                # Add bullet symbol manually
                elements.append(Paragraph(f"• {bullet_text}", styles["bullet"]))
        
        # Handle sub-headers (### in markdown)
        elif line.startswith("###"):
            header_text = clean_markdown(line)
            if header_text:
                elements.append(Paragraph(f"<b>{header_text}</b>", styles["body"]))
        
        # Regular text
        else:
            clean_text = clean_markdown(line)
            if clean_text:
                # Wrap in try-except because special characters can sometimes
                # cause issues with ReportLab's Paragraph
                try:
                    elements.append(Paragraph(clean_text, styles["body"]))
                except Exception:
                    # If paragraph fails, add as plain text
                    elements.append(Paragraph(clean_text.encode("ascii", "ignore").decode(), styles["body"]))
    
    return elements


def export_report_to_pdf(report: dict) -> bytes:
    """
    Main function that creates the complete PDF file.
    
    Takes our report object and returns PDF as bytes.
    These bytes can then be offered as a download in Streamlit.
    
    Returns:
    - PDF content as bytes (binary data)
    """
    
    # Create a buffer in memory to hold the PDF
    # io.BytesIO() is like a file but stored in RAM, not on disk
    buffer = io.BytesIO()
    
    # Create the PDF document
    # A4 size, with margins on all sides
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch
    )
    
    # Get our custom styles
    styles = create_pdf_styles()
    
    # This list holds all the content elements of the PDF
    # ReportLab builds the PDF from this list top to bottom
    elements = []
    
    # -----------------------------------------------------------------------
    # COVER PAGE
    # -----------------------------------------------------------------------
    
    # Add some space at the top
    elements.append(Spacer(1, 1 * inch))
    
    # Main title
    elements.append(Paragraph(report["title"], styles["title"]))
    elements.append(Spacer(1, 0.2 * inch))
    
    # Horizontal line under title
    elements.append(HRFlowable(width="80%", thickness=2, color=colors.HexColor("#1a237e")))
    elements.append(Spacer(1, 0.3 * inch))
    
    # Generated by and date
    elements.append(Paragraph(f"Generated by: {report['generated_by']}", styles["subtitle"]))
    elements.append(Paragraph(f"Date: {report['generated_at']}", styles["subtitle"]))
    elements.append(Spacer(1, 0.5 * inch))
    
    # Document information
    elements.append(Paragraph("DOCUMENTS ANALYZED", styles["section_header"]))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.lightgrey))
    elements.append(Spacer(1, 0.1 * inch))
    
    # Document 1 info
    doc1 = report["document_1"]
    elements.append(Paragraph(f"<b>Document 1:</b> {doc1['name']}", styles["info"]))
    elements.append(Paragraph(f"Pages: {doc1['pages']} | Size: {doc1['size_kb']} KB", styles["info"]))
    elements.append(Spacer(1, 0.15 * inch))
    
    # Document 2 info
    doc2 = report["document_2"]
    elements.append(Paragraph(f"<b>Document 2:</b> {doc2['name']}", styles["info"]))
    elements.append(Paragraph(f"Pages: {doc2['pages']} | Size: {doc2['size_kb']} KB", styles["info"]))
    
    # Page break after cover page
    elements.append(PageBreak())
    
    # -----------------------------------------------------------------------
    # REPORT SECTIONS
    # -----------------------------------------------------------------------
    
    for section_name, content in report["sections"].items():
        
        # Section header
        elements.append(Paragraph(section_name.upper(), styles["section_header"]))
        elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#1565c0")))
        elements.append(Spacer(1, 0.1 * inch))
        
        # Section content - convert text to paragraph elements
        content_elements = process_content_to_paragraphs(content, styles)
        elements.extend(content_elements)
        
        # Space after each section
        elements.append(Spacer(1, 0.2 * inch))
    
    # -----------------------------------------------------------------------
    # BUILD THE PDF
    # -----------------------------------------------------------------------
    
    # build() takes our elements list and creates the actual PDF
    doc.build(elements)
    
    # Get the PDF bytes from the buffer
    # seek(0) moves back to the start so we can read everything
    buffer.seek(0)
    pdf_bytes = buffer.read()
    
    return pdf_bytes
