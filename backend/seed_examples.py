import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "database" / "dictionary.db"

# Hand-picked examples. They REPLACE the automatic ones for that word.
# 手書きの例文。その単語の自動生成の例文を置き換える。
# Format: word -> list of (English, Japanese)
EXAMPLES = {
    "get": [
        ("I got a new phone yesterday.", "昨日、新しいスマホを手に入れた。"),
        ("It's getting cold.", "寒くなってきた。"),
        ("What time did you get home?", "何時に家に着いたの？"),
        ("I don't get it.", "意味がわからない。"),
    ],
    "make over": [
        ("She got a makeover at the salon.", "彼女はサロンでイメチェンした。"),
        ("They made over the old kitchen.", "彼らは古いキッチンを改装した。"),
        ("He made over the house to his son.", "彼は家を息子に譲渡した。"),
    ],
    "break down": [
        ("My car broke down on the highway.", "高速道路で車が故障した。"),
        ("She broke down in tears.", "彼女は泣き崩れた。"),
        ("Let's break down the cost.", "費用を内訳にして考えよう。"),
    ],
    "give us a break": [
        ("Oh, give us a break!", "もう勘弁してよ！"),
        ("Come on, give us a break.", "頼むから、大目に見てよ。"),
        ("Give us a break, we've been working all day.", "勘弁してよ、一日中働いてたんだから。"),
    ],
    "make sense": [
        ("That doesn't make sense.", "それは意味が通らない。"),
        ("Her explanation makes sense to me.", "彼女の説明は私には筋が通っている。"),
        ("It makes sense to leave early.", "早めに出るのが理にかなっている。"),
    ],
    "give out": [
        ("They gave out free tickets.", "彼らは無料チケットを配った。"),
        ("My voice gave out.", "声が出なくなった。"),
        ("The teacher gave out the tests.", "先生はテストを配った。"),
    ],
    "bring back": [
        ("This song brings back memories.", "この曲は思い出がよみがえる。"),
        ("Please bring back my book.", "私の本を返しに持ってきてね。"),
        ("They want to bring back the old rules.", "彼らは古いルールを復活させたい。"),
    ],
    "pull out": [
        ("He pulled out his wallet.", "彼は財布を取り出した。"),
        ("The car pulled out of the garage.", "車がガレージから出ていった。"),
        ("They pulled out of the deal.", "彼らは取引から手を引いた。"),
    ],
    "break": [
        ("He broke the window.", "彼は窓を割った。"),
        ("Let's take a break.", "休憩しよう。"),
        ("She broke her promise.", "彼女は約束を破った。"),
    ],
    "give away": [
        ("They are giving away free samples.", "彼らは無料サンプルを配っている。"),
        ("Don't give away the ending.", "結末をばらさないでね。"),
        ("I gave away my old clothes.", "古い服を人にあげた。"),
    ],
}


def main():
    conn = sqlite3.connect(DB_PATH)
    for word, pairs in EXAMPLES.items():
        conn.execute("DELETE FROM examples WHERE word = ?", (word,))
        conn.executemany(
            "INSERT INTO examples (word, english, japanese) VALUES (?, ?, ?)",
            [(word, en, ja) for en, ja in pairs],
        )
    conn.commit()
    conn.close()
    print(f"Seeded examples for {len(EXAMPLES)} words")


if __name__ == "__main__":
    main()