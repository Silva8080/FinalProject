# English Immersion App

Reverse Yomitan for Japanese learners of English: hover an English word in YouTube subtitles to see its Japanese meaning, then save it to Anki.

## Run the backend

```
cd backend
uv sync
uv run uvicorn main:app --reload
```

The API runs at http://127.0.0.1:8000 and the interactive docs are at http://127.0.0.1:8000/docs

## API

### GET /lookup?word=give up

200 OK:

```json
{ "word": "give up", "meaning": "諦める", "type": "phrasal verb" }
```

404 Not Found:

```json
{ "detail": "Word not found" }
```

## Project structure

- `backend/`: FastAPI backend (dictionary lookup, Anki integration)
- `extension/`: Chrome extension (subtitle detection, hover popup)