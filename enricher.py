import requests
from bs4 import BeautifulSoup
import re

class Enricher:
    def __init__(self):
        self.base_url = "https://www.pealim.com/search/"
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

    def get_words_for_root(self, root):
        """
        Fetches words for a given root from Pealim.
        Root format expected: "H.P.K" or "ה.פ.כ"
        """
        # Clean root for search: "הפכ"
        query = re.sub(r'[\.\s]', '', root)
        
        url = f"{self.base_url}?q={query}"
        results = []
        
        try:
            with open("enrich_log.txt", "a", encoding="utf-8") as log:
                log.write(f"Fetching {url}\n")
            r = requests.get(url, headers=self.headers)
            if r.status_code != 200:
                with open("enrich_log.txt", "a", encoding="utf-8") as log:
                    log.write(f"Failed to fetch Pealim: {r.status_code}\n")
                return []
            
            soup = BeautifulSoup(r.text, 'html.parser')
            
            # Find all result entries
            entries = soup.find_all('div', class_='verb-search-result')
            
            for entry in entries:
                item = {}
                
                # Lemma (Hebrew Word)
                lemma_div = entry.find('div', class_='verb-search-lemma')
                if lemma_div:
                    menukad_span = lemma_div.find('span', class_='menukad')
                    if menukad_span:
                        item['hebrew'] = menukad_span.get_text(strip=True)
                
                # Meaning
                meaning_div = entry.find('div', class_='verb-search-meaning')
                if meaning_div:
                    item['translation'] = meaning_div.get_text(strip=True)
                
                # Type / POS
                binyan_div = entry.find('div', class_='verb-search-binyan')
                if binyan_div:
                     # Clean up text: "Part of speech: verb – PA'AL" -> "verb – PA'AL"
                    pos_text = binyan_div.get_text(separator=' ', strip=True)
                    item['type'] = pos_text.replace('Part of speech:', '').strip()

                # Transcription (Attempt to find it)
                # Usually in the lemma link or detailed view, but in search list it might not be explicit for the Lemma?
                # In the HTML sample:
                # <div class="vf-search-result"> has transcription.
                # The Lemma itself (verb-search-lemma) doesn't show transcription in the HTML I saw (lines 325-335).
                # But `vf-search-result` (forms) has it.
                # I'll look for any transcription class inside the entry.
                transcription_span = entry.find('span', class_='transcription')
                if transcription_span:
                     item['transliteration'] = transcription_span.get_text(strip=True)
                else:
                    item['transliteration'] = "" # Missing in search view for Lemma sometimes

                if 'hebrew' in item:
                    results.append(item)
                    
        except Exception as e:
            print(f"Error enriching: {e}")
            
        return results

if __name__ == "__main__":
    enricher = Enricher()
    words = enricher.get_words_for_root("ה.פ.כ")
    import json
    with open("enrich_debug.json", "w", encoding="utf-8") as f:
        json.dump(words, f, indent=2, ensure_ascii=False)
