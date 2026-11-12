English | [日本語](README.ja.md)

# EasyRead

EasyRead is a "reverse Yomitan" for Japanese learners of English. Hover over a word in English YouTube subtitles to see its Japanese meanings and example sentences, then save it to Anki with one click.

## Status

Prototype. The backend (dictionary lookup and Anki card creation) works. The Chrome extension is under development.

## Project structure

- `backend/`: FastAPI backend (dictionary lookup, Anki integration)
- `extension/`: Chrome extension (subtitle detection, hover popup)

## Run the backend

Frontend teammates do not need to run the backend. You can build against the sample JSON in the "API" section below and run the backend later.

### 1. Download the data (not stored in Git)

- **JMdict (English):** download the English JSON from the jmdict-simplified releases on GitHub (by scriptin). Save it as `backend/data/jmdict-eng.json`.
- **Tatoeba sentence pairs (optional):** download `jpn-eng.zip` from manythings.org, unzip it, and save it as `backend/data/jpn-eng.txt`. Without it, `examples` is always an empty list.

### 2. Install and build the database

```
cd backend
uv sync
uv run python import_jmdict.py
uv run python seed.py
uv run python import_examples.py    # only if you downloaded the Tatoeba file
```

Run the scripts in this order. `import_jmdict.py` rebuilds the `senses` table from scratch, so run `seed.py` right after it (your hand-written entries replace the automatic ones). Re-run them whenever the data changes.

### 3. Start the server

```
uv run uvicorn main:app --reload
```

The API runs at http://127.0.0.1:8000 and the interactive docs are at http://127.0.0.1:8000/docs

## API

Base URL: `http://127.0.0.1:8000`

### GET /lookup?word=racket

Looks up an English word or phrase.

200 OK:

```json
{
  "word": "racket",
  "senses": [
    { "type": "noun", "meanings": ["ラケット"] }
  ],
  "examples": [
    { "english": "Choose your favorite racket.", "japanese": "好きなラケットを選びなさい。" }
  ]
}
```

- `word`: the normalized word (lowercase, punctuation removed), not the raw input. `Give up!` is searched and returned as `give up`.
- `senses`: a list of meaning groups, best first. Each has a part-of-speech `type` and a list of Japanese `meanings`.
- `examples`: example sentences with Japanese translations. It can be an empty list `[]`, so the popup must handle that.

404 Not Found (word not in the dictionary):

```json
{ "detail": "Word not found" }
```

Limitations (for now): only dictionary forms match. Inflected forms such as `gave up`, `running`, and `dogs` return 404 until lemmatization is added.

### POST /anki/add

Creates an Anki card through AnkiConnect.

Request body:

```json
{
  "word": "give up",
  "meaning": "諦める",
  "sentence": "I won't give up."
}
```

- `word` and `meaning`