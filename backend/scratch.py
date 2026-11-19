import re

with open("data/jpn-eng.txt", encoding="utf-8") as f:
    rows = [l.split("\t")[:2] for l in f]

pattern = re.compile(r"\bgive (?:\w+ )?away\b", re.I)
hits = [r for r in rows if pattern.search(r[0])]
print("give (it) away:", len(hits))
for h in hits[:10]:
    print(h)

other = re.compile(r"\b(gave|giving|gives|given) (?:\w+ )?away\b", re.I)
print("other forms:", sum(1 for r in rows if other.search(r[0])))