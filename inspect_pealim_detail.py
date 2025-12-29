import requests
from bs4 import BeautifulSoup

def inspect_pealim_page(url):
    print(f"Fetching {url}")
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            with open("inspection_log.txt", "w", encoding="utf-8") as f:
                f.write(f"Title: {soup.title.string}\n")
                
                text = soup.get_text()
                if "Example" in text:
                    f.write("Found 'Example' string in text.\n")
                else:
                     f.write("'Example' string not found.\n")
                     
                for h in soup.find_all(['h2', 'h3', 'h4']):
                     f.write(f"Heading: {h.get_text(strip=True)}\n")

            # Dump a bit of html
            with open("pealim_detail.html", "w", encoding="utf-8") as f:
                f.write(soup.prettify())
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # URL for 'Lahafoch' from previous search
    inspect_pealim_page("https://www.pealim.com/dict/468-lahafoch/")
