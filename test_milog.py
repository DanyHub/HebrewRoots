import requests
from bs4 import BeautifulSoup
import sys

# Ensure UTF-8
sys.stdout.reconfigure(encoding='utf-8')

def test_milog(word):
    url = f"https://milog.co.il/{word}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    with open("milog_log.txt", "w", encoding="utf-8") as f:
        f.write(f"Fetching {url}\n")
        try:
            r = requests.get(url, headers=headers)
            f.write(f"Status: {r.status_code}\n")
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, 'html.parser')
                f.write(f"Title: {soup.title.string}\n")
                
                # Milog definitions
                # <div class="sr_e_txt">...</div>
                defs = soup.find_all('div', class_='sr_e_txt')
                f.write(f"Found {len(defs)} definitions.\n")
                for d in defs[:3]:
                    f.write(f"Def: {d.get_text(strip=True)}\n")
            else:
                f.write("Failed status code.\n")
                
        except Exception as e:
            f.write(f"Error: {e}\n")

if __name__ == "__main__":
    test_milog("להתחיל")
