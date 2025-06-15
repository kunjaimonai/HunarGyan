"""
PDF Converter Module
Converts markdown text to PDF using PyMuPDF
"""

import fitz  # PyMuPDF
import markdown
import re
from typing import Optional, List, Tuple
from html import unescape


def parse_markdown_elements(md_text: str) -> List[dict]:
    """Parse markdown into structured elements for PDF rendering"""
    
    # Convert markdown to HTML first
    md = markdown.Markdown(extensions=['tables', 'fenced_code', 'toc'])
    html = md.convert(md_text)
    
    elements = []
    lines = md_text.split('\n')
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        if not line:
            elements.append({'type': 'space', 'content': ''})
            i += 1
            continue
            
        # Headers
        if line.startswith('#'):
            level = len(line) - len(line.lstrip('#'))
            content = line.lstrip('# ').strip()
            elements.append({
                'type': 'header',
                'level': level,
                'content': content
            })
            
        # Code blocks
        elif line.startswith('```'):
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith('```'):
                code_lines.append(lines[i])
                i += 1
            elements.append({
                'type': 'code_block',
                'content': '\n'.join(code_lines)
            })
            
        # Tables
        elif '|' in line and i + 1 < len(lines) and '|' in lines[i + 1]:
            table_lines = [line]
            i += 1
            # Skip separator line if it exists
            if re.match(r'^[\s\|\-\:]+$', lines[i]):
                i += 1
            # Collect table rows
            while i < len(lines) and '|' in lines[i].strip():
                table_lines.append(lines[i])
                i += 1
            i -= 1  # Adjust for the outer loop increment
            
            elements.append({
                'type': 'table',
                'content': table_lines
            })
            
        # Lists
        elif line.startswith(('- ', '* ', '+ ')) or re.match(r'^\d+\. ', line):
            list_items = [line]
            i += 1
            while i < len(lines) and (lines[i].startswith(('  ', '\t')) or 
                                    lines[i].strip().startswith(('- ', '* ', '+ ')) or 
                                    re.match(r'^\d+\. ', lines[i].strip())):
                if lines[i].strip():
                    list_items.append(lines[i])
                i += 1
            i -= 1
            
            elements.append({
                'type': 'list',
                'content': list_items
            })
            
        # Blockquotes
        elif line.startswith('>'):
            quote_lines = [line]
            i += 1
            while i < len(lines) and lines[i].startswith('>'):
                quote_lines.append(lines[i])
                i += 1
            i -= 1
            
            elements.append({
                'type': 'blockquote',
                'content': [l.lstrip('> ') for l in quote_lines]
            })
            
        # Regular paragraph
        else:
            para_lines = [line]
            i += 1
            while (i < len(lines) and lines[i].strip() and 
                   not lines[i].startswith(('#', '```', '>', '- ', '* ', '+ ')) and
                   not re.match(r'^\d+\. ', lines[i]) and '|' not in lines[i]):
                para_lines.append(lines[i].strip())
                i += 1
            i -= 1
            
            elements.append({
                'type': 'paragraph',
                'content': ' '.join(para_lines)
            })
        
        i += 1
    
    return elements


def process_text_formatting(text: str) -> List[Tuple[str, dict]]:
    """Process markdown formatting in text and return segments with styles"""
    segments = []
    
    # Handle bold, italic, and code
    patterns = [
        (r'\*\*(.*?)\*\*', {'bold': True}),
        (r'\*(.*?)\*', {'italic': True}),
        (r'`(.*?)`', {'code': True}),
    ]
    
    current_text = text
    current_pos = 0
    
    while current_pos < len(current_text):
        next_match = None
        next_pos = len(current_text)
        next_style = {}
        
        for pattern, style in patterns:
            match = re.search(pattern, current_text[current_pos:])
            if match and current_pos + match.start() < next_pos:
                next_match = match
                next_pos = current_pos + match.start()
                next_style = style
        
        if next_match:
            # Add text before match
            if next_pos > current_pos:
                segments.append((current_text[current_pos:next_pos], {}))
            
            # Add formatted text
            segments.append((next_match.group(1), next_style))
            current_pos = current_pos + next_match.end()
        else:
            # Add remaining text
            segments.append((current_text[current_pos:], {}))
            break
    
    return segments


