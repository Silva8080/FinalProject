import re


def normalize(text: str) -> str:
    # Lowercase / 小文字にする
    text = text.lower()
    # Curly apostrophe -> straight apostrophe / 曲がったアポストロフィを通常の ' に変換
    text = text.replace("’", "'")
    # Remove everything except letters, digits, spaces and '
    # 文字・数字・空白・' 以外を削除
    text = re.sub(r"[^\w\s']", "", text)
    # Trim the ends and collapse repeated spaces into one
    # 前後の空白を削除し、連続する空白を1つにする
    return " ".join(text.split())

# Words where 's is a contraction (it's = it is), not a possessive
# 's が所有格ではなく短縮形（it's = it is）になる語
CONTRACTION_S = {"it", "he", "she", "that", "what", "there", "here",
                 "let", "who", "where", "how", "when", "why"}


def strip_possessive(token: str) -> str:
    # korea's -> korea, countries' -> countries, but it's stays it's
    # 所有格の 's を取り除く（it's などの短縮形は残す）
    if token.endswith("'s") and token[:-2] not in CONTRACTION_S:
        return token[:-2]
    if token.endswith("s'"):
        return token[:-1]
    return token

# Small words that turn a verb into a phrasal verb ("give" + "up")
# 動詞を句動詞に変える小さな語
PARTICLES = {
    "up", "out", "in", "off", "on", "away", "back", "down",
    "over", "around", "along", "through", "into", "about",
}
# Pronouns that can sit between verb and particle ("give it up")
# 動詞と小さな語の間に入る代名詞
PRONOUNS = {"it", "him", "her", "them", "me", "you", "us", "this", "that"}

# Part-of-speech labels in Japanese / 品詞の日本語表記
TYPE_JA = {
    "noun": "名詞",
    "verb": "動詞",
    "phrasal verb": "句動詞",
    "adjective": "形容詞",
    "adverb": "副詞",
    "expression": "表現",
    "interjection": "感動詞",
    "pronoun": "代名詞",
    "particle": "助詞",
    "conjunction": "接続詞",
    "contraction": "短縮形",
    "idiom": "イディオム",
    "preposition": "前置詞",
    "article": "冠詞",
    "auxiliary verb": "助動詞",
    "determiner": "限定詞",
    "other": "その他",
}