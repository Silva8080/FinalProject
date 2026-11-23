import json
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "database" / "dictionary.db"

# Hand-written entries. They REPLACE whatever the JMdict import made for that word.
# Words must already be normalized (lowercase, no punctuation except ').
# Format: word -> list of (type, [meanings]), best sense first.
ENTRIES = {
    "give up": [("phrasal verb", ["諦める", "やめる", "降参する"])],
    "dog": [("noun", ["犬", "イヌ", "わんこ"])],
    "go": [
        ("verb", ["行く", "出かける", "向かう"]),
        ("verb", ["進む", "うまくいく", "動く"]),
        ("verb", ["〜になる"]),
        ("noun", ["順番", "試み"]),
    ],
    "take": [
        ("verb", ["取る", "持っていく", "連れていく"]),
        ("verb", ["(時間が)かかる"]),
        ("verb", ["受ける", "飲む"]),
        ("verb", ["乗る"]),
    ],
    "make": [
        ("verb", ["作る", "つくる"]),
        ("verb", ["〜させる"]),
        ("verb", ["稼ぐ"]),
        ("verb", ["〜になる", "〜にする"]),
    ],
    "come": [
        ("verb", ["来る", "やって来る"]),
        ("verb", ["着く", "到着する"]),
        ("verb", ["実現する", "〜になる"]),
    ],
    "put": [
        ("verb", ["置く", "入れる"]),
        ("verb", ["書く", "記入する"]),
        ("verb", ["表現する", "言う"]),
    ],
    "have": [
        ("verb", ["持っている", "所有する"]),
        ("verb", ["食べる", "飲む"]),
        ("verb", ["(経験を)する", "過ごす"]),
        ("verb", ["〜させる", "〜してもらう"]),
    ],
    "do": [
        ("verb", ["する", "行う"]),
        ("verb", ["(仕事を)している"]),
        ("verb", ["足りる", "間に合う"]),
    ],
    "see": [
        ("verb", ["見える", "見る"]),
        ("verb", ["会う", "訪ねる"]),
        ("verb", ["わかる", "理解する"]),
    ],
    "look": [
        ("verb", ["見る", "目を向ける"]),
        ("verb", ["〜に見える", "〜のようだ"]),
        ("noun", ["目つき", "見た目"]),
    ],
    "turn": [
        ("verb", ["回る", "回す"]),
        ("verb", ["曲がる", "向きを変える"]),
        ("verb", ["〜になる", "変わる"]),
        ("noun", ["順番", "回転"]),
    ],
    "run": [
        ("verb", ["走る", "駆ける"]),
        ("verb", ["経営する", "運営する"]),
        ("verb", ["動く", "流れる"]),
        ("noun", ["ラン", "走ること", "連続"]),
    ],
    "every single": [("expression", ["ありとあらゆる", "一つ残らず", "すべての"])],
    "single": [
        ("adjective", ["単一の", "たった一つの", "独身の"]),
        ("noun", ["シングル", "独身者"]),
    ],
    "bring": [
        ("verb", ["持ってくる", "連れてくる"]),
        ("verb", ["もたらす", "引き起こす"]),
    ],
    "collapse": [
        ("verb", ["崩れる", "倒壊する", "崩壊する", "倒れる"]),
        ("noun", ["崩壊", "倒壊", "暴落"]),
    ],
    "collapsed": [("adjective", ["崩壊した", "倒壊した"])],
    "run out of": [("phrasal verb", ["〜を使い果たす", "〜がなくなる"])],
    "break": [
        ("verb", ["壊す", "割る", "折る", "壊れる"]),
        ("verb", ["中断する", "破る"]),
        ("noun", ["休憩", "小休止", "チャンス"]),
    ],
    "give away": [
        ("phrasal verb", ["無料で配る", "あげる", "譲る"]),
        ("phrasal verb", ["うっかり漏らす", "暴露する"]),
    ],
    "go off": [
        ("phrasal verb", ["爆発する", "鳴り出す"]),
        ("phrasal verb", ["立ち去る", "腐る"]),
    ],
    "make it": [
        ("phrasal verb", ["間に合う", "成功する", "うまくいく"]),
    ],
    "come over": [
        ("phrasal verb", ["遊びに来る", "立ち寄る"]),
    ],
    "gotta": [("contraction", ["〜しなきゃ", "〜しなければならない"])],
    "kinda": [("contraction", ["ちょっと", "なんか〜っぽい", "まあ"])],
    "lemme": [("contraction", ["〜させて", "ちょっと〜させて"])],
    "ain't": [("contraction", ["〜じゃない", "〜ではない"])],
    "give me a break": [("expression", ["勘弁してよ", "いい加減にして", "冗談でしょ"])],
    "give us a break": [("expression", ["勘弁してよ", "いい加減にして"])],
    "get": [
        ("verb", ["手に入れる", "得る", "もらう", "買う"]),  # obtain / receive
        ("verb", ["〜になる", "〜してくる"]),  # become
        ("verb", ["着く", "到着する"]),  # arrive
        ("verb", ["わかる", "理解する"]),  # understand
    ],
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