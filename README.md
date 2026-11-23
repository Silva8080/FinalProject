English | [日本語](README.ja.md)

# EasyRead

EasyRead is a "reverse Yomitan" for Japanese learners of English. Hover over a word in English YouTube subtitles to see its Japanese meanings and example sentences, then save it to Anki with one click.

## Status

Prototype. The backend (dictionary lookup with lemmatization, phrase detection in a sentence, example sentences, and Anki card creation) works. The Chrome extension is under development.

## Project structure

- `backend/`: FastAPI backend (dictionary lookup, Anki integration)
- `extension/`: Chrome extension (subtitle detection, hover popup)

## Run the backend

Frontend teammates can either build the database themselves (below) or get a ready-made `dictionary.db` from the backend developer and put it in `backend/database/`. Until the backend runs, build against the sample JSON in the "API" section.

### 1. Download the data (not stored in Git)

The data files are large and are listed in `.gitignore`. Never commit them.

- **JMdict (English):** download the English JSON from the jmdict-simplified releases on GitHub (by scriptin). Save it as `backend/data/jmdict-eng.json`.
- **Tatoeba sentence pairs (optional):** download `jpn-eng.zip` from manythings.org, unzip it, and save the text file as `backend/data/jpn-eng.txt`. Without it, automatic examples are not generated (curated examples still work).

### 2. Install and build the database

```
cd backend
uv sync
uv run python import_jmdict.py
uv run python seed.py
uv run python import_examples.py
uv run python seed_examples.py
```

Run the scripts **in this order**. Each one depends on the one before it:

| Script | What it does |
| --- | --- |
| `import_jmdict.py` | Builds the `senses` table from JMdict (English to Japanese). Rebuilds the table from scratch. |
| `seed.py` | Hand-written senses. They replace the automatic ones for the same word. Also adds phrasal verbs, idioms, and slang that JMdict lacks. |
| `import_examples.py` | Builds the `examples` table from Tatoeba. It reads the words from `senses`, and rebuilds the table from scratch. Skip it if you do not have the Tatoeba file. |
| `seed_examples.py` | Hand-written example sentences. They replace the automatic ones for the same word. |

Re-run the whole sequence whenever any data or script changes. `uv sync` also installs spaCy and its English model (`en_core_web_sm`) for lemmatization, and `wordfreq` for ranking.

### 3. Check coverage (optional)

```
uv run python check_coverage.py
```

Lists common phrases that are missing from the dictionary, or that have fewer than 3 example sentences. Add them to `seed.py` and `seed_examples.py`, rebuild, and run it again. Add new phrases to the `CANDIDATES` list in the script.

### 4. Run the tests (optional)

```
uv run pytest -v
```

Tests use the built database, so run the build scripts first.

### 5. Start the server

```
uv run uvicorn main:app --reload
```

The first start is a little slower because the spaCy model is loaded once at startup.

The API runs at http://127.0.0.1:8000 and the interactive docs are at http://127.0.0.1:8000/docs

## Data

- **Automatic data:** JMdict is Japanese to English, so the import inverts it. This works well for concrete nouns and poorly for core verbs (`get`, `go`, `take`, `make`) and for phrasal verbs, idioms, and slang, which JMdict barely contains.
- **Curated data:** `seed.py` and `seed_examples.py` hold hand-written entries for those words. Japanese in these files should be checked by a native speaker before release.
- **Examples:** Tatoeba sentences are matched by exact word form, and the longest known phrase wins (a sentence with "give up" is saved under `give up`, not `give`). Different meanings of the same word are not distinguished in automatic examples.

## API

Base URL: `http://127.0.0.1:8000`

### GET /lookup?word=racket

Looks up an English word or phrase.

Query parameters:

| Name | Required | Description |
| --- | --- | --- |
| `word` | yes | The hovered word (or a phrase). |
| `sentence` | no | The whole subtitle line that contains the word. If sent, the backend looks for a phrase around the word (for example `give up`). |

Always URL-encode both values (`encodeURIComponent` in JavaScript).

200 OK:

```json
{
  "word": "racket",
  "senses": [
    { "type": "noun", "type_ja": "名詞", "meanings": ["ラケット"] }
  ],
  "examples": [
    { "english": "You have the same racket as I have.", "japanese": "君は僕と同じラケットを持っている。" },
    { "english": "Tom laid his racket on the ground.", "japanese": "トムはラケットを地面に置いた。" },
    { "english": "I bought this racket at a 20 percent discount.", "japanese": "私はこのラケットを２０％引きで買った。" }
  ]
}
```

