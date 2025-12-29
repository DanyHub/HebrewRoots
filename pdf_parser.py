import pdfplumber
import re

class PDFParser:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path

    def reverse_hebrew(self, text):
        # Still need basic reversal for the Root itself if it's visually reversed in PDF
        return text[::-1]

    def _is_hebrew(self, char):
        return '\u0590' <= char <= '\u05FF'

    def parse_page(self, page_num):
        """Parses a specific page and returns *only* the root."""
        results = {
            "root": "",
            "words": [] # Kept empty by design, logic moved to Enricher
        }
        
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                if page_num >= len(pdf.pages):
                    return None
                
                page = pdf.pages[page_num]
                text = page.extract_text()
                
                if not text:
                    return None

                lines = text.split('\n')
                
                # Check for Root
                # Heuristic: Find line with "Racine" then next line is Root
                for i, line in enumerate(lines):
                    if "Racine" in line:
                        if i + 1 < len(lines):
                            raw_root = lines[i+1].strip()
                            if any(self._is_hebrew(c) for c in raw_root):
                                # Reverse the root string
                                results["root"] = self.reverse_hebrew(raw_root)
                        break
        except Exception as e:
            print(f"Error parsing PDF: {e}")
            return None
            
        return results
