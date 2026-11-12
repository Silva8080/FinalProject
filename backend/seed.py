import json
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "database" / "dictionary.db"

# Hand-written entries. They REPLACE whatever the JMdict import made for that word.
# Words must already be normalized (lowercase, no punctuation except ').
# Format: word -> list of (type, [meanings]), best sense first.
ENTRIES = {
    "give up": [("phrasal verb", ["諦める", "やめる", "降参する"])],
    "hang out": [("phrasal verb", ["遊ぶ", "たむろする", "一緒に過ごす"])],
    "gonna": [("contraction", ["〜するつもり", "〜しようとしている"])],
    "wanna": [("contraction", ["〜したい"])],
    "what's up": [("expression", ["やあ", "どうしたの", "調子はどう"])],
    "no way": [("expression", ["まさか", "マジで！？", "絶対だめ"])],
    "run": [
        ("verb", ["走る", "運営する", "流れる"]),
        ("noun", ["ラン", "走ること", "連続"]),
    ],
}


def main():
    conn = sqlite3.connect(DB_PATH)
    # Make sure the table exists (normally import_jmdict.py created it)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS senses (
            id       INTEGER PRIMARY KEY,
            word     TEXT NOT NULL,
            type     TEXT NOT NULL,
            meanings TEXT NOT NULL,
            position INTEGER NOT NULL
        )
        """
    )
    conn.execute("CREATE INDEX IF NOT EXISTS idx_senses_word ON senses(word)")

    for word, senses in ENTRIES.items():
        # Delete the automatic rows first, then insert ours
        conn.execute("DELETE FROM senses WHERE word = ?", (word,))
        for position, (word_type, meanings) in enumerate(senses):
            conn.execute(
                "INSERT INTO senses (word, type, meanings, position) VALUES (?, ?, ?, ?)",
                (word, word_type, json.dumps(meanings, ensure_ascii=False), position),
            )

    conn.commit()
    conn.close()
    print(f"Seeded {len(ENTRIES)} words")


if __name__ == "__main__":
    main()