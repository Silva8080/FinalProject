import json
import re
import sqlite3
from collections import defaultdict
from pathlib import Path

from text_utils import normalize

# Paths to the JMdict file and the output database
# JMdictファイルと出力先データベースのパス
BASE = Path(__file__).parent
JSON_PATH = BASE / "data" / "jmdict-eng.json"
DB_PATH = BASE / "database" / "dictionary.db"

# Max Japanese words per sense
# 1つの意味のまとまり(sense)に入れる日本語の最大数
MAX_MEANINGS = 5
# Max senses (part-of-speech groups) per English word
# 英単語1つあたりの意味のまとまりの最大数
MAX_SENSES = 4
# Skip glosses longer than this many words (they are explanations, not words)
# これより長い語義は説明文なので除外する(単語数)
MAX_WORDS = 4


def simple_type(pos_tags):
    """
    Turn JMdict part-of-speech tags into a simple label.
    JMdictの詳細な品詞タグを、わかりやすいラベルに変換する。
    """
    for tag in pos_tags:
        if tag == "n" or tag.startswith("n-"):
            return "noun"            # noun / 名詞
        if tag.startswith("v"):
            return "verb"            # verb / 動詞
        if tag.startswith("adj"):
            return "adjective"       # adjective / 形容詞
        if tag.startswith("adv"):
            return "adverb"          # adverb / 副詞
        if tag == "exp":
            return "expression"      # expression / 表現
        if tag == "int":
            return "interjection"    # interjection / 感動詞
        if tag == "pn":
            return "pronoun"         # pronoun / 代名詞
        if tag == "prt":
            return "particle"        # particle / 助詞
        if tag == "conj":
            return "conjunction"     # conjunction / 接続詞
    return "other"


def clean_gloss(text):
    """
    Turn an English gloss into a lookup key. Returns None if unusable.
    英語の語義を検索用のキーに変換する。使えない場合は None を返す。
    """
    # Remove notes in parentheses
    # 括弧内の補足を削除する
    text = re.sub(r"\([^)]*\)", "", text)
    text = text.lower().strip()
    # "to give up" -> "give up"
    # 先頭の "to " を削除する
    if text.startswith("to "):
        text = text[3:]
    # Same normalization as /lookup, so the keys match
    # /lookup と同じ正規化を使い、キーが一致するようにする
    text = normalize(text)
    # Skip empty or too-long glosses
    # 空の語義や長すぎる語義は除外する
    if not text or len(text.split()) > MAX_WORDS:
        return None
    return text


def main():
    # Load the whole JMdict file (takes a few seconds)
    # JMdictファイル全体を読み込む(数秒かかる)
    with open(JSON_PATH, encoding="utf-8") as f:
        data = json.load(f)

    # English key -> list of (rank, part of speech, Japanese word)
    # 英語キー -> (順位, 品詞, 日本語) のリスト
    candidates = defaultdict(list)

    for entry in data["words"]:
        kanji = entry.get("kanji", [])
        kana = entry.get("kana", [])
        if not kana:
            continue

        # Is this a common word? Common words are ranked first.
        # 一般的な語か。一般的な語を優先して上位にする。
        common = any(k.get("common") for k in kanji + kana)

        # Japanese form to show: common kanji spelling if any, otherwise kana
        # 表示する日本語: 一般的な漢字表記があればそれ、なければかな
        common_kanji = next((k["text"] for k in kanji if k.get("common")), None)
        japanese = common_kanji or kana[0]["text"]

        last_pos = []
        for sense_index, sense in enumerate(entry.get("sense", [])):
            # An empty part-of-speech list means "same as the previous sense"
            # 品詞が空なら「前の意味と同じ」という意味
            pos = sense.get("partOfSpeech") or last_pos
            last_pos = pos
            word_type = simple_type(pos)

            for gloss_index, gloss in enumerate(sense.get("gloss", [])):
                # Only English glosses
                # 英語の語義だけを使う
                if gloss.get("lang", "eng") != "eng":
                    continue
                key = clean_gloss(gloss["text"])
                if key is None:
                    continue
                # Lower rank = better (common first, then earlier senses)
                # 順位は小さいほど上位(一般的な語が先、次に前の意味が先)
                rank = (0 if common else 1, sense_index, gloss_index)
                candidates[key].append((rank, word_type, japanese))

    rows = []
    for key, items in candidates.items():
        # Group the Japanese words by part of speech
        # 日本語を品詞ごとにグループ化する
        groups = defaultdict(list)
        for rank, word_type, jp in items:
            groups[word_type].append((rank, jp))

        built = []
        for word_type, entries in groups.items():
            entries.sort(key=lambda x: x[0])

            # Remove duplicates and keep at most MAX_MEANINGS
            # 重複を除き、最大 MAX_MEANINGS 個まで残す
            meanings = []
            for _, jp in entries:
                if jp not in meanings:
                    meanings.append(jp)
                if len(meanings) == MAX_MEANINGS:
                    break
            built.append((entries[0][0], word_type, meanings))

        # Best-ranked group first
        # 順位が良いグループを先頭にする
        built.sort(key=lambda x: x[0])

        for position, (_, word_type, meanings) in enumerate(built[:MAX_SENSES]):
            # Rough guess: a multi-word verb key is a phrasal verb (refine later)
            # 大まかな判定: 複数語の動詞は句動詞とする(後で改善する)
            if " " in key and word_type == "verb":
                word_type = "phrasal verb"
            rows.append(
                (key, word_type, json.dumps(meanings, ensure_ascii=False), position)
            )

    # Rebuild the senses table from scratch
    # senses テーブルを作り直す
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DROP TABLE IF EXISTS senses")
    conn.execute(
        """
        CREATE TABLE senses (
            id       INTEGER PRIMARY KEY,
            word     TEXT NOT NULL,
            type     TEXT NOT NULL,
            meanings TEXT NOT NULL,
            position INTEGER NOT NULL
        )
        """
    )
    conn.executemany(
        "INSERT INTO senses (word, type, meanings, position) VALUES (?, ?, ?, ?)",
        rows,
    )
    # Index on word so lookups stay fast
    # 検索を速くするため word にインデックスを作る
    conn.execute("CREATE INDEX idx_senses_word ON senses(word)")
    conn.commit()
    conn.close()
    print(f"Saved {len(rows)} senses for {len(candidates)} words")


if __name__ == "__main__":
    main()