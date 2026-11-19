English | [日本語](README.ja.md)

# EasyRead

EasyRead is a "reverse Yomitan" for Japanese learners of English. Hover over a word in English YouTube subtitles to see its Japanese meanings and example sentences, then save it to Anki with one click.

## Status

Prototype. The backend (dictionary lookup with lemmatization, example sentences, and Anki card creation) works. The Chrome extension is under development.

## Project structure

- `backend/`: FastAPI backend (dictionary lookup, Anki integration)
- `extension/`: Chrome extension (subtitle detection, hover popup)

## Run the backend

Frontend teammates do not need to run the backend. You can build against the sample JSON in the "API" section below and run the backend later.

### 1. Download the data (not stored in Git)

- **JMdict (English):** download the English JSON from the jmdict-simplified releases on GitHub (by scriptin). Save it as `backend/data/jmdict-eng.json`.
- **Tatoeba sentence pairs (optional):** download `jpn-eng.zip` from manythings.org, unzip it, and save the text file as `backend/data/jpn-eng.txt`. Without it, `examples` is always an empty list.

### 2. Install and build the database

```
cd backend
uv sync
uv run python import_jmdict.py
uv run python seed.py
uv run python import_examples.py    # only if you downloaded the Tatoeba file
```

`uv sync` also installs spaCy and its English model (`en_core_web_sm`), which are used for lemmatization.

Run the scripts in this order. `import_jmdict.py` rebuilds the `senses` table from scratch, so run `seed.py` right after it (your hand-written entries replace the automatic ones). Re-run them whenever the data changes.

### 3. Start the server

```
uv run uvicorn main:app --reload
```

The first start is a little slower because the spaCy model is loaded once at startup.

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

- `word`: the dictionary entry that was found, not the raw input. The input is normalized first (lowercase, punctuation removed). If there is no exact match, the word is converted to its base form (lemma) and searched again. For example, `Give up!` returns `give up`, and `gave up` also returns `give up`. `running` returns `run`.
- `senses`: a list of meaning groups, best first. Each has a part-of-speech `type` and a list of Japanese `meanings`.
- `examples`: up to 3 example sentences with Japanese translations. It can be an empty list `[]` (for rare words, or when the Tatoeba data is not installed), so the popup must handle that.

404 Not Found (word not in the dictionary):

```json
{ "detail": "Word not found" }
```

Limitations (for now):

- The lemmatizer works on single words or short phrases without context, so it can be wrong for ambiguous words (for example, `left`).
- Finding phrases inside a whole sentence is not supported yet. Send one word or phrase per request.
- Example sentences only match the exact form of the word. `give up` finds "Don't give up." but not "He gave up."

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

- `word` and `meaning` are required.
- `sentence` is optional. If it is omitted or empty, the backend uses the first example sentence for the word (English and its Japanese translation), if one exists. If there is none, the card is created without a sentence.

200 OK:

```json
{ "status": "ok", "note_id": 1234567890 }
```

Errors:

| Status | Meaning | Body |
| --- | --- | --- |
| 409 | The card already exists | `{ "detail": "Card already exists" }` |
| 503 | Cannot reach Anki | `{ "detail": "Cannot connect to Anki. Open Anki and install AnkiConnect." }` |
| 400 | Any other Anki error | `{ "detail": "<message from Anki>" }` |
| 422 | Invalid request body (for example, a missing `word`) | FastAPI validation error |

Card format: deck `EasyRead`, note type `Basic`. Front is the word. Back is the meaning, with the sentence below it. The deck is created automatically.

### Requirements for Anki

- Anki must be open on the same computer as the backend.
- The AnkiConnect add-on must be installed (code `2055492159`), and Anki restarted afterward.
- The `Basic` note type must have the fields `Front` and `Back`.

### Calling the API from the extension

- Add `http://127.0.0.1:8000/*` to `host_permissions` in `manifest.json`.
- CORS is already allowed in the backend.

### Changing the API

If the JSON shape changes, tell the team first. Changes can break the extension.

## Credits

- Dictionary data: JMdict/EDRDG, licensed under CC BY-SA 4.0 (https://www.edrdg.org/). Accessed through the jmdict-simplified project.
- Example sentences: Tatoeba (https://tatoeba.org/), licensed under CC BY 2.0 FR.
- Lemmatization: spaCy (https://spacy.io/) with the `en_core_web_sm` model.