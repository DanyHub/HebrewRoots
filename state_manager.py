import json
import os

HISTORY_FILE = "history.json"

class StateManager:
    def __init__(self, file_path=HISTORY_FILE):
        self.file_path = file_path
        self.history = self._load_history()

    def _load_history(self):
        if not os.path.exists(self.file_path):
            return {"used_roots": [], "used_pages": []}
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {"used_roots": [], "used_pages": []}

    def save_history(self):
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(self.history, f, indent=2, ensure_ascii=False)

    def is_root_used(self, root):
        return root in self.history["used_roots"]

    def is_page_used(self, page_num):
        return page_num in self.history["used_pages"]

    def mark_used(self, root, page_num):
        if root and root not in self.history["used_roots"]:
            self.history["used_roots"].append(root)
        if page_num not in self.history["used_pages"]:
            self.history["used_pages"].append(page_num)
        self.save_history()

    def get_last_page(self):
        if not self.history["used_pages"]:
            return -1
        return max(self.history["used_pages"])
