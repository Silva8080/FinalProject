import json
import re
import sqlite3
from collections import defaultdict
from pathlib import Path

from wordfreq import zipf_frequency

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
# Minimum common entries needed before rare ones are dropped
# 珍しい語を除外するために必要な、一般的な語の最小数
MIN_COMMON = 1
# Senses tagged with these are formal, old, rude or rare: rank them lower
# 敬語・古語・俗語・まれな語の意味は順位を下げる
BAD_MISC = {"hum", "hon", "pol", "arch", "obs", "obsc", "rare", "derog", "vulg", "sl"}


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
    # Remove (notes), including nested parentheses
    # 括弧内の補足を削除する（入れ子の括弧にも対応）
    while True:
        new_text = re.sub(r"\([^()]*\)", "", text)
        if new_text == text:
            break
        text = new_text
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
    words = text.split()
    if not text or len(words) > MAX_WORDS:
        return None
    # Skip "the dog" / "a cat": an article plus one word is not a real phrase
    # "the dog" のような「冠詞＋1語」は句ではないので除外する
    if len(words) == 2 and words[0] in {"the", "a", "an"}:
        return None
    return text


# Cache of Japanese word -> frequency score (higher = more common)
# 日本語 -> 頻度スコアのキャッシュ（大きいほど一般的）
_freq_cache = {}


def freq(japanese):
    if japanese not in _freq_cache:
        _freq_cache[japanese] = zipf_frequency(japanese, "ja")
    return _freq_cache[japanese]


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

                # Penalize formal, old, rude or rare senses
                # 敬語・古語・俗語・まれな意味は順位を下げる
                penalty = 1 if BAD_MISC & set(sense.get("misc", [])) else 0
                # Primary meaning: this English word is the first gloss of the first sense
                # 主な意味: この英語が最初の意味の最初の語義である
                # Formal/rare senses are never primary matches
                # 敬語・まれな意味は「主な意味」にしない
                tier = 0 if (sense_index == 0 and gloss_index == 0 and penalty == 0) else 1
                # Lower rank = better
                # 順位は小さいほど上位
                rank = (
                    0 if common else 1,   # [0] common first / 一般的な語が先
                    penalty,              # [1] formal/rare last / 敬語・まれな語は後
                    tier,                 # [2] primary meaning first / 主な意味が先
                    -freq(japanese),      # [3] negative so common words sort first
                    sense_index,          # [4]
                    gloss_index,          # [5]
                )
                candidates[key].append((rank, word_type, japanese))

    rows = []
    for key, items in candidates.items():
        # If there are enough common entries, drop the rare ones
        # 一般的な語が十分あれば、珍しい語は除外する
        common_items = [it for it in items if it[0][0] == 0]
        if len(common_items) >= MIN_COMMON:
            items = common_items

        # Group the Japanese words by part of speech
        # 日本語を品詞ごとにグループ化する
        groups = defaultdict(list)
        for rank, word_type, jp in items:
            groups[word_type].append((rank, jp))

        built = []
        for word_type, entries in groups.items():
            entries.sort(key=lambda x: x[0])

            # NEW: if some entries are primary matches (tier 0), drop the incidental ones
            # NEW: 主な意味の一致(tier 0)があれば、偶然一致しただけの語は除外する
            if any(e[0][2] == 0 for e in entries):
                entries = [e for e in entries if e[0][2] == 0]

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

        # NEW: drop groups that only match incidentally when a primary group exists
        # NEW: 主な意味のグループがあれば、偶然一致しただけのグループは除外する
        if any(b[0][2] == 0 for b in built):
            built = [b for b in built if b[0][2] == 0]

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