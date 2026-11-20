import sqlite3

conn = sqlite3.connect("database/dictionary.db")
for w in ["have", "do", "see", "look", "turn", "run", "bring"]:
    senses = conn.execute("SELECT COUNT(*) FROM senses WHERE word = ?", (w,)).fetchone()[0]
    examples = conn.execute("SELECT COUNT(*) FROM examples WHERE word = ?", (w,)).fetchone()[0]
    print(f"{w}: {senses} senses, {examples} examples")