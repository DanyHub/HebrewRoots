import requests
from bs4 import BeautifulSoup

def test_pealim(root):
    # Root format: ה.פ.כ -> need to strip dots for some searches or keep them?
    # Pealim search usually works with letters.
    query = root.replace(".", "")
    url = f"https://www.pealim.com/search/?q={query}"
    with open("scrape_result.txt", "w", encoding="utf-8") as f:
        f.write(f"Testing URL: {url}\n")
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            r = requests.get(url, headers=headers)
            f.write(f"Status: {r.status_code}\n")
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, 'html.parser')
                f.write(f"Title: {soup.title.string}\n")
                with open("pealim.html", "w", encoding="utf-8") as html_f:
                    html_f.write(soup.prettify())
        except Exception as e:
            f.write(f"Error: {e}\n")

if __name__ == "__main__":
    test_pealim("ה.פ.כ")
