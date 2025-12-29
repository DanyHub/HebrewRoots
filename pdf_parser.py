import pdfplumber
import re

class PDFParser:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path

    def reverse_hebrew(self, text):
        import unicodedata
        clusters = []
        current_cluster = ""
        for char in text:
            if current_cluster and unicodedata.combining(char):
                current_cluster += char
            else:
                if current_cluster:
                    clusters.append(current_cluster)
                current_cluster = char
        if current_cluster:
            clusters.append(current_cluster)
        
        # Reverse the clusters
        return "".join(reversed(clusters))

    def _is_hebrew(self, char):
        return '\u0590' <= char <= '\u05FF'

    def parse_page(self, page_num):
        """Parses a specific page (0-indexed) and returns the root and words."""
        results = {
            "root": "",
            "words": []
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
                root_found = False
                for i, line in enumerate(lines):
                    if "Racine" in line:
                        if i + 1 < len(lines):
                            raw_root = lines[i+1].strip()
                            # Check if root line contains Hebrew
                            if any(self._is_hebrew(c) for c in raw_root):
                                results["root"] = self.reverse_hebrew(raw_root)
                                root_found = True
                        break
                
                if not root_found:
                    # Fallback: maybe just look for the first Hebrew text?
                    # But for now, rely on "Racine".
                    return None

                # Extract Words with Grouping
                # Group lines into entries
                current_entry = {}
                
                for line in lines:
                    line = line.strip()
                    # Skip metadata
                    if "Racine" in line or (root_found and line == results["root"][::-1]):
                         continue
                    if "Serge Frydman" in line:
                        continue
                    if not line:
                        continue
                    
                    # Logic:
                    # 1. Contains Latin + Hebrew: Start of new word (usually).
                    # 2. Contains Hebrew Only: continuation (Plain Hebrew).
                    # 3. Contains Latin Only: definition extension.

                    has_hebrew = any(self._is_hebrew(c) for c in line)
                    latin_part = re.sub(r'[\u0590-\u05FF\s"\']+', ' ', re.sub(r'[\u0590-\u05FF]+', '', line)).strip()
                    
                    # Extract raw Hebrew parts for reversal
                    hebrew_matches = re.findall(r'[\u0590-\u05FF\u0591-\u05c7\s"]+', line)
                    # Note: \u0591-\u05c7 are Nikkud (Vowels) + others.
                    
                    full_hebrew_str = ""
                    if has_hebrew:
                        # Join matches. Visual order usually implies distinct blocks.
                        # "ète תאֶ" -> Hebrew is at end.
                        # Simple join and reverse per line seems to have worked for order, key is graphemes.
                        # We just extract the 'Hebrew substring' from the line.
                        # We assume the Hebrew part is contiguous or we just join them.
                        raw_hebw = "".join(match for match in hebrew_matches if any(self._is_hebrew(c) for c in match))
                        full_hebrew_str = self.reverse_hebrew(raw_hebw.strip())

                    if has_hebrew and latin_part:
                        # New Entry
                        if current_entry:
                            results["words"].append(current_entry)
                        current_entry = {
                            "hebrew_vocalized": full_hebrew_str,
                            "hebrew_plain": "", 
                            "latin": latin_part,
                            "description": latin_part
                        }
                    elif has_hebrew and not latin_part:
                        # Likely the Plain Hebrew version of the previous entry
                        # IGNORE if it's just a single char or noise (like stray vowel)
                        if len(full_hebrew_str) <= 1:
                            continue
                            
                        if current_entry:
                             # Don't overwrite if we already have a long/good string
                             if len(current_entry["hebrew_plain"]) > len(full_hebrew_str):
                                 continue
                             current_entry["hebrew_plain"] = full_hebrew_str
                    elif not has_hebrew and latin_part:
                        # Latin only - append to description
                        if current_entry:
                            current_entry["description"] += " " + latin_part
                            current_entry["latin"] += " " + latin_part

                if current_entry:
                    results["words"].append(current_entry)

        except Exception as e:
            # write error to file to see it
            with open("parse_error.txt", "w") as f:
                f.write(str(e))
            return None
            
        return results

if __name__ == "__main__":
    parser = PDFParser("roots.pdf")
    data = parser.parse_page(0) # Page 1
    import json
    with open("debug_output.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
