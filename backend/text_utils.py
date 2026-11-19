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


# Small words that turn a verb into a phrasal verb ("give" + "up")
# 動詞を句動詞に変える小さな語
PARTICLES = {
    "up", "out", "in", "off", "on", "away", "back", "down",
    "over", "around", "along", "through", "into", "about",
}
# Pronouns that can sit between verb and particle ("give it up")
# 動詞と小さな語の間に入る代名詞
PRONOUNS = {"it", "him", "her", "them", "me", "you", "us", "this", "that"}