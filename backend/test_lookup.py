from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def lookup(word, sentence=""):
    r = client.get("/lookup", params={"word": word, "sentence": sentence})
    return r.status_code, (r.json() if r.status_code == 200 else None)


def test_plain_word():
    status, data = lookup("racket")
    assert status == 200
    assert data["word"] == "racket"


def test_normalization():
    assert lookup("Give up!")[1]["word"] == "give up"


def test_lemma():
    assert lookup("gave up")[1]["word"] == "give up"
    assert lookup("dogs")[1]["word"] == "dog"


def test_not_found():
    assert lookup("asdfgh")[0] == 404


def test_phrase_in_sentence():
    assert lookup("give", "I won't give up")[1]["word"] == "give up"
    assert lookup("up", "I won't give up")[1]["word"] == "give up"
    assert lookup("give", "Give it up")[1]["word"] == "give up"
    assert lookup("take", "Take off your shoes")[1]["word"] == "take off"


def test_inflected_phrase_in_sentence():
    assert lookup("ran", "We ran out of time")[1]["word"] == "run out of"
    assert lookup("out", "We ran out of time")[1]["word"] == "run out of"


def test_fallback_to_word():
    assert lookup("dog", "The dog is big")[1]["word"] == "dog"


def test_dog_has_inu():
    meanings = [m for s in lookup("dog")[1]["senses"] for m in s["meanings"]]
    assert "犬" in meanings


def test_examples_are_not_phrasal_for_base_verb():
    examples = lookup("give")[1]["examples"]
    for e in examples:
        assert "give up" not in e["english"].lower()

def test_type_ja():
    senses = lookup("dog")[1]["senses"]
    assert senses[0]["type_ja"] == "名詞"

def test_noun_is_not_phrasal_verb():
    sentence = "A strike on a private home killed one person"
    assert lookup("strike", sentence)[1]["word"] == "strike"

def test_auto_phrase_does_not_hijack():
    assert lookup("dog", "The dog is big")[1]["word"] == "dog"
    assert lookup("out", "Get out of here")[1]["word"] != "every single"


def test_curated_phrase_matches():
    assert lookup("single", "every single person")[1]["word"] == "every single"

def test_verb_still_matches_phrasal_verb():
    assert lookup("strike", "They strike on a new idea")[1]["word"] == "strike on"

def test_inflected_form_uses_lemma():
    assert lookup("staring")[1]["word"] == "stare"
    assert lookup("collapsed")[1]["word"] == "collapse"
def test_spelling_rule_lemmas():
    assert lookup("hoping")[1]["word"] == "hope"
    assert lookup("singing")[1]["word"] == "sing"
    assert lookup("running")[1]["word"] == "run"
    assert lookup("starred")[1]["word"] == "star"

def test_nationality_has_person_and_language():
    meanings = [m for s in lookup("russian")[1]["senses"] for m in s["meanings"]]
    assert "ロシア人" in meanings
    assert "ロシア語" in meanings


def test_nationality_without_language():
    meanings = [m for s in lookup("american")[1]["senses"] for m in s["meanings"]]
    assert "アメリカ人" in meanings
    assert all("語" not in m for m in meanings)

def test_nationality_without_language_batch():
    for word, expected in [("chilean", "チリ人"), ("syrian", "シリア人"), ("south african", "南アフリカ人")]:
        meanings = [m for s in lookup(word)[1]["senses"] for m in s["meanings"]]
        assert expected in meanings

def test_plural_uses_singular():
    assert lookup("taxes")[1]["word"] == "tax"
    assert lookup("babies")[1]["word"] == "baby"
    assert lookup("dogs")[1]["word"] == "dog"


def test_not_plural():
    assert lookup("news")[1]["word"] == "news"

def test_regional_nationalities():
    assert lookup("american", "a South American nation")[1]["word"] == "south american"
    assert lookup("south", "a South American nation")[1]["word"] == "south american"
    assert lookup("american", "a North American country")[1]["word"] == "north american"
    assert lookup("american")[1]["word"] == "american"

def test_us_acronym():
    assert lookup("US")[1]["word"] == "united states"
    assert lookup("U.S.")[1]["word"] == "united states"
    assert lookup("us")[1]["word"] != "united states"

def test_possessive_phrase():
    s = "South Korea's trade minister said"
    assert lookup("South", s)[1]["word"] == "south korea"
    assert lookup("Korea's", s)[1]["word"] == "south korea"


def test_contraction_not_stripped():
    assert lookup("what's up")[1]["word"] == "what's up"

