import sys
import re
# Ensure UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

line = "être énervé, irrité lireguoze âle לעַ זֹגּר ְלִ"
# Characters involved:
# \u05DC (Lamed)
# \u05E2 (Ayin)
# \u05B7 (Patah)
# \u0020 (Space)
# \u05D6 (Zayin)
# \u05B9 (Holam)
# \uFB32 (Gimel Dagesh)
# \u05E8 (Resh)

# Original Regex
regex_orig = r'[\u0590-\u05FF\uFB1D-\uFB4F\s"]+'
matches_orig = re.findall(regex_orig, line)
print(f"Original Matches: {matches_orig}")

# Check if FB32 is matched
gimel = '\uFB32'
match_gimel = re.match(r'[\uFB1D-\uFB4F]', gimel)
print(f"Matches FB32 directly: {match_gimel}")

# Try regex with lower case hex or different structure
regex_fix = r'[\u0590-\u05FF\ufb1d-\ufb4f\s"]+'
matches_fix = re.findall(regex_fix, line)
print(f"Fix Matches: {matches_fix}")

# Try separating
regex_sep = r'([\u0590-\u05FF]+|[\uFB1D-\uFB4F]+|\s+)+'
matches_sep = re.findall(regex_sep, line)
# Note: findall with groups returns tuples. not ideal for extraction.
