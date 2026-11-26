import json
import sqlite3
from pathlib import Path
from seed_top_words import TOP_ENTRIES


DB_PATH = Path(__file__).parent / "database" / "dictionary.db"

# Hand-written entries. They REPLACE whatever the JMdict import made for that word.
# Words must already be normalized (lowercase, no punctuation except ').
# Format: word -> list of (type, [meanings]), best sense first.
ENTRIES = {
    "give up": [("phrasal verb", ["諦める", "やめる", "降参する"])],
    "dog": [("noun", ["犬", "イヌ", "わんこ"])],
    "go": [
        ("verb", ["行く", "出かける", "向かう"]),
        ("verb", ["進む", "うまくいく", "動く"]),
        ("verb", ["〜になる"]),
        ("noun", ["順番", "試み"]),
    ],
    "take": [
        ("verb", ["取る", "持っていく", "連れていく"]),
        ("verb", ["(時間が)かかる"]),
        ("verb", ["受ける", "飲む"]),
        ("verb", ["乗る"]),
    ],
    "make": [
        ("verb", ["作る", "つくる"]),
        ("verb", ["〜させる"]),
        ("verb", ["稼ぐ"]),
        ("verb", ["〜になる", "〜にする"]),
    ],
    "come": [
        ("verb", ["来る", "やって来る"]),
        ("verb", ["着く", "到着する"]),
        ("verb", ["実現する", "〜になる"]),
    ],
    "put": [
        ("verb", ["置く", "入れる"]),
        ("verb", ["書く", "記入する"]),
        ("verb", ["表現する", "言う"]),
    ],
    "have": [
        ("verb", ["持っている", "所有する"]),
        ("verb", ["食べる", "飲む"]),
        ("verb", ["(経験を)する", "過ごす"]),
        ("verb", ["〜させる", "〜してもらう"]),
    ],
    "do": [
        ("verb", ["する", "行う"]),
        ("verb", ["(仕事を)している"]),
        ("verb", ["足りる", "間に合う"]),
    ],
    "see": [
        ("verb", ["見える", "見る"]),
        ("verb", ["会う", "訪ねる"]),
        ("verb", ["わかる", "理解する"]),
    ],
    "stare": [
        ("verb", ["じっと見る", "見つめる", "じろじろ見る"]),
        ("noun", ["凝視", "じっと見ること"]),
    ],
    "look": [
        ("verb", ["見る", "目を向ける"]),
        ("verb", ["〜に見える", "〜のようだ"]),
        ("noun", ["目つき", "見た目"]),
    ],
    "grocery store": [("noun", ["食料品店", "食料品店(スーパー)", "八百屋"])],
    "grocery": [("noun", ["食料品", "食料雑貨"])],
    "turn": [
        ("verb", ["回る", "回す"]),
        ("verb", ["曲がる", "向きを変える"]),
        ("verb", ["〜になる", "変わる"]),
        ("noun", ["順番", "回転"]),
    ],
    "run": [
        ("verb", ["走る", "駆ける"]),
        ("verb", ["経営する", "運営する"]),
        ("verb", ["動く", "流れる"]),
        ("noun", ["ラン", "走ること", "連続"]),
    ],
    "every single": [("expression", ["ありとあらゆる", "一つ残らず", "すべての"])],
    "single": [
        ("adjective", ["単一の", "たった一つの", "独身の"]),
        ("noun", ["シングル", "独身者"]),
    ],
    "bring": [
        ("verb", ["持ってくる", "連れてくる"]),
        ("verb", ["もたらす", "引き起こす"]),
    ],
    "collapse": [
        ("verb", ["崩れる", "倒壊する", "崩壊する", "倒れる"]),
        ("noun", ["崩壊", "倒壊", "暴落"]),
    ],

    "run out of": [("phrasal verb", ["〜を使い果たす", "〜がなくなる"])],
    "break": [
        ("verb", ["壊す", "割る", "折る", "壊れる"]),
        ("verb", ["中断する", "破る"]),
        ("noun", ["休憩", "小休止", "チャンス"]),
    ],
    "give away": [
        ("phrasal verb", ["無料で配る", "あげる", "譲る"]),
        ("phrasal verb", ["うっかり漏らす", "暴露する"]),
    ],
    "go off": [
        ("phrasal verb", ["爆発する", "鳴り出す"]),
        ("phrasal verb", ["立ち去る", "腐る"]),
    ],
    "make it": [
        ("phrasal verb", ["間に合う", "成功する", "うまくいく"]),
    ],
    "come over": [
        ("phrasal verb", ["遊びに来る", "立ち寄る"]),
    ],
    "gotta": [("contraction", ["〜しなきゃ", "〜しなければならない"])],
    "kinda": [("contraction", ["ちょっと", "なんか〜っぽい", "まあ"])],
    "lemme": [("contraction", ["〜させて", "ちょっと〜させて"])],
    "ain't": [("contraction", ["〜じゃない", "〜ではない"])],
    "give me a break": [("expression", ["勘弁してよ", "いい加減にして", "冗談でしょ"])],
    "give us a break": [("expression", ["勘弁してよ", "いい加減にして"])],
    "get": [
        ("verb", ["手に入れる", "得る", "もらう", "買う"]),  # obtain / receive
        ("verb", ["〜になる", "〜してくる"]),  # become
        ("verb", ["着く", "到着する"]),  # arrive
        ("verb", ["わかる", "理解する"]),  # understand
    ],
    "english": [
        ("noun", ["英語"]),
        ("noun", ["イギリス人", "英国人"]),
        ("adjective", ["英語の", "イギリスの", "英国の"]),
    ],
    "arabic": [
        ("noun", ["アラビア語"]),
        ("adjective", ["アラビアの", "アラビア語の"]),
    ],
    "arab": [
        ("noun", ["アラブ人"]),
        ("adjective", ["アラブの"]),
    ],
    "british": [
        ("noun", ["イギリス人", "英国人"]),
        ("adjective", ["イギリスの", "英国の"]),
    ],
    "hang out": [("phrasal verb", ["遊ぶ", "たむろする", "一緒に過ごす"])],
    "gonna": [("contraction", ["〜するつもり", "〜しようとしている"])],
    "wanna": [("contraction", ["〜したい"])],
    "what's up": [("expression", ["やあ", "どうしたの", "調子はどう"])],
    "no way": [("expression", ["まさか", "マジで！？", "絶対だめ"])],
    "run": [
        ("verb", ["走る", "運営する", "流れる"]),
        ("noun", ["ラン", "走ること", "連続"]),
    ],
    "african american": [
        ("noun", ["アフリカ系アメリカ人"]),
        ("adjective", ["アフリカ系アメリカ人の"]),
    ],
    "asian american": [
        ("noun", ["アジア系アメリカ人"]),
        ("adjective", ["アジア系アメリカ人の"]),
    ],
    "native american": [
        ("noun", ["アメリカ先住民", "ネイティブアメリカン"]),
        ("adjective", ["アメリカ先住民の"]),
    ],
    "south american": [
        ("noun", ["南米人", "南アメリカ人"]),
        ("adjective", ["南米の", "南アメリカの"]),
    ],
    "north american": [
        ("noun", ["北米人", "北アメリカ人"]),
        ("adjective", ["北米の", "北アメリカの"]),
    ],
    "false": [
        ("adjective", ["間違った", "誤った", "嘘の", "虚偽の"]),
        ("adjective", ["偽の", "人工の", "疑似の"]),
    ],
    "south korea": [("noun", ["韓国", "大韓民国"])],
    "north korea": [("noun", ["北朝鮮", "朝鮮民主主義人民共和国"])],
    "korea": [("noun", ["韓国", "朝鮮半島"])],
    "united states": [("noun", ["アメリカ合衆国", "アメリカ", "米国"])],
    "united kingdom": [("noun", ["イギリス", "英国", "連合王国"])],
    "european union": [("noun", ["欧州連合", "EU"])],
    "united nations": [("noun", ["国際連合", "国連"])],
}
ENTRIES.update(TOP_ENTRIES)
# (English word, country in Japanese, language in Japanese or None)
# (英語, 国名, 言語名 / なければ None)
NATIONALITIES = [
    # Europe / ヨーロッパ
    ("russian", "ロシア", "ロシア語"),
    ("ukrainian", "ウクライナ", "ウクライナ語"),
    ("polish", "ポーランド", "ポーランド語"),
    ("german", "ドイツ", "ドイツ語"),
    ("french", "フランス", "フランス語"),
    ("spanish", "スペイン", "スペイン語"),
    ("italian", "イタリア", "イタリア語"),
    ("portuguese", "ポルトガル", "ポルトガル語"),
    ("dutch", "オランダ", "オランダ語"),
    ("swedish", "スウェーデン", "スウェーデン語"),
    ("norwegian", "ノルウェー", "ノルウェー語"),
    ("danish", "デンマーク", "デンマーク語"),
    ("finnish", "フィンランド", "フィンランド語"),
    ("greek", "ギリシャ", "ギリシャ語"),
    ("turkish", "トルコ", "トルコ語"),
    ("czech", "チェコ", "チェコ語"),
    ("hungarian", "ハンガリー", "ハンガリー語"),
    ("romanian", "ルーマニア", "ルーマニア語"),
    ("swiss", "スイス", None),
    ("irish", "アイルランド", "アイルランド語"),
    ("belgian", "ベルギー", None),
    ("austrian", "オーストリア", None),
    # Asia / アジア
    ("japanese", "日本", "日本語"),
    ("chinese", "中国", "中国語"),
    ("korean", "韓国", "韓国語"),
    ("thai", "タイ", "タイ語"),
    ("vietnamese", "ベトナム", "ベトナム語"),
    ("indonesian", "インドネシア", "インドネシア語"),
    ("filipino", "フィリピン", "フィリピン語"),
    ("indian", "インド", None),
    ("pakistani", "パキスタン", None),
    ("iranian", "イラン", None),
    ("iraqi", "イラク", None),
    ("israeli", "イスラエル", None),
    ("saudi", "サウジアラビア", None),
    # Americas / 南北アメリカ
    ("american", "アメリカ", None),
    ("canadian", "カナダ", None),
    ("mexican", "メキシコ", None),
    ("brazilian", "ブラジル", None),
    ("argentine", "アルゼンチン", None),
    ("colombian", "コロンビア", None),
    ("cuban", "キューバ", None),
    # Oceania / オセアニア
    ("australian", "オーストラリア", None),
    # Africa / アフリカ
    ("egyptian", "エジプト", None),
    ("nigerian", "ナイジェリア", None),
    ("kenyan", "ケニア", None),
    ("ethiopian", "エチオピア", None),
    # Middle East / 中東
    ("syrian", "シリア", None),
    ("lebanese", "レバノン", None),
    ("jordanian", "ヨルダン", None),
    ("kuwaiti", "クウェート", None),
    ("qatari", "カタール", None),
    ("omani", "オマーン", None),
    ("yemeni", "イエメン", None),
    ("bahraini", "バーレーン", None),
    ("emirati", "アラブ首長国連邦", None),
    ("afghan", "アフガニスタン", None),
    # South and Southeast Asia / 南アジア・東南アジア
    ("bangladeshi", "バングラデシュ", None),
    ("nepalese", "ネパール", None),
    ("sri lankan", "スリランカ", None),
    ("malaysian", "マレーシア", None),
    ("singaporean", "シンガポール", None),
    ("cambodian", "カンボジア", None),
    ("laotian", "ラオス", None),
    ("taiwanese", "台湾", None),
    # Africa / アフリカ
    ("moroccan", "モロッコ", None),
    ("algerian", "アルジェリア", None),
    ("tunisian", "チュニジア", None),
    ("libyan", "リビア", None),
    ("sudanese", "スーダン", None),
    ("ghanaian", "ガーナ", None),
    ("ugandan", "ウガンダ", None),
    ("tanzanian", "タンザニア", None),
    ("south african", "南アフリカ", None),
    ("senegalese", "セネガル", None),
    ("ivorian", "コートジボワール", None),
    ("cameroonian", "カメルーン", None),
    ("zimbabwean", "ジンバブエ", None),
    ("zambian", "ザンビア", None),
    ("congolese", "コンゴ", None),
    ("angolan", "アンゴラ", None),
    ("rwandan", "ルワンダ", None),
    ("malian", "マリ", None),
    # South and Central America, Caribbean / 中南米・カリブ
    ("chilean", "チリ", None),
    ("peruvian", "ペルー", None),
    ("venezuelan", "ベネズエラ", None),
    ("ecuadorian", "エクアドル", None),
    ("bolivian", "ボリビア", None),
    ("uruguayan", "ウルグアイ", None),
    ("paraguayan", "パラグアイ", None),
    ("panamanian", "パナマ", None),
    ("costa rican", "コスタリカ", None),
    ("guatemalan", "グアテマラ", None),
    ("honduran", "ホンジュラス", None),
    ("salvadoran", "エルサルバドル", None),
    ("nicaraguan", "ニカラグア", None),
    ("dominican", "ドミニカ共和国", None),
    ("jamaican", "ジャマイカ", None),
    ("haitian", "ハイチ", None),
    ("puerto rican", "プエルトリコ", None),
    # Europe and Oceania / ヨーロッパ・オセアニア
    ("cypriot", "キプロス", None),
    ("monacan", "モナコ", None),
    ("new zealander", "ニュージーランド", None),
    # Others
    ("peruvian", "ペルー", None),
    # Regions / 地域
    ("south american", "南米", None),
    ("north american", "北米", None),
    ("central american", "中米", None),
    ("latin american", "ラテンアメリカ", None),
    ("european", "ヨーロッパ", None),
    ("asian", "アジア", None),
    ("african", "アフリカ", None),
    ("southeast asian", "東南アジア", None),
    ("east asian", "東アジア", None),
    ("middle eastern", "中東", None),
]

