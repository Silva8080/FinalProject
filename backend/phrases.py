from text_utils import PARTICLES, PRONOUNS, normalize

MAX_LEN = 4  # longest phrase to try (words) / 試す最長のフレーズ（語数）


def candidate_phrases(sentence: str, word: str) -> list[str]:
    """
    Phrases from the sentence that contain the hovered word, longest first.
    文の中からホバーした単語を含むフレーズを、長い順に返す。
    """
    tokens = normalize(sentence).split()
    target = normalize(word)
    found = []  # (words used in the sentence, phrase)

    for p, tok in enumerate(tokens):
        if tok != target:
            continue

        # Adjacent windows of 2..MAX_LEN words that include position p
        # 位置 p を含む、2〜MAX_LEN語の連続したまとまり
        for n in range(MAX_LEN, 1, -1):
            for s in range(max(0, p - n + 1), p + 1):
                if s + n <= len(tokens):
                    found.append((n, " ".join(tokens[s:s + n])))

        # Separated phrasal verb: "give it up" -> "give up"
        # 分離した句動詞: "give it up" -> "give up"
        for s in range(max(0, p - 2), p + 1):
            if (
                s + 2 < len(tokens)
                and tokens[s + 1] in PRONOUNS
                and tokens[s + 2] in PARTICLES
            ):
                found.append((3, tokens[s] + " " + tokens[s + 2]))

    found.sort(key=lambda f: -f[0])   # stable: longest first / 長い順
    result, seen = [], set()
    for _, phrase in found:
        if phrase not in seen:
            seen.add(phrase)
            result.append(phrase)
    return result