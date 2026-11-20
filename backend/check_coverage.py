import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "database" / "dictionary.db"

# Phrases you want to be sure about. Add more whenever you think of one.
CANDIDATES = [
    # get
    "get up", "get out", "get over", "get along", "get back", "get on", "get off",
    "get away", "get in", "get through", "get together",
    # go
    "go on", "go out", "go away", "go back", "go ahead", "go over", "go through", "go off",
    # take
    "take off", "take on", "take out", "take over", "take care of", "take back",
    "take up", "take away", "take a break",
    # make
    "make up", "make out", "make sure", "make it", "make sense", "make over",
    # come
    "come on", "come back", "come out", "come up", "come over", "come in", "come along",
    # put
    "put on", "put off", "put out", "put up", "put away", "put down", "put back",
    # give
    "give up", "give in", "give away", "give back", "give out", "give me a break",
    # others
    "look up", "look out", "look after", "look for", "turn on", "turn off",
    "turn up", "turn down", "turn out", "run out", "run away", "run into",
    "pick up", "break down", "break up", "bring up", "bring back", "call off",
    "keep up", "keep on", "hold on", "pull out", "work out", "find out",
    "figure out", "hang out", "show up", "set up", "sit down", "stand up",
    # slang / contractions
    "gonna", "wanna", "gotta", "kinda", "lemme", "ain't", "what's up", "no way",
    # core verbs
    "get", "go", "take", "make", "come", "put", "give", "have", "do",
    "see", "look", "turn", "run", "bring", "break",
]

MIN_EXAMPLES = 3


def main():
    conn = sqlite3.connect(DB_PATH)

    in_dict = {r[0] for r in conn.execute("SELECT DISTINCT word FROM senses")}
    counts = dict(conn.execute("SELECT word, COUNT(*) FROM examples GROUP BY word"))

    # Also check every multi-word entry in the dictionary that has a hand-written seed
    from seed import ENTRIES
    phrases = list(dict.fromkeys(CANDIDATES + [w for w in ENTRIES if " " in w]))

    missing, few, ok = [], [], []
    for p in phrases:
        if p not in in_dict:
            missing.append(p)
        elif counts.get(p, 0) < MIN_EXAMPLES:
            few.append((p, counts.get(p, 0)))
        else:
            ok.append(p)

    print(f"\n=== NOT IN DICTIONARY ({len(missing)}): add to seed.py ===")
    for p in missing:
        print("  ", p)

    print(f"\n=== IN DICTIONARY, FEWER THAN {MIN_EXAMPLES} EXAMPLES ({len(few)}): add to seed_examples.py ===")
    for p, c in sorted(few, key=lambda x: x[1]):
        print(f"   {p}: {c}")

    print(f"\n=== OK ({len(ok)}) ===")
    print("  ", ", ".join(ok))

    conn.close()


if __name__ == "__main__":
    main()