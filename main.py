import os
import sys
import requests
import argparse
from pdf_parser import PDFParser
from enricher import Enricher
from state_manager import StateManager

# Fix encoding
sys.stdout.reconfigure(encoding='utf-8')

# Configuration
PDF_PATH = "roots.pdf"
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "YOUR_TOKEN_HERE")
CHAT_ID = os.environ.get("CHAT_ID", "YOUR_CHAT_ID")

def send_telegram_message(message):
    if TELEGRAM_TOKEN == "YOUR_TOKEN_HERE":
        print("Telegram Token not set. Printing message instead:")
        print(message)
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print("Message sent successfully.")
    except Exception as e:
        print(f"Failed to send Telegram message: {e}")

def format_message(root, words, is_enriched=False):
    lines = [f"Daily Shoresh: *{root}*"]
    if is_enriched:
        lines.append("(Enriched with external sources)")
    
    lines.append("")
    
    for i, word in enumerate(words):
        # Determine highlighting
        # User asked for color, we use Bold as fallback.
        # We need to identify the root in the Hebrew word?
        # That's hard to do programmatically without complex morphology.
        # So we just bold the whole Hebrew word for now or just the label.
        
        # Word Structure: 
        # Hebrew: <word>
        # Description: <desc>
        # Transliteration: <trans> (if available, mostly for enriched)
        # Translation: <trans> (from enricher/pdf)
        
        hebrew = word.get('hebrew_vocalized') or word.get('hebrew', '')
        # Clean latin/desc
        latin = word.get('latin', '') or word.get('translation', '')
        desc = word.get('description', '') 
        # Note: In PDF parser, 'latin' == 'description'.
        # In Enricher: 'translation' is used.
        
        translit = word.get('transliteration', '')
        type_info = word.get('type', '')
        
        lines.append(f"*{hebrew}*")
        if type_info:
             lines.append(f"Description of type: {type_info}")
        if translit:
            lines.append(f"Transliteration: {translit}")
        
        # Translation is often mixed with Latin in PDF, or separate in Enricher
        translation = latin
        if not translation and 'translation' in word:
            translation = word['translation']
            
        lines.append(f"Translation: {translation}")
        lines.append("")
        
        if i >= 15: # Limit message length
            lines.append("... (Trunkated)")
            break
            
    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--preview", action="store_true", help="Preview only, don't update state")
    args = parser.parse_args()

    # Initialize
    pdf_parser = PDFParser(PDF_PATH)
    enricher = Enricher()
    state_manager = StateManager()

    # Find next page
    last_page = state_manager.get_last_page()
    next_page = last_page + 1
    
    # Try finding a valid root on next pages
    max_pages = 262 # From analysis
    found_data = None
    
    # Heuristic: limit search to next 10 pages to avoid infinite loop if EOF
    for page_num in range(next_page, min(next_page + 10, max_pages)):
        print(f"Checking page {page_num + 1}...")
        data = pdf_parser.parse_page(page_num)
        
        if data and data['root']:
            # Check if root used (duplicate check)
            if state_manager.is_root_used(data['root']):
                print(f"Root {data['root']} already used. Skipping.")
                continue
            
            found_data = data
            current_page = page_num
            break
    
    if not found_data:
        print("No new roots found.")
        return

    root = found_data['root']
    words = found_data['words']
    
    # print(f"Found Root: {root} with {len(words)} words.") 
    print(f"Found Root (length: {len(words)} words)")
    
    is_enriched = False
    if len(words) < 10:
        print("Fewer than 10 words. Enriching...")
        extra_words = enricher.get_words_for_root(root)
        # Append extra words
        # Need to normalize keys
        normalized_extra = []
        for w in extra_words:
            normalized_extra.append({
                'hebrew_vocalized': w.get('hebrew'),
                'latin': w.get('translation'),
                'type': w.get('type'),
                'transliteration': w.get('transliteration')
            })
        
        words.extend(normalized_extra)
        is_enriched = True

    # Format Message
    msg = format_message(root, words, is_enriched)
    
    # Write message to file for verification
    with open("message_preview.md", "w", encoding="utf-8") as f:
        f.write(msg)
    
    # Print generic success
    print(f"Generated message for root {root}. See message_preview.md")
    
    # Send
    send_telegram_message(msg)
    
    # Update State
    if not args.preview:
        state_manager.mark_used(root, current_page)
        print("State updated.")

if __name__ == "__main__":
    main()
