import spacy

# Load the model ONCE when the server starts (loading per request would be slow)
# サーバー起動時に1回だけモデルを読み込む（リクエストごとだと遅い）
_nlp = spacy.load("en_core_web_sm", disable=["parser", "ner"])


def lemmatize(text: str) -> str:
    # "gave up" -> "give up", "dogs" -> "dog"
    # 活用形を見出し語の形に戻す
    return " ".join(token.lemma_.lower() for token in _nlp(text))