English | [日本語](README.ja.md)

# EasyRead

Reverse Yomitan for Japanese learners of English: hover an English word in YouTube subtitles to see its Japanese meanings and example sentences, then save it to Anki.

## Project structure

- `backend/`: FastAPI backend (dictionary lookup, Anki integration)
- `extension/`: Chrome extension (subtitle detection, hover popup)

## Run the backend

1. Download the data files (they are not stored in Git):
   - JMdict (English): jmdict-simplified releases on GitHub (by scriptin). Save the English JSON as `backend/data/jmdict-eng.json`
   - Tatoeba sentence pairs: `jpn-eng.zip` from manythings.org. Save the text file as `backend/data/jpn-eng.txt`

2. Install and build the database:

```
cd backend
uv sync
uv run python import_jmdict.py
uv run python seed.py
uv run python import_examples.py
```

The three scripts must run in this order. Re-run them whenever you change the data.

3. Start the server:

```
uv run uvicorn main:app --reload
```

The API runs at http://127.0.0.1:8000 and the interactive docs are at http://127.0.0.1:8000/docs

## API

### GET /lookup?word=racket

200 OK:

```json
{
  "word": "racket",
  "senses": [
    { "type": "noun", "meanings": ["ラケット"] },
    { "type": "noun", "meanings": ["騒音", "どんちゃん騒ぎ"] }
  ],
  "examples": [
    { "english": "Choose your favorite racket.", "japanese": "好きなラケットを選びなさい。" }
  ]
}
```

- `senses` is a list of definitions, each with a part-of-speech `type` and a list of Japanese `meanings`.
- `examples` can be an empty list.
- The word is normalized (lowercase, punctuation removed), and the `word` field returns the cleaned version.

404 Not Found:

```json
{ "detail": "Word not found" }
```

## Credits

- Dictionary data: JMdict/EDRDG, licensed under CC BY-SA 4.0 (https://www.edrdg.org/). Accessed through the jmdict-simplified project.
- Example sentences: Tatoeba (https://tatoeba.org/), licensed under CC BY 2.0 FR.