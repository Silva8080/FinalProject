import json
import sqlite3
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from text_utils import TYPE_JA, normalize
from anki import AnkiError, add_card
from lemmatizer import lemmatize, verb_tokens
from phrases import candidate_phrases
from html import escape
from seed import ENTRIES as CURATED

app = FastAPI(title="EasyRead API")

# CORS: lets the Chrome extension call this API
# CORS設定: Chrome拡張機能からこのAPIを呼び出せるようにする
app.add_middleware(
    CORSMiddleware,
    # Allow everything for the prototype; restrict before release
    # プロトタイプなので全て許可。公開前に制限する
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# Schemas: the contract with the frontend team (shape of the JSON we return)
# スキーマ: フロントエンド担当との約束（APIが返すJSONの形）
class Sense(BaseModel):
    # Part of speech (noun, verb, phrasal verb, ...) / 品詞
    type: str
    # Part of speech in Japanese (名詞, 動詞, ...) / 品詞の日本語
    type_ja: str = ""
    # Japanese meanings of this sense / この意味のまとまりの日本語訳のリスト
    meanings: list[str]


class Example(BaseModel):
    # English example sentence / 英語の例文
    english: str
    # Its Japanese translation / 例文の日本語訳
    japanese: str


class LookupResult(BaseModel):
    # Normalized word / 正規化した単語
    word: str
    # List of senses, best first / 意味のまとまりのリスト（重要な順）
    senses: list[Sense]
    # Example sentences; can be empty / 例文のリスト（空の場合あり）
    examples: list[Example] = []


# Path to the dictionary database / 辞書データベースのパス
DB_PATH = Path(__file__).parent / "database" / "dictionary.db"


@app.get("/")
def root():
    # Health check / サーバーが動いているかの確認用
    return {"message": "API is running"}


def find_senses(word: str):
    # One DB connection per request (routes run in separate threads)
    # リクエストごとにDB接続を開く（スレッド間で接続を共有しない）
    conn = sqlite3.connect(DB_PATH)
    try:
        rows = conn.execute(
            "SELECT type, meanings FROM senses WHERE word = ? ORDER BY position",
            (word,),
        ).fetchall()
        # meanings is stored as a JSON string, so decode it
        # meanings はJSON文字列で保存されているのでリストに戻す
        return [
            {"type": t, "type_ja": TYPE_JA.get(t, ""), "meanings": json.loads(m)}
            for t, m in rows
        ]
    finally:
        conn.close()


def find_examples(word: str):
    conn = sqlite3.connect(DB_PATH)
    try:
        rows = conn.execute(
            "SELECT english, japanese FROM examples WHERE word = ? ORDER BY id",
            (word,),
        ).fetchall()
        return [{"english": e, "japanese": j} for e, j in rows]
    except sqlite3.OperationalError:
        # examples table not created yet: return no examples
        # examples テーブルがまだ無い場合は例文なしで返す
        return []
    finally:
        conn.close()

def find_in_sentence(word: str, sentence: str):
    # Words used as verbs in this sentence (to reject "strike on" in "A strike on ...")
    # この文で動詞として使われている単語（名詞の "strike on" などを除外するため）
    verbs = verb_tokens(sentence)

    for phrase in candidate_phrases(sentence, word):
        first = phrase.split()[0]

        # Try the exact form, then its lemma
        # 完全一致、次に基本形の順に試す
        options = [phrase]
        lemma = normalize(lemmatize(phrase))
        if lemma != phrase:
            options.append(lemma)

        for option in options:
            senses = find_senses(option)
            if not senses:
                continue
            # Automatic multi-word entries are too noisy: only accept
            # phrasal verbs and hand-written (seeded) phrases
            # 自動生成の複数語エントリはノイズが多いので、句動詞か手書きのものだけ使う
            is_phrase = " " in option
            is_phrasal = all(s["type"] == "phrasal verb" for s in senses)
            if is_phrase and option not in CURATED and not is_phrasal:
                continue
            # A phrasal verb must start with a word used as a verb
            # 句動詞は、動詞として使われている単語で始まる必要がある
            if all(s["type"] == "phrasal verb" for s in senses) and first not in verbs:
                continue
            return option, senses
    return None

@app.get("/lookup", response_model=LookupResult)
def lookup(word: str, sentence: str = ""):
    clean = normalize(word)
    senses = []

    # 0) If the subtitle line was sent, look for a phrase around the word
    # 字幕の1行が送られてきた場合は、単語の周りのフレーズを探す
    if sentence:
        hit = find_in_sentence(word, sentence)
        if hit:
            clean, senses = hit

    # 1) Exact match first / まず完全一致
    if not senses:
        senses = find_senses(clean)

    # 2) Retry with the lemma / 見つからなければ見出し語に直して再検索
    if not senses:
        lemma = normalize(lemmatize(clean))
        if lemma != clean:
            senses = find_senses(lemma)
            if senses:
                clean = lemma

    if not senses:
        raise HTTPException(status_code=404, detail="Word not found")
    return {
        "word": clean,
        "senses": senses,
        "examples": find_examples(clean),
    }

def build_back(senses, examples, context=""):
    # Card back: all senses, then examples, then the subtitle line
    # カードの裏面: すべての意味、例文、字幕の1行の順に並べる
    parts = []
    for s in senses:
        label = s["type"]
        ja = TYPE_JA.get(label)
        title = f"{label} / {ja}" if ja else label
        parts.append(f"<b>{escape(title)}</b><br>{escape('、'.join(s['meanings']))}")
    back = "<br><br>".join(parts)

    if examples:
        ex = "<br><br>".join(
            f"{escape(e['english'])}<br>{escape(e['japanese'])}" for e in examples
        )
        back += "<hr>" + ex

    # Skip the subtitle line if it is already one of the examples
    # 字幕の1行が例文と同じなら、重複するので追加しない
    example_texts = {normalize(e["english"]) for e in examples}
    if context and normalize(context) not in example_texts:
        back += f"<hr><i>{escape(context)}</i>"
    return back

# Request body sent by the extension
# 拡張機能が送るリクエストの形
class AnkiCard(BaseModel):
    # The "word" field from /lookup (for example "give up")
    # /lookup が返した word（例: "give up"）
    word: str
    # Optional: only used if the word is not in the dictionary
    # 省略可。辞書にない単語のときだけ使う
    meaning: str = ""
    # Optional: the subtitle line where the word appeared
    # 省略可。単語が出てきた字幕の1行
    sentence: str = ""


# Response / レスポンスの形
class AnkiResult(BaseModel):
    status: str
    note_id: int


@app.post("/anki/add", response_model=AnkiResult)
def anki_add(card: AnkiCard):
    clean = normalize(card.word)
    senses = find_senses(clean)
    examples = find_examples(clean) if senses else []

    if senses:
        back = build_back(senses, examples, card.sentence)
    elif card.meaning:
        # Not in the dictionary: use what the extension sent
        # 辞書にない場合は、拡張機能から送られた内容を使う
        back = escape(card.meaning)
        if card.sentence:
            back += f"<hr><i>{escape(card.sentence)}</i>"
    else:
        raise HTTPException(status_code=404, detail="Word not found")

    try:
        note_id = add_card(card.word, back)
    except AnkiError as e:
        message = str(e)
        # Anki not open -> 503, duplicate card -> 409, anything else -> 400
        # Ankiが閉じている -> 503、重複 -> 409、その他 -> 400
        if "Cannot connect" in message:
            raise HTTPException(status_code=503, detail=message)
        if "duplicate" in message.lower():
            raise HTTPException(status_code=409, detail="Card already exists")
        raise HTTPException(status_code=400, detail=message)
    return {"status": "ok", "note_id": note_id}