for eng, country, language in NATIONALITIES:
    senses = [
        ("noun", [f"{country}人"]),
        ("adjective", [f"{country}の"]),
    ]
    if language:
        senses.insert(1, ("noun", [language]))
    # Do not overwrite a hand-written entry of the same word
    # 同じ単語の手書きエントリがあれば上書きしない
    ENTRIES.setdefault(eng, senses)


def main():
    conn = sqlite3.connect(DB_PATH)
    # Make sure the table exists (normally import_jmdict.py created it)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS senses (
            id       INTEGER PRIMARY KEY,
            word     TEXT NOT NULL,
            type     TEXT NOT NULL,
            meanings TEXT NOT NULL,
            position INTEGER NOT NULL
        )
        """
    )
    conn.execute("CREATE INDEX IF NOT EXISTS idx_senses_word ON senses(word)")

    for word, senses in ENTRIES.items():
        # Delete the automatic rows first, then insert ours
        conn.execute("DELETE FROM senses WHERE word = ?", (word,))
        for position, (word_type, meanings) in enumerate(senses):
            conn.execute(
                "INSERT INTO senses (word, type, meanings, position) VALUES (?, ?, ?, ?)",
                (word, word_type, json.dumps(meanings, ensure_ascii=False), position),
            )

    conn.commit()
    conn.close()
    print(f"Seeded {len(ENTRIES)} words")


if __name__ == "__main__":
    main()