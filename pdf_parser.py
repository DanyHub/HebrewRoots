import pdfplumber
import re

class PDFParser:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path

    def reverse_hebrew(self, text):
        import unicodedata
        # Remove spaces between diacritics and letters if they exist?
        # In the issue "מַ  ְהךָ", we see spaces. 
        # Clean up spaces that might be artifacts between combining marks.
        # But first, let's just reverse blindly and see if we can re-order.
        # Actually, simpler approach for "Visual" Hebrew with diacritics:
        # If the input is [LastChar] [Mark] [PrevChar] [Mark]...
        # We want [FirstChar] [Mark] [NextChar] [Mark]...
        
        # 1. Reverse the string completely (chars).
        # 2. But this puts marks *before* their base if they were *after* in visual? 
        #    Note: in visual LTR, if I type "Shalom" RTL, I see "molahS".
        #    If I have "Shin+Qamats", does it become "Qamats+Shin" (visual)? 
        #    Usually PDF visual text is: [Shin] [Qamats] -> (extracts as) -> [Shin] [Qamats] if simple.
        #    If reversed: [Qamats] [Shin]. This renders Qamats on the char *before* Shin (or dotted circle).
        #    So we need [Shin] [Qamats].
        #    This implies we should NOT reverse the [Char+Mark] cluster.
        #    We should reverse the ORDER of the clusters.
        
        # My previous code did: Identify clusters, then reverse list of clusters.
        # output: [Cluster3] [Cluster2] [Cluster1].
        # Cluster = Base + Marks.
        # This assumes the input `text` was [Cluster1] [Cluster2] [Cluster3] in REVERSE order?
        # Input: `text` from pdfplumber. 
        # If PDF is Visual LTR: "txeT werbeH"
        # Cluster1 (Hebrew Start) is at the end of the string.
        # So yes, reversing the list of clusters is correct.
        
        # The issue "מַ  ְהךָ" has spaces. 
        # Input likely: `Kaf` `Space` `Qamats` ...
        # My cluster logic: `current_cluster` = `Kaf`. Next char `Space`.
        # `Space` is NOT combining. So `Kaf` is flushed.
        # Next `Space`. Flushed.
        # Next `Qamats` (Combining). Attached to... `Space`? Or new cluster?
        # `unicodedata.combining(' ')` is 0.
        # So `Qamats` starts new cluster (on dotted circle).
        
        # FIX: We need to ignore/merge spaces that separate a base and a mark.
        
        clusters = []
        current_cluster = ""
        
        text = text.strip()
        
        # Pass 1: Remove spaces between Base and Mark?
        # Regex: [Base] [Space] [Mark] -> [Base] [Mark]
        # But we need to know what is Base and Mark.
        
        # Let's iterate.
        for char in text:
            is_combining = unicodedata.combining(char)
            is_space = char.isspace()
            
            if is_combining:
                # If current cluster ends with space, remove it?
                if current_cluster and current_cluster[-1].isspace():
                    current_cluster = current_cluster.rstrip()
                current_cluster += char
            else:
                if current_cluster:
                     clusters.append(current_cluster)
                current_cluster = char
                
        if current_cluster:
            clusters.append(current_cluster)
        
        # Filter out purely whitespace clusters if they are noise?
        # clusters = [c for c in clusters if c.strip()] 
        
        # Reverse
        reversed_text = "".join(reversed(clusters))
        
        # Post-processing: Collapse multiple spaces
        reversed_text = re.sub(r'\s{2,}', ' ', reversed_text)
        return reversed_text.strip()

    def _is_hebrew(self, char):
        # Include Presentation Forms A and B (FB1D-FB4F, FE70-FEFF check?)
        # FB1D-FB4F is Hebrew.
        # 0590-05FF is Standard.
        code = ord(char)
        return (0x0590 <= code <= 0x05FF) or (0xFB1D <= code <= 0xFB4F)

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
                    
                    # Regex to remove Hebrew chars (Standard + Presentation Forms + Nikkud)
                    # Range: \u0590-\u05FF and \uFB1D-\uFB4F
                    latin_part = re.sub(r'[\u0590-\u05FF\uFB1D-\uFB4F]+', '', line).strip()
                    # Also cleanup stray quotes/punctuation acting as Hebrew leftovers
                    latin_part = re.sub(r'\s+', ' ', latin_part)
                    
                    # Extract raw Hebrew parts
                    # Capture Standard, Presentation, and Nikkud (0591-05C7 are inside 0590-05FF)
                    hebrew_matches = re.findall(r'[\u0590-\u05FF\uFB1D-\uFB4F\s"]+', line)
                    
                    full_hebrew_str = ""
                    if has_hebrew:
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
