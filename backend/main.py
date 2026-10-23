from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import re
import sqlite3
from pathlib import Path
app = FastAPI(title="English Immersion API")

# CORS: lets the Chrome extension call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # fine for a prototype, restrict it later
    allow_methods=["*"],
    allow_headers=["*"],
)


# Schema: the contract with your frontend teammates
class LookupResult(BaseModel):
    word: str
    meaning: str
    type: str

DB_PATH = Path(__file__).parent / "database" / "dictionary.db"


def find_word(word: str):
    conn = sqlite3.connect(DB_PATH)
    try:
        return conn.execute(
            "SELECT meaning, type FROM entries WHERE word = ?", (word,)
        ).fetchone()
    finally:
        conn.close()
@app.get("/")
def root():
    return {"message": "API is running"}

def normalize(text: str) -> str:
    text = text.lower()
    text = text.replace("’", "'")           # curly apostrophe -> straight
    text = re.sub(r"[^\w\s']", "", text)    # remove everything except letters, digits, spaces, '
    return " ".join(text.split())           # trim and collapse repeated spaces
@app.get("/lookup", response_model=LookupResult)
def lookup(word: str):
    clean = normalize(word)
    row = find_word(clean)
    if row is None:
        raise HTTPException(status_code=404, detail="Word not found")
    meaning, word_type = row
    return {"word": clean, "meaning": meaning, "type": word_type}