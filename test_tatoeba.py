import requests
from bs4 import BeautifulSoup
import sys

sys.stdout.reconfigure(encoding='utf-8')

def test_tatoeba(word):
    url = f"https://tatoeba.org/en/sentences/search?query={word}&from=heb&to=eng"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    with open("tatoeba_log.txt", "w", encoding="utf-8") as f:
        f.write(f"Fetching {url}\n")
        try:
            r = requests.get(url, headers=headers)
            f.write(f"Status: {r.status_code}\n")
            
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, 'html.parser')
                # Tatoeba structure: div class="sentence-and-translations"
                # text in div class="text"
                
                sentences = soup.find_all('div', class_='sentence-and-translations')
                f.write(f"Found {len(sentences)} sentences.\n")
                
                for i, s in enumerate(sentences[:3]):
                    # Hebrew
                    # The main sentence is usually the first "text" inside?
                    # structure: <div class="sentence ..."> <div class="text">...</div> </div>
                    
                    # Need to distinguish Source (Heb) and Translation (Eng).
                    # The search `from=heb` means results should be Hebrew.
                    
                    # Inspect first 'text'
                    heb_div = s.find('div', class_='text')
                    heb_text = heb_div.get_text(strip=True) if heb_div else "N/A"
                    
                    # Translations are in 'translations' div?
                    # structure varies.
                    # Simplified: Just grab text blocks.
                    f.write(f"--- {i} ---\n")
                    f.write(f"HE: {heb_text}\n")
                    
                    # Try to find english translation
                    # direct translations usually listed below
                    trans_divs = s.find_all('div', class_='translation')
                    for t in trans_divs:
                        t_text = t.find('div', class_='text').get_text(strip=True)
                        # Check lang? Tatoeba uses icons usually.
                        # For now just dump text.
                        f.write(f"TR: {t_text}\n")

        except Exception as e:
            f.write(f"Error: {e}\n")

if __name__ == "__main__":
    test_tatoeba("להתחיל")
