import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "database" / "dictionary.db"

# Words must be stored already normalized (lowercase, no punctuation)
ENTRIES = [
    ("give up", "諦める", "phrasal verb"),
    ("hang out", "遊ぶ", "phrasal verb"),
    ("gonna", "〜するつもり", "contraction"),
    ("no way", "マジで！？", "idiom"),
    ("what's up", "よう", "idiom"),
    ("hello", "こんにちは", "interjection"),
]


def main():
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS entries (
            word    TEXT PRIMARY KEY,
            meaning TEXT NOT NULL,
            type    TEXT NOT NULL
        )
        """
    )
    conn.executemany(
        "INSERT OR REPLACE INTO entries (word, meaning, type) VALUES (?, ?, ?)",
        ENTRIES,
    )
    conn.commit()
    conn.close()
    print(f"Seeded {len(ENTRIES)} entries into {DB_PATH}")


if __name__ == "__main__":
    main()