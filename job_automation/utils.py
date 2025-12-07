from fpdf import FPDF
import re

class PDFResume(FPDF):
    def header(self):
        # We don't want a repeated header on every page for a resume usually, 
        # but if we did, it would go here.
        pass

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', align='C')

    def chapter_title(self, label):
        self.set_font('Helvetica', 'B', 16)
        self.set_text_color(0, 51, 102) # Dark Blue
        self.cell(0, 10, label, new_x="LMARGIN", new_y="NEXT", align='L')
        self.ln(2)

    def chapter_subtitle(self, label):
        self.set_font('Helvetica', 'B', 12)
        self.set_text_color(0, 0, 0)
        self.cell(0, 8, label, new_x="LMARGIN", new_y="NEXT", align='L')

    def body_text(self, text):
        self.set_font('Helvetica', '', 11)
        self.set_text_color(0, 0, 0)
        self.multi_cell(0, 6, text, new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def bullet_point(self, text):
        self.set_font('Helvetica', '', 11)
        self.set_text_color(0, 0, 0)
        # Indent and add bullet
        self.set_x(self.l_margin + 5)
        self.multi_cell(0, 6, f"\x95 {text}", new_x="LMARGIN", new_y="NEXT") 
        self.ln(1)

def parse_markdown_to_pdf(content: str, filename: str):
    """
    Parses a markdown string and generates a PDF file.
    """
    pdf = PDFResume()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Pre-process content to handle bold text (simple removal of ** for clean PDF)
    # A full markdown parser is complex, this simple parser handles headers and lists.
    
    lines = content.split('\n')
    
    
    for line in lines:
        # Robust sanitization: replace known smart chars, then strip any other non-latin-1 chars
        line = line.replace(u"\u2018", "'").replace(u"\u2019", "'").replace(u"\u201c", '"').replace(u"\u201d", '"')
        line = line.replace(u"\u2013", "-").replace(u"\u2014", "-")
        # unknown chars are ignored to prevent crash
        line = line.encode('latin-1', 'ignore').decode('latin-1')

        line = line.strip()
        if not line:
            pdf.ln(2)
            continue
            
        # Headers
        if line.startswith('# '):
            pdf.chapter_title(line[2:].strip())
        elif line.startswith('## '):
            pdf.chapter_title(line[3:].strip()) # Treat H2 same as H1 for resume sections usually
        elif line.startswith('### '):
            pdf.chapter_subtitle(line[4:].strip())
            
        # List items
        elif line.startswith('- ') or line.startswith('* '):
            clean_line = line[2:].strip().replace('**', '') # Remove bold markers for cleaner text
            pdf.bullet_point(clean_line)
            
        # Regular text
        else:
            # Check for simple "Key: Value" lines which act like subtitles
            if re.match(r'^[\w\s]+:', line):
                 pdf.set_font('Helvetica', 'B', 11)
                 pdf.multi_cell(0, 6, line.replace('**', ''), new_x="LMARGIN", new_y="NEXT")
                 pdf.ln(1)
            else:
                pdf.body_text(line.replace('**', ''))

    pdf.output(filename)
    return filename
