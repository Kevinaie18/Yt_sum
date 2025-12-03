"""
Export Module

Handles generating downloadable files in TXT, MD, and PDF formats.
"""

import io
from typing import Tuple
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_LEFT, TA_JUSTIFY


def generate_txt(summary: str, video_id: str = None) -> Tuple[bytes, str]:
    """
    Generate a plain text file from the summary.
    
    Args:
        summary: Summary text (may contain markdown)
        video_id: Optional video ID for filename
        
    Returns:
        Tuple of (file_bytes, filename)
    """
    # Clean up markdown formatting for plain text
    text = summary
    
    # Remove markdown headers but keep the text
    lines = []
    for line in text.split('\n'):
        # Convert headers to uppercase with underline
        if line.startswith('## '):
            lines.append('')
            lines.append(line[3:].upper())
            lines.append('=' * len(line[3:]))
        elif line.startswith('# '):
            lines.append('')
            lines.append(line[2:].upper())
            lines.append('=' * len(line[2:]))
        else:
            lines.append(line)
    
    text = '\n'.join(lines)
    
    # Encode to bytes
    file_bytes = text.encode('utf-8')
    
    # Generate filename
    filename = f"summary_{video_id}.txt" if video_id else "summary.txt"
    
    return file_bytes, filename


def generate_md(summary: str, video_id: str = None) -> Tuple[bytes, str]:
    """
    Generate a markdown file from the summary.
    
    Args:
        summary: Summary text (already in markdown format)
        video_id: Optional video ID for filename
        
    Returns:
        Tuple of (file_bytes, filename)
    """
    # Add a title header if not present
    if not summary.startswith('#'):
        text = f"# Video Summary\n\n{summary}"
    else:
        text = summary
    
    # Add metadata footer
    if video_id:
        text += f"\n\n---\n*Generated from YouTube video: {video_id}*"
    
    # Encode to bytes
    file_bytes = text.encode('utf-8')
    
    # Generate filename
    filename = f"summary_{video_id}.md" if video_id else "summary.md"
    
    return file_bytes, filename


def generate_pdf(summary: str, video_id: str = None) -> Tuple[bytes, str]:
    """
    Generate a PDF file from the summary.
    
    Args:
        summary: Summary text (may contain markdown)
        video_id: Optional video ID for filename
        
    Returns:
        Tuple of (file_bytes, filename)
    """
    # Create a buffer to hold the PDF
    buffer = io.BytesIO()
    
    # Create the PDF document
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch
    )
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=20,
        alignment=TA_LEFT
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceBefore=15,
        spaceAfter=10,
        alignment=TA_LEFT
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=11,
        leading=14,
        alignment=TA_JUSTIFY,
        spaceAfter=8
    )
    
    bullet_style = ParagraphStyle(
        'CustomBullet',
        parent=styles['Normal'],
        fontSize=11,
        leading=14,
        leftIndent=20,
        spaceAfter=6
    )
    
    # Build the PDF content
    story = []
    
    # Add title
    story.append(Paragraph("Video Summary", title_style))
    story.append(Spacer(1, 10))
    
    # Process the markdown content
    lines = summary.split('\n')
    current_text = []
    
    def flush_text():
        """Flush accumulated text as a paragraph."""
        if current_text:
            text = ' '.join(current_text).strip()
            if text:
                # Escape special characters for ReportLab
                text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                story.append(Paragraph(text, body_style))
            current_text.clear()
    
    for line in lines:
        line = line.strip()
        
        if not line:
            flush_text()
            continue
        
        # Handle headers
        if line.startswith('## '):
            flush_text()
            header_text = line[3:].replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            story.append(Paragraph(header_text, heading_style))
        elif line.startswith('# '):
            flush_text()
            header_text = line[2:].replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            story.append(Paragraph(header_text, title_style))
        # Handle bullet points
        elif line.startswith('- ') or line.startswith('* '):
            flush_text()
            bullet_text = line[2:].replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            # Add bullet character
            story.append(Paragraph(f"• {bullet_text}", bullet_style))
        # Handle numbered lists
        elif len(line) > 2 and line[0].isdigit() and line[1] in '.):':
            flush_text()
            list_text = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            story.append(Paragraph(list_text, bullet_style))
        else:
            # Regular text - accumulate
            current_text.append(line)
    
    # Flush any remaining text
    flush_text()
    
    # Add footer with video ID if provided
    if video_id:
        story.append(Spacer(1, 20))
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=9,
            textColor='gray'
        )
        story.append(Paragraph(f"Generated from YouTube video: {video_id}", footer_style))
    
    # Build PDF
    doc.build(story)
    
    # Get the PDF bytes
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    # Generate filename
    filename = f"summary_{video_id}.pdf" if video_id else "summary.pdf"
    
    return pdf_bytes, filename


def export_summary(summary: str, format: str, video_id: str = None) -> Tuple[bytes, str, str]:
    """
    Export summary in the specified format.
    
    Args:
        summary: Summary text
        format: Export format ('TXT', 'MD', or 'PDF')
        video_id: Optional video ID for filename
        
    Returns:
        Tuple of (file_bytes, filename, mime_type)
    """
    format = format.upper()
    
    if format == 'TXT':
        file_bytes, filename = generate_txt(summary, video_id)
        return file_bytes, filename, 'text/plain'
    
    elif format == 'MD':
        file_bytes, filename = generate_md(summary, video_id)
        return file_bytes, filename, 'text/markdown'
    
    elif format == 'PDF':
        file_bytes, filename = generate_pdf(summary, video_id)
        return file_bytes, filename, 'application/pdf'
    
    else:
        raise ValueError(f"Unsupported format: {format}")

