"""
Space Weather PDF Export

This module provides professional PDF report generation for space weather data.
Uses ReportLab for reliable, production-quality PDF creation.

Key Features:
- Executive briefing format
- Color-coded severity indicators
- Embedded chart images
- NZDF-ready professional styling
- Automatic page breaks
- Header/footer with branding

Functions:
    - create_space_weather_pdf: Main PDF generation function
    - SpaceWeatherPDF: Custom PDF class with styling
    - Helper functions for tables, charts, and formatting
"""

from typing import Optional, Dict, List, Any, Tuple
from datetime import datetime
import io
import tempfile
import os
from pathlib import Path

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors as rl_colors
    from reportlab.lib.units import cm, mm
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        PageBreak, Image as RLImage, KeepTogether
    )
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
    from reportlab.pdfgen import canvas
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

from .constants import SEVERITY_COLORS, SEVERITY_LEVELS
from .scales import r_scale, s_scale, g_scale

import logging
logger = logging.getLogger(__name__)


# PDF Color Scheme (NZDF-compatible professional colors)
PDF_COLORS = {
    "primary": rl_colors.HexColor("#003366") if REPORTLAB_AVAILABLE else None,  # NZDF Blue
    "secondary": rl_colors.HexColor("#1e5a8e") if REPORTLAB_AVAILABLE else None,
    "accent": rl_colors.HexColor("#4f9ecf") if REPORTLAB_AVAILABLE else None,
    "text": rl_colors.black if REPORTLAB_AVAILABLE else None,
    "text_light": rl_colors.HexColor("#666666") if REPORTLAB_AVAILABLE else None,
    "background": rl_colors.white if REPORTLAB_AVAILABLE else None,
    "grid": rl_colors.HexColor("#cccccc") if REPORTLAB_AVAILABLE else None,
}

# Severity color mapping (R/S/G scales)
SEVERITY_RGB = {
    "none": rl_colors.HexColor("#82ca71") if REPORTLAB_AVAILABLE else None,  # Green
    "minor": rl_colors.HexColor("#f1c40f") if REPORTLAB_AVAILABLE else None,  # Yellow
    "moderate": rl_colors.HexColor("#e67e22") if REPORTLAB_AVAILABLE else None,  # Orange
    "strong": rl_colors.HexColor("#e74c3c") if REPORTLAB_AVAILABLE else None,  # Red
    "severe": rl_colors.HexColor("#c0392b") if REPORTLAB_AVAILABLE else None,  # Dark Red
    "extreme": rl_colors.HexColor("#8e44ad") if REPORTLAB_AVAILABLE else None,  # Purple
}


def check_reportlab_available() -> bool:
    """Check if reportlab is available."""
    return REPORTLAB_AVAILABLE


def get_severity_color(scale_value: str, scale_type: str = "r") -> Any:
    """
    Get ReportLab color for a scale value.
    
    Args:
        scale_value: Scale value like "R3", "S2", "G1", etc.
        scale_type: Type of scale ("r", "s", or "g")
        
    Returns:
        ReportLab Color object
    """
    if not REPORTLAB_AVAILABLE:
        return None
    
    # Extract severity level from scale value
    if scale_value.upper() in ["NONE", "R0", "S0", "G0", "-"]:
        return SEVERITY_RGB["none"]
    
    # Try to get severity from the scale functions
    try:
        if scale_type == "r":
            _, severity = r_scale(1e-5)  # This will be overridden
        elif scale_type == "s":
            _, severity = s_scale(10)
        else:
            _, severity = g_scale(5)
            
        # Map severity to color
        severity_map = {
            "minor": "minor",
            "moderate": "moderate", 
            "strong": "strong",
            "severe": "severe",
            "extreme": "extreme"
        }
        return SEVERITY_RGB.get(severity_map.get(severity, "none"), SEVERITY_RGB["none"])
    except:
        return SEVERITY_RGB["none"]


