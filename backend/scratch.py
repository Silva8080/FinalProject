import sqlite3
conn = sqlite3.connect("database/dictionary.db")
for w in ["russian", "russian person", "japanese", "english"]:
    print(w, conn.execute("SELECT type, meanings FROM senses WHERE word = ?", (w,)).fetchall())