import httpx

# AnkiConnect address (Anki must be open)
# AnkiConnectのアドレス（Ankiを起動しておく必要がある）
ANKI_URL = "http://127.0.0.1:8765"
DECK_NAME = "EasyRead"
MODEL_NAME = "Basic"


class AnkiError(Exception):
    """Raised when something goes wrong talking to Anki. / Ankiとの通信で問題が起きたときのエラー"""


def _call(action: str, **params):
    # Send one request to AnkiConnect and return its result
    # AnkiConnectに1回リクエストを送り、結果を返す
    try:
        r = httpx.post(
            ANKI_URL,
            json={"action": action, "version": 6, "params": params},
            timeout=5,
        )
    except httpx.ConnectError:
        raise AnkiError("Cannot connect to Anki. Open Anki and install AnkiConnect.")
    data = r.json()
    if data.get("error"):
        raise AnkiError(data["error"])
    return data["result"]


def add_card(word: str, meaning: str, sentence: str = "") -> int:
    # Create the deck if needed (does nothing if it already exists)
    # デッキが無ければ作る（既にあれば何もしない）
    _call("createDeck", deck=DECK_NAME)

    back = meaning
    if sentence:
        back += "<br><br>" + sentence

    return _call(
        "addNote",
        note={
            "deckName": DECK_NAME,
            "modelName": MODEL_NAME,
            "fields": {"Front": word, "Back": back},
            "options": {"allowDuplicate": False},
            "tags": ["EasyRead"],
        },
    )