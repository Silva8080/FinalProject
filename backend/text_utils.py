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