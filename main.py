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

def format_message(root_text, words):
    """
    Formats the daily shoresh message for Telegram using Gemini data.
    """
    lines = [f"Daily Shoresh: *{root_text}*\n"]
    
    if not words:
        lines.append("(No words found for this root today. Check back tomorrow!)")
        return "\n".join(lines)

    for i, word in enumerate(words):
        # Gemini Structure:
        # {
        #   "hebrew": "...",
        #   "transliteration": "...",
        #   "type": "...",
        #   "translation": "...",
        #   "example": {"hebrew": "...", "english": "..."}
        # }
        
        hebrew = word.get('hebrew', 'N/A')
        translit = word.get('transliteration', '')
        pos = word.get('type', 'N/A')
        definition = word.get('translation', 'N/A')
        
        # Word Header
        lines.append(f"*{hebrew}* ({translit})")
        
        # Part of Speech
        lines.append(f"🏷️ Part of Speech: {pos}")
        
        # Definition
        lines.append(f"📖 Definition:\n{definition}")
        
        # Example
        ex = word.get('example')
        if ex and isinstance(ex, dict):
             lines.append(f"🗣️ Example:")
             lines.append(f"🇮🇱 {ex.get('hebrew', '')}")
             lines.append(f"🇬🇧 {ex.get('english', '')}")
        
        lines.append("\n" + "-"*15 + "\n")
        
        if i >= 15: # Limit message length
            lines.append("... (Truncated)")
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
    
    print(f"Found Root in PDF: {root}")
    
    # Gemini Enrichment
    print("Generating content with Gemini...")
    words = enricher.get_words_for_root(root)
    
    if words is None:
        error_msg = ("⚠️ **Configuration Error** ⚠️\n\n"
                     "The Gemini API Key is missing or invalid.\n"
                     "Please check your GitHub Secrets and ensure `GEMINI_API_KEY` is set correctly.")
        print(error_msg)
        send_telegram_message(error_msg)
        return

    if not words:
        print("Warning: Gemini returned no words (Empty List). Sending fallback message.")
    
    # Format Message
    msg = format_message(root, words)
    
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