def text_to_pdf(text: str, title: Optional[str] = None) -> bytes:
    """
    Convert markdown text to PDF
    
    Args:
        text (str): Markdown text to convert
        title (str, optional): PDF title for metadata
        
    Returns:
        bytes: PDF file as bytes
        
    Raises:
        Exception: If PDF generation fails
    """
    doc = fitz.open()
    
    try:
        # Parse markdown elements
        elements = parse_markdown_elements(text)
        
        # Create first page
        page = doc.new_page(width=595, height=842)  # A4
        margin = 50
        page_width = page.rect.width - 2 * margin
        page_height = page.rect.height - 2 * margin
        
        y_pos = margin
        line_height = 20
        
        # Font configurations
        fonts = {
            'regular': 'helv',
            'bold': 'hebo',
            'italic': 'heit',
            'code': 'cour'
        }
        
        def check_new_page(needed_height):
            nonlocal y_pos, page
            if y_pos + needed_height > page.rect.height - margin:
                page = doc.new_page(width=595, height=842)
                y_pos = margin
                return True
            return False
        
        def insert_text_with_formatting(text_segments, x, y, font_size=16):
            """Insert text with formatting support"""
            current_x = x
            max_y = y
            
            for text, style in text_segments:
                if not text.strip():
                    continue
                    
                # Determine font
                font = fonts['regular']
                if style.get('bold'):
                    font = fonts['bold']
                elif style.get('italic'):
                    font = fonts['italic']
                elif style.get('code'):
                    font = fonts['code']
                    font_size = 14
                
                # Insert text
                try:
                    text_width = fitz.get_text_length(text, fontname=font, fontsize=font_size)
                    if current_x + text_width > margin + page_width:
                        # Wrap to next line
                        max_y += line_height
                        current_x = x
                        check_new_page(line_height)
                    
                    page.insert_text(
                        (current_x, max_y),
                        text,
                        fontname=font,
                        fontsize=font_size,
                        color=(0, 0, 0)
                    )
                    current_x += text_width
                except:
                    # Fallback to simple text insertion
                    page.insert_text((current_x, max_y), text, fontsize=font_size)
                    current_x += len(text) * font_size * 0.6
            
            return max_y + line_height
        
        # Render elements
        for element in elements:
            if element['type'] == 'header':
                level = element['level']
                content = element['content']
                
                # Header sizing
                header_sizes = {1: 24, 2: 20, 3: 18, 4: 16, 5: 14, 6: 12}
                font_size = header_sizes.get(level, 16)
                
                check_new_page(font_size + 10)
                y_pos += 10  # Extra space before header
                
                page.insert_text(
                    (margin, y_pos),
                    content,
                    fontname=fonts['bold'],
                    fontsize=font_size,
                    color=(0.17, 0.24, 0.31)  # Dark blue
                )
                y_pos += font_size + 10
                
                # Underline for H1
                if level == 1:
                    page.draw_line(
                        fitz.Point(margin, y_pos - 5),
                        fitz.Point(margin + page_width, y_pos - 5),
                        color=(0.2, 0.6, 0.86),
                        width=2
                    )
                    y_pos += 5
            
            elif element['type'] == 'paragraph':
                content = element['content']
                if content.strip():
                    check_new_page(line_height * 2)
                    segments = process_text_formatting(content)
                    y_pos = insert_text_with_formatting(segments, margin, y_pos)
                    y_pos += 10  # Paragraph spacing
            
            elif element['type'] == 'code_block':
                content = element['content']
                lines = content.split('\n')
                
                check_new_page(len(lines) * 16 + 20)
                
                # Background rectangle
                rect = fitz.Rect(margin - 5, y_pos - 5, 
                               margin + page_width + 5, y_pos + len(lines) * 16 + 10)
                page.draw_rect(rect, color=(0.97, 0.97, 0.97), fill=(0.97, 0.97, 0.97))
                
                for line in lines:
                    page.insert_text(
                        (margin, y_pos),
                        line,
                        fontname=fonts['code'],
                        fontsize=14,
                        color=(0, 0, 0)
                    )
                    y_pos += 16
                y_pos += 15
            
            elif element['type'] == 'list':
                items = element['content']
                for item in items:
                    check_new_page(line_height)
                    
                    # Remove list markers and process
                    clean_item = re.sub(r'^[\s]*[-\*\+][\s]*', '', item)
                    clean_item = re.sub(r'^[\s]*\d+\.[\s]*', '', clean_item)
                    
                    # Add bullet
                    page.insert_text((margin, y_pos), "• ", fontsize=16)
                    
                    segments = process_text_formatting(clean_item.strip())
                    y_pos = insert_text_with_formatting(segments, margin + 15, y_pos)
                y_pos += 10
            
            elif element['type'] == 'blockquote':
                lines = element['content']
                check_new_page(len(lines) * line_height + 20)
                
                # Draw left border
                start_y = y_pos
                for line in lines:
                    segments = process_text_formatting(line)
                    y_pos = insert_text_with_formatting(segments, margin + 20, y_pos, 15)
                
                # Draw quote border
                page.draw_line(
                    fitz.Point(margin + 5, start_y - 5),
                    fitz.Point(margin + 5, y_pos),
                    color=(0.2, 0.6, 0.86),
                    width=3
                )
                y_pos += 10
            
            elif element['type'] == 'table':
                table_lines = element['content']
                if len(table_lines) > 1:
                    # Simple table rendering
                    check_new_page(len(table_lines) * 25)
                    
                    for i, line in enumerate(table_lines):
                        cells = [cell.strip() for cell in line.split('|') if cell.strip()]
                        cell_width = page_width / len(cells) if cells else page_width
                        
                        for j, cell in enumerate(cells):
                            x_pos = margin + j * cell_width
                            
                            # Header row styling
                            if i == 0:
                                page.insert_text(
                                    (x_pos, y_pos),
                                    cell,
                                    fontname=fonts['bold'],
                                    fontsize=14
                                )
                            else:
                                page.insert_text((x_pos, y_pos), cell, fontsize=14)
                        
                        y_pos += 20
                    y_pos += 10
            
            elif element['type'] == 'space':
                y_pos += 10
        
        # Set metadata
        metadata = {
            "creator": "PDF Converter Module",
            "producer": "PyMuPDF"
        }
        
        if title:
            metadata["title"] = title
        
        doc.set_metadata(metadata)
        
        # Return PDF bytes
        pdf_bytes = doc.tobytes()
        return pdf_bytes
        
    except Exception as e:
        raise Exception(f"Failed to generate PDF: {str(e)}")
    finally:
        doc.close()


def convert_markdown_to_pdf(markdown_text: str, document_title: Optional[str] = None) -> bytes:
    """
    Main function to convert markdown to PDF
    
    Args:
        markdown_text (str): The markdown content to convert
        document_title (str, optional): Title for the PDF document
        
    Returns:
        bytes: PDF content as bytes
    """
    return text_to_pdf(markdown_text, document_title)