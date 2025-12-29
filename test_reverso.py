import requests
from bs4 import BeautifulSoup

def test_reverso(word):
    url = f"https://context.reverso.net/translation/hebrew-english/{word}"
    with open("reverso_log.txt", "w", encoding="utf-8") as f:
        f.write(f"Fetching {url}\n")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    with open("reverso_log.txt", "w", encoding="utf-8") as f:
        f.write(f"Fetching {url}\n")
        try:
            r = requests.get(url, headers=headers)
            f.write(f"Status: {r.status_code}\n")
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, 'html.parser')
                f.write(f"Title: {soup.title.string}\n")
                
                # Examples usually in div class="example"
                examples = soup.find_all('div', class_='example')
                f.write(f"Found {len(examples)} examples.\n")
                
                for i, ex in enumerate(examples[:3]):
                    # Source (Hebrew)
                    src = ex.find('div', class_='src').get_text(strip=True) if ex.find('div', class_='src') else ""
                    # Target (English)
                    trg = ex.find('div', class_='trg').get_text(strip=True) if ex.find('div', class_='trg') else ""
                    
                    f.write(f"--- Ex {i} ---\n")
                    f.write(f"HE: {src}\n")
                    f.write(f"EN: {trg}\n")
            else:
                 f.write("Failed to fetch.\n")
        except Exception as e:
            f.write(f"Error: {e}\n")

if __name__ == "__main__":
    test_reverso("להתחיל")
