import spacy

# Load the model ONCE when the server starts (loading per request would be slow)
# サーバー起動時に1回だけモデルを読み込む（リクエストごとだと遅い）
_nlp = spacy.load("en_core_web_sm", disable=["parser", "ner"])


def lemmatize(text: str) -> str:
    # "gave up" -> "give up", "dogs" -> "dog"
    # 活用形を見出し語の形に戻す
    return " ".join(token.lemma_.lower() for token in _nlp(text))
def verb_tokens(sentence: str) -> set[str]:
    # Lowercase words that are used as verbs in this sentence
    # この文の中で動詞として使われている単語（小文字）
    return {t.text.lower() for t in _nlp(sentence) if t.pos_ in ("VERB", "AUX")}
def noun_tokens(sentence: str) -> set[str]:
    # Lowercase words used as nouns in this sentence
    # この文の中で名詞として使われている単語（小文字）
    return {t.text.lower() for t in _nlp(sentence) if t.pos_ in ("NOUN", "PROPN")}
VOWELS = "aeiou"


def rule_lemma(word: str, is_verb, is_word=None) -> str | None:
    # Spelling-rule lemma for -ing / -ed forms.
    # is_verb(w): w has a verb sense. is_word(w): w has any entry.
    # -ing / -ed 形のつづり規則による基本形
    is_word = is_word or is_verb
    for suffix in ("ing", "ed"):
        if not word.endswith(suffix) or len(word) <= len(suffix) + 2:
            continue
        stem = word[: -len(suffix)]
        cvc = False

        if len(stem) >= 3 and stem[-1] == stem[-2]:
            # Doubled consonant: running -> run
            candidates = [stem[:-1], stem]
        else:
            # consonant-vowel-consonant: hoping -> hope, staring -> stare
            cvc = (
                len(stem) >= 3
                and stem[-1] not in VOWELS + "wxy"
                and stem[-2] in VOWELS
                and stem[-3] not in VOWELS
            )
            candidates = [stem + "e", stem] if cvc else [stem, stem + "e"]

        for c in candidates:
            # The "+e" form of a cvc stem only needs to exist as a word
            # cvc語幹の「+e」形は、辞書にあれば十分とする
            check = is_word if (cvc and c == stem + "e") else is_verb
            if check(c):
                return c
    return None

# Words that look plural but are not / 複数形に見えるが複数形ではない語
NOT_PLURAL = {"news", "series", "species", "means", "physics", "politics",
              "mathematics", "lens", "gas", "bus", "yes", "this", "his"}


def plural_lemma(word: str, is_word) -> str | None:
    # Spelling-rule lemma for plurals: taxes -> tax, babies -> baby, cats -> cat
    # 複数形のつづり規則による基本形
    if word in NOT_PLURAL or len(word) <= 3 or not word.endswith("s"):
        return None
    if word.endswith(("ss", "us", "is")):
        return None

    candidates = []
    if word.endswith("ies"):
        candidates.append(word[:-3] + "y")      # babies -> baby
    if word.endswith("es"):
        candidates.append(word[:-2])            # taxes -> tax, boxes -> box
    candidates.append(word[:-1])                # cats -> cat, houses -> house

    for c in candidates:
        if is_word(c):
            return c
    return None