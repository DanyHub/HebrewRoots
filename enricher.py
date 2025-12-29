import os
import google.generativeai as genai
import json
import re

class Enricher:
    def __init__(self):
        # API Key should be in environment variable
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            # Fallback for local testing if not set? 
            # Or raise error. For now, bot might fail if not set, which is expected.
            print("WARNING: GEMINI_API_KEY not set.")
            self.model = None
        else:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash-exp')

    def get_words_for_root(self, root):
        """
        Generates structured data for a given Hebrew root using Gemini.
        Returns a list of dictionaries.
        """
        if not self.model:
            return []
            
        # Clean root
        clean_root = re.sub(r'[\.\s]', '', root)
        
        prompt = f"""
        You are a Hebrew expert. I have the Hebrew root "{root}" (shoresh).
        Please generate 10 distinct Hebrew words derived from this root.
        
        For each word, provide:
        1. "hebrew": The word in Hebrew with Nikud (vocalized).
        2. "transliteration": Standard English transliteration.
        3. "type": Part of speech (e.g., Noun, Verb - Pa'al, Adjective).
        4. "translation": A clear English definition/translation.
        5. "example": A dictionary object containing:
            - "hebrew": A short, natural example sentence in Hebrew using the word.
            - "english": The English translation of the sentence.
            
        Return the result as a raw JSON list of objects. Do not wrap in markdown or code blocks.
        """
        
        try:
            response = self.model.generate_content(prompt)
            # Strip potential markdown formatting if Gemini adds it (```json ... ```)
            text = response.text
            if text.startswith("```"):
                text = text.split("\n", 1)[1]
                if text.endswith("```"):
                    text = text.rsplit("\n", 1)[0]
                # Also handle ```json specifically
                text = text.replace("```json", "").replace("```", "").strip()
            
            data = json.loads(text)
            return data
            
        except Exception as e:
            print(f"Gemini Error: {e}")
            # Log full error for debugging
            with open("enrich_log.txt", "a", encoding="utf-8") as f:
                f.write(f"Gemini Request Failed for {root}: {e}\n")
            return []

if __name__ == "__main__":
    # Test run (requires env var set via CLI on run)
    enricher = Enricher()
    # You can set the key in the terminal before running: set GEMINI_API_KEY=...
    words = enricher.get_words_for_root("ה.פ.כ")
    with open("enrich_debug.json", "w", encoding="utf-8") as f:
        json.dump(words, f, indent=2, ensure_ascii=False)
