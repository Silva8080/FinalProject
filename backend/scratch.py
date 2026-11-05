import sqlite3

conn = sqlite3.connect("database/dictionary.db")
for word in ["racket", "dog", "run", "give up", "hello"]:
    print(word)
    for row in conn.execute(
        "SELECT type, meanings FROM senses WHERE word = ? ORDER BY position", (word,)
    ):
        print("   ", row)