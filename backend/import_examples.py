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
# Preferred sentence length: short ones are mostly imperatives
# 好ましい文の長さ（短い文は命令文ばかりになるため）
TARGET_CHARS = 40

# Words that turn a verb into a phrasal verb ("give" + "up")
# 動詞を句動詞に変える小さな語（give + up など）
PARTICLES = {
    "up", "out", "in", "off", "on", "away", "back", "down",
    "over", "around", "along", "through", "into", "about",
}
# Pronouns that can sit between verb and particle ("give it up")
# 動詞と小さな語の間に入る代名詞（give it up など）
PRONOUNS = {"it", "him", "her", "them", "me", "you", "us", "this", "that"}


def main():
    conn = sqlite3.connect(DB_PATH)

    # All known words and phrases / 既知の単語とフレーズ
    known = {row[0] for row in conn.execute("SELECT DISTINCT word FROM senses")}

    # Single words that are verbs (only these get the particle check)
    # 動詞の単語（これらだけ小さな語のチェックをする）
    verbs = {
        row[0]
        for row in conn.execute(
            "SELECT DISTINCT word FROM senses WHERE type = 'verb'"
        )
    }

    # Read (English, Japanese) pairs / (英語, 日本語) のペアを読み込む
    pairs = []
    with open(TXT_PATH, encoding="utf-8") as f:
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 2 or len(parts[0]) > MAX_CHARS:
                continue
            pairs.append((parts[0], parts[1]))

    # Prefer sentences close to TARGET_CHARS
    # TARGET_CHARS に近い長さの文を優先する
    pairs.sort(key=lambda p: abs(len(p[0]) - TARGET_CHARS))

    counts = {}
    rows = []
    seen_pairs = set()   # (word, English) already saved / 保存済みの英文
    seen_ja = set()      # (word, Japanese) already saved / 保存済みの日本語訳
    for english, japanese in pairs:
        tokens = normalize(english).split()
        i = 0
        while i < len(tokens):
            # Longest known phrase starting at position i (4, 3, 2, then 1 words)
            # 位置 i から始まる最も長い既知のフレーズを選ぶ
            matched = None

            # Separable phrasal verb: "give it away" -> "give away"
            # 分離できる句動詞: "give it away" -> "give away"
            if i + 2 < len(tokens) and tokens[i + 1] in PRONOUNS and tokens[i + 2] in PARTICLES:
                separable = tokens[i] + " " + tokens[i + 2]
                if separable in known:
                    matched = (separable, 3)  # uses 3 words in the sentence

            if matched is None:
                for n in (4, 3, 2, 1):
                    chunk = tokens[i:i + n]
                    if len(chunk) == n and " ".join(chunk) in known:
                        matched = (" ".join(chunk), n)
                        break

            if matched is None:
                i += 1
                continue

            key, n = matched

            # A single verb followed by a particle is probably a phrasal verb
            # 単独の動詞の後ろに小さな語が続く場合は句動詞の可能性が高いので除外する
            if n == 1 and key in verbs:
                nxt = tokens[i + 1] if i + 1 < len(tokens) else ""
                nxt2 = tokens[i + 2] if i + 2 < len(tokens) else ""
                if nxt in PARTICLES or (nxt in PRONOUNS and nxt2 in PARTICLES):
                    i += 1
                    continue

            if (
                counts.get(key, 0) < MAX_PER_WORD
                and (key, english) not in seen_pairs
                and (key, japanese) not in seen_ja
            ):
                rows.append((key, english, japanese))
                seen_pairs.add((key, english))
                seen_ja.add((key, japanese))
                counts[key] = counts.get(key, 0) + 1
            i += n   # skip the words we just used / 使った語はスキップする

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