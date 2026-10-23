import re
import sqlite3
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

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


# Schema: the contract with the frontend team (shape of the JSON we return)
# スキーマ: フロントエンド担当との約束（APIが返すJSONの形）
class LookupResult(BaseModel):
    # Normalized word / 正規化した単語
    word: str
    # Japanese meaning / 日本語の意味
    meaning: str
    # Part of speech (phrasal verb, idiom, etc.) / 品詞（phrasal verb, idiom など）
    type: str


# Path to the dictionary database (relative to main.py)
# 辞書データベースのパス（main.pyから見た相対パス）
DB_PATH = Path(__file__).parent / "database" / "dictionary.db"


@app.get("/")
def root():
    # Health check: confirms the server is running
    # サーバーが動いているかの確認用
    return {"message": "API is running"}


def find_word(word: str):
    # Open a new DB connection per request (FastAPI runs routes in separate
    # threads, so we don't share connections)
    # リクエストごとにDB接続を開く（FastAPIは別スレッドで実行するため、接続を使い回さない）
    conn = sqlite3.connect(DB_PATH)
    try:
        # Use ? placeholders to pass values safely (prevents SQL injection).
        # Returns (meaning, type) if found, otherwise None.
        # ? を使って安全に値を渡す（SQLインジェクション対策）。
        # 見つかれば (意味, 品詞) を、なければ None を返す
        return conn.execute(
            "SELECT meaning, type FROM entries WHERE word = ?", (word,)
        ).fetchone()
    finally:
        conn.close()


def normalize(text: str) -> str:
    # Make subtitle text match the dictionary format
    # 字幕の表記ゆれをそろえて、辞書と同じ形にする

    # Lowercase / 小文字にする
    text = text.lower()
    # Curly apostrophe -> straight apostrophe / 曲がったアポストロフィを通常の ' に変換
    text = text.replace("’", "'")
    # Remove everything except letters, digits, spaces and ' (! ? . , etc.)
    # 文字・数字・空白・' 以外（! ? . , など）を削除
    text = re.sub(r"[^\w\s']", "", text)
    # Trim the ends and collapse repeated spaces into one
    # 前後の空白を削除し、連続する空白を1つにする
    return " ".join(text.split())


@app.get("/lookup", response_model=LookupResult)
def lookup(word: str):
    # Example: /lookup?word=Give up! is searched as "give up"
    # 例: /lookup?word=Give up! → "give up" として検索する
    clean = normalize(word)
    row = find_word(clean)
    if row is None:
        # Not in the dictionary: return 404
        # 辞書にない場合は404を返す
        raise HTTPException(status_code=404, detail="Word not found")
    meaning, word_type = row
    return {"word": clean, "meaning": meaning, "type": word_type}