import pdfplumber

def analyze_pdf(pdf_path):
    try:
        with pdfplumber.open(pdf_path) as pdf:
            with open("analysis_output.txt", "w", encoding="utf-8") as f:
                f.write(f"Total Pages: {len(pdf.pages)}\n")
                for i, page in enumerate(pdf.pages[:3]):
                    f.write(f"--- Page {i+1} ---\n")
                    text = page.extract_text()
                    if text:
                        f.write(text[:1000] + "\n")
                    else:
                        f.write("[No text found]\n")
                    f.write("----------------\n")
    except Exception as e:
        with open("analysis_output.txt", "w", encoding="utf-8") as f:
            f.write(f"Error reading PDF: {e}")

if __name__ == "__main__":
    analyze_pdf("roots.pdf")