class SpaceWeatherPDF:
    """
    Custom PDF document class for space weather reports.
    
    Handles header, footer, styling, and page numbering.
    """
    
    def __init__(
        self, 
        output_path: str,
        title: str = "Space Weather Executive Brief",
        logo_path: Optional[str] = None,
        organization: str = "NZDF Space Weather Service"
    ):
        """
        Initialize PDF document.
        
        Args:
            output_path: Path where PDF will be saved
            title: Document title
            logo_path: Optional path to organization logo
            organization: Organization name for footer
        """
        self.output_path = output_path
        self.title = title
        self.logo_path = logo_path
        self.organization = organization
        self.story = []  # Content elements
        
        # Create document
        self.doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=3*cm,
            bottomMargin=2.5*cm,
            title=title,
            author=organization
        )
        
        # Setup styles
        self._setup_styles()
    
    def _setup_styles(self):
        """Setup paragraph and text styles."""
        self.styles = getSampleStyleSheet()
        
        # Custom title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            textColor=PDF_COLORS["primary"],
            spaceAfter=12,
            spaceBefore=0,
            alignment=TA_LEFT,
            fontName='Helvetica-Bold'
        ))
        
        # Section heading style
        self.styles.add(ParagraphStyle(
            name='SectionHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=PDF_COLORS["secondary"],
            spaceAfter=8,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))
        
        # Body text style
        self.styles.add(ParagraphStyle(
            name='BodyText',
            parent=self.styles['BodyText'],
            fontSize=11,
            textColor=PDF_COLORS["text"],
            alignment=TA_JUSTIFY,
            spaceAfter=6,
            leading=14
        ))
        
        # Bullet point style
        self.styles.add(ParagraphStyle(
            name='BulletText',
            parent=self.styles['BodyText'],
            fontSize=11,
            textColor=PDF_COLORS["text"],
            leftIndent=20,
            bulletIndent=10,
            spaceAfter=4,
            leading=14
        ))
        
        # Caption style
        self.styles.add(ParagraphStyle(
            name='Caption',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=PDF_COLORS["text_light"],
            alignment=TA_CENTER,
            spaceAfter=6
        ))
    
    def _header_footer(self, canvas, doc):
        """Draw header and footer on each page."""
        canvas.saveState()
        
        # Header
        canvas.setFillColor(PDF_COLORS["primary"])
        canvas.rect(0, A4[1] - 2*cm, A4[0], 2*cm, fill=True, stroke=False)
        
        # Logo (if provided)
        if self.logo_path and os.path.exists(self.logo_path):
            try:
                canvas.drawImage(
                    self.logo_path,
                    1.5*cm,
                    A4[1] - 1.8*cm,
                    width=2*cm,
                    height=1.5*cm,
                    preserveAspectRatio=True,
                    mask='auto'
                )
            except Exception as e:
                logger.warning(f"Could not embed logo: {e}")
        
        # Title in header
        canvas.setFillColor(rl_colors.white)
        canvas.setFont('Helvetica-Bold', 14)
        canvas.drawString(4*cm if self.logo_path else 2*cm, A4[1] - 1.3*cm, self.title)
        
        # Footer
        canvas.setStrokeColor(PDF_COLORS["grid"])
        canvas.line(2*cm, 2*cm, A4[0] - 2*cm, 2*cm)
        
        canvas.setFillColor(PDF_COLORS["text_light"])
        canvas.setFont('Helvetica', 9)
        
        # Generated timestamp
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
        canvas.drawString(2*cm, 1.5*cm, f"Generated: {timestamp}")
        
        # Page number
        page_num = f"Page {doc.page}"
        canvas.drawRightString(A4[0] - 2*cm, 1.5*cm, page_num)
        
        # Organization
        canvas.drawCentredString(A4[0] / 2, 1.5*cm, self.organization)
        
        canvas.restoreState()
    
    def add_title(self, text: str):
        """Add a main title to the document."""
        self.story.append(Paragraph(text, self.styles['CustomTitle']))
        self.story.append(Spacer(1, 0.3*cm))
    
    def add_section_heading(self, text: str):
        """Add a section heading."""
        self.story.append(Spacer(1, 0.4*cm))
        self.story.append(Paragraph(text, self.styles['SectionHeading']))
    
    def add_paragraph(self, text: str):
        """Add a body paragraph."""
        self.story.append(Paragraph(text, self.styles['BodyText']))
    
    def add_bullet_list(self, items: List[str]):
        """Add a bulleted list."""
        for item in items:
            bullet_text = f"• {item}"
            self.story.append(Paragraph(bullet_text, self.styles['BulletText']))
    
    def add_table(
        self,
        data: List[List[str]],
        col_widths: Optional[List[float]] = None,
        header_row: bool = True,
        cell_colors: Optional[List[List[Any]]] = None
    ):
        """
        Add a table to the document.
        
        Args:
            data: Table data as list of rows
            col_widths: Optional column widths in cm
            header_row: If True, first row is styled as header
            cell_colors: Optional 2D list of ReportLab colors for cells
        """
        if not data:
            return
        
        # Create table
        if col_widths:
            col_widths = [w*cm for w in col_widths]
        
        table = Table(data, colWidths=col_widths)
        
        # Base style
        style = [
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, PDF_COLORS["grid"]),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [rl_colors.white, rl_colors.HexColor("#f9f9f9")]),
        ]
        
        # Header row styling
        if header_row:
            style.extend([
                ('BACKGROUND', (0, 0), (-1, 0), PDF_COLORS["primary"]),
                ('TEXTCOLOR', (0, 0), (-1, 0), rl_colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
            ])
        
        # Apply custom cell colors
        if cell_colors:
            for row_idx, row in enumerate(cell_colors):
                for col_idx, color in enumerate(row):
                    if color:
                        style.append(('BACKGROUND', (col_idx, row_idx), (col_idx, row_idx), color))
        
        table.setStyle(TableStyle(style))
        self.story.append(table)
        self.story.append(Spacer(1, 0.5*cm))
    
    def add_image(
        self,
        image_path: str,
        width: Optional[float] = None,
        caption: Optional[str] = None
    ):
        """
        Add an image to the document.
        
        Args:
            image_path: Path to image file
            width: Image width in cm (default: fit page width)
            caption: Optional image caption
        """
        if not os.path.exists(image_path):
            logger.warning(f"Image not found: {image_path}")
            return
        
        try:
            if width is None:
                width = 16  # Default width in cm
            
            img = RLImage(image_path, width=width*cm, height=None)
            self.story.append(img)
            
            if caption:
                self.story.append(Spacer(1, 0.2*cm))
                self.story.append(Paragraph(caption, self.styles['Caption']))
            
            self.story.append(Spacer(1, 0.5*cm))
        except Exception as e:
            logger.error(f"Failed to embed image {image_path}: {e}")
    
    def add_page_break(self):
        """Add a page break."""
        self.story.append(PageBreak())
    
    def add_spacer(self, height_cm: float = 0.5):
        """Add vertical space."""
        self.story.append(Spacer(1, height_cm*cm))
    
    def build(self):
        """Build and save the PDF document."""
        self.doc.build(self.story, onFirstPage=self._header_footer, onLaterPages=self._header_footer)


def create_space_weather_pdf(
    output_path: str,
    current_conditions: Dict[str, str],
    past_conditions: Dict[str, str],
    forecast_24h: Dict[str, Any],
    summary_text: str,
    discussion_text: Optional[str] = None,
    aurora_text: Optional[str] = None,
    chart_paths: Optional[Dict[str, str]] = None,
    logo_path: Optional[str] = None,
    organization: str = "NZDF Space Weather Service",
    include_charts: bool = True,
    include_discussion: bool = True
) -> bool:
    """
    Create a comprehensive space weather PDF report.
    
    Args:
        output_path: Where to save the PDF
        current_conditions: Dict with current R/S/G scale values
        past_conditions: Dict with past 24h R/S/G values
        forecast_24h: Dict with 24h forecast data
        summary_text: Executive summary text
        discussion_text: Optional NOAA discussion text
        aurora_text: Optional aurora forecast text
        chart_paths: Optional dict of chart image paths {"xray": "path.png", ...}
        logo_path: Optional path to organization logo
        organization: Organization name
        include_charts: Include chart images
        include_discussion: Include full discussion text
        
    Returns:
        True if PDF created successfully, False otherwise
        
    Example:
        >>> success = create_space_weather_pdf(
        ...     "space_weather_report.pdf",
        ...     current_conditions={"r": "R1", "s": "S0", "g": "G2"},
        ...     past_conditions={"r": "R2", "s": "S1", "g": "G1"},
        ...     forecast_24h={"kp": 4, "r12": 25, "r3": 5, "s1": 10},
        ...     summary_text="Current space weather conditions are moderate..."
        ... )
    """
    if not REPORTLAB_AVAILABLE:
        logger.error("ReportLab not available. Install with: pip install reportlab")
        return False
    
    try:
        # Create PDF document
        pdf = SpaceWeatherPDF(
            output_path=output_path,
            title="Space Weather Executive Brief",
            logo_path=logo_path,
            organization=organization
        )
        
        # Title
        pdf.add_title("Executive Summary")
        
        # Current status bullets
        kp_value = forecast_24h.get("kp", "~")
        r12_prob = forecast_24h.get("r12", 0)
        r3_prob = forecast_24h.get("r3", 0)
        s1_prob = forecast_24h.get("s1", 0)
        
        bullets = [
            f"Current status (NOAA): {current_conditions.get('r', 'R0')}/{current_conditions.get('s', 'S0')}/{current_conditions.get('g', 'G0')}",
            f"Next 24h forecast: Kp ~{kp_value}, R1-R2 {r12_prob}% / R3+ {r3_prob}%, S1+ {s1_prob}%",
        ]
        
        if aurora_text:
            aurora_summary = aurora_text.split('\n')[0] if '\n' in aurora_text else aurora_text[:100]
            bullets.append(f"Aurora outlook: {aurora_summary}")
        
        pdf.add_bullet_list(bullets)
        pdf.add_spacer(0.5)
        
        # Summary paragraph
        pdf.add_paragraph(summary_text)
        
        # Key Metrics Table
        pdf.add_section_heading("Key Metrics (NOAA R/S/G Scales)")
        
        # Prepare table data
        table_data = [
            ["Timeframe", "R - Radio Blackouts", "S - Radiation Storms", "G - Geomagnetic Storms"]
        ]
        
        # Current row
        curr_r = current_conditions.get('r', 'R0')
        curr_s = current_conditions.get('s', 'S0')
        curr_g = current_conditions.get('g', 'G0')
        table_data.append(["Current", curr_r, curr_s, curr_g])
        
        # Past 24h row
        past_r = past_conditions.get('r', 'R0')
        past_s = past_conditions.get('s', 'S0')
        past_g = past_conditions.get('g', 'G0')
        table_data.append(["Past 24h", past_r, past_s, past_g])
        
        # Forecast row
        fcst_r = f"R1-R2: {r12_prob}%\nR3+: {r3_prob}%"
        fcst_s = f"S1+: {s1_prob}%"
        fcst_g = f"Kp ~{kp_value}"
        table_data.append(["Next 24h", fcst_r, fcst_s, fcst_g])
        
        # Prepare cell colors (severity-based)
        cell_colors = [
            [None, None, None, None],  # Header row
            [None, get_severity_color(curr_r, "r"), get_severity_color(curr_s, "s"), get_severity_color(curr_g, "g")],
            [None, get_severity_color(past_r, "r"), get_severity_color(past_s, "s"), get_severity_color(past_g, "g")],
            [None, SEVERITY_RGB["minor"], SEVERITY_RGB["minor"], SEVERITY_RGB["moderate"]],  # Forecast colors
        ]
        
        pdf.add_table(
            data=table_data,
            col_widths=[4, 4.5, 4.5, 4.5],
            header_row=True,
            cell_colors=cell_colors
        )
        
        # Charts (if provided and requested)
        if include_charts and chart_paths:
            pdf.add_page_break()
            pdf.add_section_heading("Recent Trends")
            
            for chart_name, chart_path in chart_paths.items():
                if chart_path and os.path.exists(chart_path):
                    pdf.add_image(
                        chart_path,
                        width=16,
                        caption=f"{chart_name.replace('_', ' ').title()} - Last 24 hours"
                    )
        
        # NOAA Discussion (if provided and requested)
        if include_discussion and discussion_text:
            pdf.add_page_break()
            pdf.add_section_heading("NOAA Space Weather Discussion")
            
            # Split into paragraphs
            paragraphs = discussion_text.split('\n\n')
            for para in paragraphs:
                para = para.strip()
                if para:
                    pdf.add_paragraph(para)
        
        # Aurora forecast (if provided)
        if aurora_text:
            pdf.add_page_break()
            pdf.add_section_heading("Aurora Forecast")
            pdf.add_paragraph(aurora_text)
        
        # Build PDF
        pdf.build()
        logger.info(f"PDF created successfully: {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to create PDF: {e}")
        return False


def save_chart_for_pdf(fig, output_path: str, width: int = 1200, height: int = 500) -> bool:
    """
    Save a Plotly figure as an image for PDF embedding.
    
    This is a helper function that handles the chart export more reliably
    than the old kaleido-based approach.
    
    Args:
        fig: Plotly Figure object
        output_path: Where to save the image
        width: Image width in pixels
        height: Image height in pixels
        
    Returns:
        True if successful, False otherwise
    """
    if fig is None:
        return False
    
    try:
        # Try using kaleido first (if available)
        try:
            import plotly.io as pio
            pio.write_image(fig, output_path, width=width, height=height, scale=2)
            return True
        except (ImportError, Exception):
            pass
        
        # Fallback: save as HTML then convert (requires additional tools)
        logger.warning("Kaleido not available. Charts will not be embedded in PDF.")
        logger.info("To enable chart embedding, install: pip install kaleido")
        return False
        
    except Exception as e:
        logger.error(f"Failed to save chart: {e}")
        return False


# Module exports
__all__ = [
    "create_space_weather_pdf",
    "SpaceWeatherPDF",
    "save_chart_for_pdf",
    "check_reportlab_available",
    "PDF_COLORS",
    "SEVERITY_RGB",
]