- `word`: the dictionary entry that was found, not the raw input. Use it as the popup heading. The input is normalized first (lowercase, punctuation removed). If there is no exact match, the word is converted to its base form (lemma) and searched again. For example, `Give up!` returns `give up`, and `gave up` also returns `give up`. `running` returns `run`.
- `senses`: a list of meaning groups, best first. Each has a part-of-speech `type`, its Japanese label `type_ja`, and a list of Japanese `meanings`.
- `type_ja`: the part of speech in Japanese (for example `名詞`, `動詞`, `句動詞`). It is an empty string if the type has no Japanese label, so fall back to `type`.
- `examples`: up to 3 example sentences with Japanese translations. It can be an empty list `[]` (for rare words or phrases), so the popup must handle that.

404 Not Found (word not in the dictionary):

```json
{ "detail": "Word not found" }
```

#### Phrase detection with `sentence`

```
GET /lookup?word=give&sentence=I%20won't%20give%20up
```

returns the entry `give up`. Hovering `up` in the same line returns `give up` too. The backend tries phrases that contain the hovered word, longest first, including separated forms ("give it up" becomes `give up`) and inflected forms ("gave up" becomes `give up`). If no phrase matches, it falls back to looking up the word alone. Without `sentence`, the behavior is the same as before.

Limitations (for now):

- Only phrases that exist in the dictionary can be found. If `get over` is missing, hovering `get` in that line returns `get`. Missing phrases are added to `seed.py`.
- The lemmatizer works on single words or short phrases without context, so it can be wrong for ambiguous words (for example, `left`).
- Example sentences only match the exact form of the word. `give up` finds "Don't give up." but not "He gave up."

### POST /anki/add

Creates an Anki card through AnkiConnect. The backend builds the card from its own dictionary data, so the card matches what the popup shows.

Request body:

```json
{
  "word": "give up",
  "sentence": "I won't give up."
}
```

- `word` is required. Send the `word` field from the `/lookup` response (for example `give up`).
- `sentence` is optional. It is the subtitle line where the word appeared, and it is added at the bottom of the card (unless it is already one of the examples).
- `meaning` is optional and only used if the word is not in the dictionary. If the word is in the dictionary, it is ignored.

Card format: deck `EasyRead`, note type `Basic`. Front is the word. Back has every sense with its part of speech (English and Japanese), up to 3 example sentences with Japanese translations, and the subtitle line (if sent). The deck is created automatically.

200 OK:

```json
{ "status": "ok", "note_id": 1234567890 }
```

Errors:

| Status | Meaning | Body |
| --- | --- | --- |
| 404 | The word is not in the dictionary and no `meaning` was sent | `{ "detail": "Word not found" }` |
| 409 | The card already exists | `{ "detail": "Card already exists" }` |
| 503 | Cannot reach Anki | `{ "detail": "Cannot connect to Anki. Open Anki and install AnkiConnect." }` |
| 400 | Any other Anki error | `{ "detail": "<message from Anki>" }` |
| 422 | Invalid request body (for example, a missing `word`) | FastAPI validation error |

### Requirements for Anki

- Anki must be open on the same computer as the backend.
- The AnkiConnect add-on must be installed (code `2055492159`), and Anki restarted afterward.
- The `Basic` note type must have the fields `Front` and `Back`.

### Calling the API from the extension

- Add `http://127.0.0.1:8000/*` to `host_permissions` in `manifest.json`.
- CORS is already allowed in the backend.
- Calling the API from the background service worker (and passing the result to the content script with `chrome.runtime.sendMessage`) is the safest approach.

### Changing the API

If the JSON shape changes, tell the team first. Changes can break the extension.

## Sharing the database

`dictionary.db` is not stored in Git (`*.db` is in `.gitignore`). To give it to a teammate, send the file (zip it if it is large) and have them put it in `backend/database/`. To update, stop the server, replace the file, and start it again. Name each copy with a date (for example `dictionary-2026-11-20.db`) so you know which version is in use. `git pull` never touches this file.

## Git notes

- Never commit `backend/data/`, `*.db`, `.venv/`, `__pycache__/`, or `.pytest_cache/`. They are in `.gitignore`. GitHub rejects files over 100 MB.
- Run `git pull` before you start work and before you push.

## Credits

- Dictionary data: JMdict/EDRDG, licensed under CC BY-SA 4.0 (https://www.edrdg.org/). Accessed through the jmdict-simplified project.
- Example sentences: Tatoeba (https://tatoeba.org/), licensed under CC BY 2.0 FR.
- Lemmatization: spaCy (https://spacy.io/) with the `en_core_web_sm` model.
- Word frequency: wordfreq (https://github.com/rspeer/wordfreq).