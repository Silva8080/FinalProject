import json
import sqlite3
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from text_utils import normalize
from anki import AnkiError, add_card
from lemmatizer import lemmatize

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
        return [{"type": t, "meanings": json.loads(m)} for t, m in rows]
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


@app.get("/lookup", response_model=LookupResult)
def lookup(word: str):
    clean = normalize(word)

    # 1) Exact match first (fast) / まず完全一致で検索する（速い）
    senses = find_senses(clean)

    # 2) On a miss, retry with the lemma / 見つからなければ見出し語に直して再検索する
    if not senses:
        lemma = normalize(lemmatize(clean))
        if lemma != clean:
            senses = find_senses(lemma)
            if senses:
                clean = lemma   # return the entry that was actually found

    if not senses:
        raise HTTPException(status_code=404, detail="Word not found")
    return {
        "word": clean,
        "senses": senses,
        "examples": find_examples(clean),
    }

# Request body sent by the extension
# 拡張機能が送るリクエストの形
class AnkiCard(BaseModel):
    # The English word or phrase / 英単語またはフレーズ
    word: str
    # Japanese meaning to put on the back of the card / カードの裏面に入れる日本語の意味
    meaning: str
    # Example sentence; optional. If empty, the first example from the DB is used
    # 例文（省略可）。空の場合はDBの最初の例文を使う
    sentence: str = ""


# Response / レスポンスの形
class AnkiResult(BaseModel):
    status: str
    note_id: int


@app.post("/anki/add", response_model=AnkiResult)
def anki_add(card: AnkiCard):
    # If no sentence was sent, use the first example from the database
    # 例文が送られてこなかった場合は、DBの最初の例文を使う
    sentence = card.sentence
    if not sentence:
        examples = find_examples(normalize(card.word))
        if examples:
            sentence = f"{examples[0]['english']}<br>{examples[0]['japanese']}"

    try:
        note_id = add_card(card.word, card.meaning, sentence)
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