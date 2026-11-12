import sqlite3
from pathlib import Path

from text_utils import normalize

# Paths to the Tatoeba file and the database
# Tatoebaファイルとデータベースのパス
BASE = Path(__file__).parent
TXT_PATH = BASE / "data" / "jpn-eng.txt"
DB_PATH = BASE / "database" / "dictionary.db"

# Examples kept per word / 1単語あたりに残す例文の数
MAX_PER_WORD = 3
# Skip sentences longer than this (characters) / これより長い文は除外する（文字数）
MAX_CHARS = 80


def main():
    conn = sqlite3.connect(DB_PATH)

    # Only words that exist in the senses table
    # senses テーブルにある単語だけを対象にする
    known = {row[0] for row in conn.execute("SELECT DISTINCT word FROM senses")}

    # Read (English, Japanese) pairs; column 1 = English, column 2 = Japanese
    # (英語, 日本語) のペアを読み込む。1列目が英語、2列目が日本語
    pairs = []
    with open(TXT_PATH, encoding="utf-8") as f:
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 2 or len(parts[0]) > MAX_CHARS:
                continue
            pairs.append((parts[0], parts[1]))

    # Shortest sentences first: they make the best examples
    # 短い文を優先する（例文として読みやすいため）
    pairs.sort(key=lambda p: len(p[0]))

    counts = {}
    rows = []
    for english, japanese in pairs:
        tokens = normalize(english).split()
        seen = set()
        # Try 1-word, 2-word and 3-word phrases from the sentence
        # 文の中から1語・2語・3語のフレーズを調べる
        for n in (1, 2, 3):
            for i in range(len(tokens) - n + 1):
                key = " ".join(tokens[i:i + n])
                if key in known and key not in seen and counts.get(key, 0) < MAX_PER_WORD:
                    rows.append((key, english, japanese))
                    counts[key] = counts.get(key, 0) + 1
                    seen.add(key)

    # Rebuild the examples table from scratch
    # examples テーブルを作り直す
    conn.execute("DROP TABLE IF EXISTS examples")
    conn.execute(
        """
        CREATE TABLE examples (
            id       INTEGER PRIMARY KEY,
            word     TEXT NOT NULL,
            english  TEXT NOT NULL,
            japanese TEXT NOT NULL
        )
        """
    )
    conn.execute("CREATE INDEX idx_examples_word ON examples(word)")
    conn.executemany(
        "INSERT INTO examples (word, english, japanese) VALUES (?, ?, ?)", rows
    )
    conn.commit()
    conn.close()
    print(f"Saved {len(rows)} examples for {len(counts)} words")


if __name__ == "__main__":
    main()