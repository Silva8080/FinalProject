import spacy

nlp = spacy.load("en_core_web_sm", disable=["parser", "ner"])
for text in ["gave up", "running", "dogs", "hanging out", "went"]:
    print(text, "->", " ".join(t.lemma_ for t in nlp(text)))