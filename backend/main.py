from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
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


# Fake dictionary (Stage 1). Moves to SQLite in Stage 3.
DICTIONARY = {
    "give up": {"meaning": "諦める", "type": "phrasal verb"},
    "hang out": {"meaning": "遊ぶ", "type": "phrasal verb"},
    "gonna": {"meaning": "〜するつもり", "type": "contraction"},
    "no way": {"meaning": "マジで！？", "type": "idiom"},
    "hello": {"meaning": "こんにちは", "type": "interjection"},
}


@app.get("/")
def root():
    return {"message": "API is running"}


@app.get("/lookup", response_model=LookupResult)
def lookup(word: str):
    entry = DICTIONARY.get(word)
    if entry is None:
        raise HTTPException(status_code=404, detail="Word not found")
    return {"word": word, **entry}