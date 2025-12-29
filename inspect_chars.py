import pdfplumber
import sys

# Ensure UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

def inspect_page(pdf_path, page_num):
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[page_num]
        text = page.extract_text()
        lines = text.split('\n')
        for line in lines:
            if "lireguoze" in line: # Target the problematic line
                print(f"Line content: {line}")
                print("Characters:")
                for char in line:
                    print(f"{char}: U+{ord(char):04X}")

if __name__ == "__main__":
    inspect_page("roots.pdf", 1) # Page 2 is index 1
