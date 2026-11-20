import re
from collections import Counter

text = open("seed.py", encoding="utf-8").read()
keys = re.findall(r'^\s{4}"([^"]+)":\s*\[', text, re.M)
print([k for k, c in Counter(keys).items() if c > 1])