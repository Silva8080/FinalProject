# Corrections for the 300 most frequent English words (from review_top_words.csv).
# 頻出300語のレビュー結果の修正データ。
#
# Format: word -> list of (type, [meanings]), best sense first.
# Written by an AI reviewer, NOT a native speaker: have a native speaker check it.
# AIが作成した下書きです。ネイティブの方の確認が必要です。
#
# Types used (add the new ones to TYPE_JA in text_utils.py):
#   preposition 前置詞 / article 冠詞 / auxiliary verb 助動詞 / determiner 限定詞

TOP_ENTRIES = {
    # ---- articles, prepositions, conjunctions / 冠詞・前置詞・接続詞 ----
    "the": [("article", ["その", "あの", "（特定のものを指す。訳さないことが多い）"])],
    "a": [("article", ["一つの", "ある", "（訳さないことが多い）"])],
    "an": [("article", ["一つの", "ある", "（訳さないことが多い）"])],
    "to": [
        ("preposition", ["〜へ", "〜に", "〜まで"]),
        ("expression", ["〜すること", "〜するために（動詞の前につく不定詞のto）"]),
    ],
    "and": [("conjunction", ["そして", "〜と", "〜や", "〜して"])],
    "of": [("preposition", ["〜の", "〜のうち", "〜について"])],
    "in": [
        ("preposition", ["〜の中に", "〜で", "〜に（月・年・季節）"]),
        ("adverb", ["中に", "中へ"]),
    ],
    "for": [
        ("preposition", ["〜のために", "〜に対して", "〜の間"]),
        ("conjunction", ["というのも〜だから（文語）"]),
    ],
    "on": [
        ("preposition", ["〜の上に", "〜に（曜日・日付）", "〜について"]),
        ("adverb", ["続けて", "身につけて", "作動して"]),
    ],
    "with": [("preposition", ["〜と一緒に", "〜を使って", "〜を持った"])],
    "as": [
        ("preposition", ["〜として"]),
        ("conjunction", ["〜のとき", "〜のように", "〜なので"]),
    ],
    "at": [("preposition", ["〜で", "〜に（時刻）", "〜を目がけて"])],
    "by": [("preposition", ["〜によって", "〜のそばに", "〜までに"])],
    "but": [("conjunction", ["しかし", "でも", "だが"])],
    "from": [("preposition", ["〜から", "〜出身の"])],
    "or": [("conjunction", ["または", "あるいは", "それとも"])],
    "so": [
        ("adverb", ["とても", "そんなに", "そう"]),
        ("conjunction", ["だから", "それで", "なので"]),
    ],
    "if": [("conjunction", ["もし〜なら", "〜かどうか"])],
    "about": [
        ("preposition", ["〜について", "〜のあたりに"]),
        ("adverb", ["およそ", "約"]),
    ],
    "when": [
        ("conjunction", ["〜のとき", "〜するときに"]),
        ("adverb", ["いつ"]),
    ],
    "after": [
        ("preposition", ["〜の後に", "〜のあとで"]),
        ("conjunction", ["〜してから"]),
        ("adverb", ["後に", "あとで"]),
    ],
    "before": [
        ("preposition", ["〜の前に"]),
        ("conjunction", ["〜する前に"]),
        ("adverb", ["以前に", "前に"]),
    ],
    "into": [("preposition", ["〜の中へ", "〜に（変わる）"])],
    "than": [("conjunction", ["〜より", "〜よりも"])],
    "because": [("conjunction", ["なぜなら", "〜なので", "〜だから"])],
    "since": [
        ("preposition", ["〜以来"]),
        ("conjunction", ["〜して以来", "〜なので"]),
    ],
    "until": [
        ("preposition", ["〜まで"]),
        ("conjunction", ["〜するまで"]),
    ],
    "while": [
        ("conjunction", ["〜している間", "一方で", "〜だが"]),
        ("noun", ["しばらくの間", "少しの間"]),
    ],
    "though": [
        ("conjunction", ["〜だけれども", "〜にもかかわらず"]),
        ("adverb", ["でも", "もっとも"]),
    ],
    "through": [
        ("preposition", ["〜を通って", "〜を通じて", "〜によって"]),
        ("adverb", ["通り抜けて", "最後まで"]),
    ],
    "during": [("preposition", ["〜の間に", "〜中に"])],
    "without": [("preposition", ["〜なしで", "〜なしに"])],
    "against": [("preposition", ["〜に反対して", "〜に対して", "〜にもたれて"])],
    "under": [("preposition", ["〜の下に", "〜未満の"]), ("adverb", ["下に"])],
    "between": [("preposition", ["〜の間に", "〜の間で"])],
    "around": [
        ("preposition", ["〜のまわりに", "〜ごろ"]),
        ("adverb", ["まわりに", "あちこちに", "およそ"]),
    ],
    "over": [
        ("preposition", ["〜の上に", "〜を越えて", "〜の間に"]),
        ("adverb", ["終わって", "向こうへ", "繰り返して"]),
    ],
    "up": [
        ("adverb", ["上へ", "上に", "起きて"]),
        ("preposition", ["〜の上へ"]),
    ],
    "down": [
        ("adverb", ["下へ", "下に", "落ち込んで"]),
        ("preposition", ["〜を下って"]),
        ("noun", ["羽毛", "ダウン"]),
    ],
    "out": [("adverb", ["外へ", "外に", "なくなって", "不在で"])],
    "off": [
        ("adverb", ["離れて", "休みで", "消えて"]),
        ("preposition", ["〜から離れて"]),
    ],
    "away": [("adverb", ["離れて", "去って", "遠くに"])],

    # ---- be / auxiliaries / modals / be動詞・助動詞 ----
    "be": [
        ("verb", ["〜である", "〜だ", "いる", "ある"]),
        ("auxiliary verb", ["〜している（進行形）", "〜される（受け身）"]),
    ],
    "have": [
        ("verb", ["持っている", "所有する"]),
        ("verb", ["食べる", "飲む"]),
        ("verb", ["(経験を)する", "過ごす"]),
        ("verb", ["〜させる", "〜してもらう"]),
        ("auxiliary verb", ["〜した（現在完了）", "〜したことがある"]),
    ],
    "do": [
        ("verb", ["する", "行う"]),
        ("verb", ["(仕事を)している"]),
        ("verb", ["足りる", "間に合う"]),
        ("auxiliary verb", ["（疑問文・否定文を作る）", "〜しない（don't）"]),
    ],
    "can": [
        ("auxiliary verb", ["〜できる", "〜してもよい", "〜することがある"]),
        ("noun", ["缶"]),
    ],
    "could": [("auxiliary verb", ["〜できた", "〜かもしれない", "〜していただけませんか"])],
    "will": [
        ("auxiliary verb", ["〜するつもりだ", "〜だろう", "〜してくれませんか"]),
        ("noun", ["意志", "遺言"]),
    ],
    "would": [
        ("auxiliary verb", ["〜だろう", "〜するつもりだった", "〜してくれませんか（丁寧）", "よく〜したものだ"]),
    ],
    "should": [("auxiliary verb", ["〜すべきだ", "〜したほうがいい", "〜はずだ"])],
    "may": [("auxiliary verb", ["〜かもしれない", "〜してもよい"])],
    "might": [
        ("auxiliary verb", ["〜かもしれない"]),
        ("noun", ["力", "権力"]),
    ],
    "must": [("auxiliary verb", ["〜しなければならない", "〜に違いない"])],

    # ---- pronouns and determiners / 代名詞・限定詞 ----
    "i": [("pronoun", ["私", "僕", "俺"])],
    "you": [("pronoun", ["あなた", "君", "あなたたち"])],
    "it": [("pronoun", ["それ", "あれ", "（天気・時間などを表す。訳さないことが多い）"])],
    "this": [("pronoun", ["これ"]), ("determiner", ["この"])],
    "that": [
        ("pronoun", ["それ", "あれ"]),
        ("determiner", ["その", "あの"]),
        ("conjunction", ["〜ということ", "〜という"]),
    ],
    "these": [("pronoun", ["これら"]), ("determiner", ["これらの"])],
    "those": [("pronoun", ["それら", "あれら"]), ("determiner", ["それらの", "あれらの"])],
    "me": [("pronoun", ["私を", "私に"])],
    "him": [("pronoun", ["彼を", "彼に"])],
    "her": [
        ("determiner", ["彼女の"]),
        ("pronoun", ["彼女を", "彼女に"]),
    ],
    "us": [("pronoun", ["私たちを", "私たちに"])],
    "them": [("pronoun", ["彼らを", "彼らに", "それらを"])],
    "my": [("determiner", ["私の"])],
    "your": [("determiner", ["あなたの", "君の"])],
    "his": [("determiner", ["彼の"]), ("pronoun", ["彼のもの"])],
    "its": [("determiner", ["それの", "その"])],
    "our": [("determiner", ["私たちの"])],
    "their": [("determiner", ["彼らの", "それらの"])],
    "what": [
        ("pronoun", ["何", "何が", "〜するもの"]),
        ("determiner", ["どんな", "何の"]),
    ],
    "who": [("pronoun", ["誰", "〜する人"])],
    "which": [
        ("pronoun", ["どれ", "〜するところの（関係代名詞）"]),
        ("determiner", ["どの"]),
    ],
    "all": [
        ("determiner", ["すべての", "全部の"]),
        ("pronoun", ["すべて", "全部"]),
        ("adverb", ["まったく", "すっかり"]),
    ],
    "some": [
        ("determiner", ["いくつかの", "いくらかの", "ある"]),
        ("pronoun", ["いくつか", "いくらか"]),
    ],
    "any": [("determiner", ["（疑問・否定で）いくらかの", "何も〜ない", "どんな〜でも"])],
    "one": [
        ("determiner", ["一つの", "1つの"]),
        ("pronoun", ["一つ", "もの", "（一般の）人"]),
    ],
    "two": [("noun", ["2", "二つ"]), ("determiner", ["2つの", "2人の"])],
    "no": [
        ("determiner", ["〜がない", "少しも〜ない"]),
        ("interjection", ["いいえ", "いや"]),
    ],
    "many": [("determiner", ["多くの", "たくさんの"]), ("pronoun", ["多く", "多数"])],
    "much": [
        ("determiner", ["多くの（量）"]),
        ("adverb", ["とても", "はるかに"]),
        ("pronoun", ["多く"]),
    ],
    "more": [
        ("adverb", ["もっと", "さらに"]),
        ("determiner", ["もっと多くの"]),
    ],
    "most": [
        ("adverb", ["最も"]),
        ("determiner", ["ほとんどの", "最も多くの"]),
        ("pronoun", ["ほとんど"]),
    ],
    "few": [("determiner", ["ほとんどない（少数の）", "少しの（a few）"])],
    "little": [
        ("adjective", ["小さい", "少しの"]),
        ("adverb", ["ほとんど〜ない"]),
        ("pronoun", ["少し"]),
    ],
    "less": [
        ("adverb", ["より少なく"]),
        ("determiner", ["より少ない"]),
    ],
    "both": [("determiner", ["両方の"]), ("pronoun", ["両方", "どちらも"])],
    "each": [
        ("determiner", ["それぞれの", "各〜"]),
        ("pronoun", ["それぞれ"]),
    ],
    "every": [("determiner", ["すべての", "毎〜", "あらゆる"])],
    "another": [("determiner", ["もう一つの", "別の"]), ("pronoun", ["もう一つ", "別のもの"])],
    "other": [("adjective", ["他の", "ほかの", "別の"])],
    "such": [("determiner", ["そのような", "このような", "こんなに〜な"])],
    "same": [("adjective", ["同じ"]), ("pronoun", ["同じもの"])],
    "something": [("pronoun", ["何か", "あるもの"])],
    "anything": [("pronoun", ["何か", "何でも", "何も（否定文）"])],
    "nothing": [("pronoun", ["何も〜ない"])],
    "everything": [("pronoun", ["すべて", "何もかも"])],
    "everyone": [("pronoun", ["みんな", "全員", "誰でも"])],

    # ---- adverbs and others / 副詞ほか ----
    "not": [("adverb", ["〜ない", "〜ではない"])],
    "just": [
        ("adverb", ["ちょうど", "ただ〜だけ", "ほんの", "たった今"]),
        ("adjective", ["公正な"]),
    ],
    "now": [("adverb", ["今", "今すぐ", "今や"]), ("noun", ["今", "現在"])],
    "then": [("adverb", ["そのとき", "それから", "それなら"])],
    "there": [
        ("adverb", ["そこに", "そこで"]),
        ("pronoun", ["（There is 〜）〜がある", "〜がいる"]),
    ],
    "here": [("adverb", ["ここに", "ここで", "ここへ"])],
    "where": [
        ("adverb", ["どこに", "どこで", "どこへ"]),
        ("conjunction", ["〜するところ"]),
    ],
    "how": [("adverb", ["どのように", "どうやって", "どれくらい"])],
    "also": [("adverb", ["〜も", "また", "さらに"])],
    "only": [
        ("adverb", ["〜だけ", "ただ〜だけ"]),
        ("adjective", ["唯一の", "たった一つの"]),
    ],
    "too": [("adverb", ["〜もまた", "あまりにも〜すぎる"])],
    "even": [
        ("adverb", ["〜でさえ", "さらに"]),
        ("adjective", ["平らな", "偶数の"]),
    ],
    "still": [
        ("adverb", ["まだ", "今でも", "それでも"]),
        ("adjective", ["静かな", "じっとした"]),
    ],
    "yet": [
        ("adverb", ["まだ", "もう（疑問文）", "すでに"]),
        ("conjunction", ["しかし"]),
    ],
    "never": [("adverb", ["一度も〜ない", "決して〜ない"])],
    "ever": [("adverb", ["これまでに", "いつか", "今まで"])],
    "always": [("adverb", ["いつも", "常に", "ずっと"])],
    "again": [("adverb", ["また", "もう一度", "再び"])],
    "later": [("adverb", ["あとで", "のちほど"]), ("adjective", ["もっと後の"])],
    "actually": [("adverb", ["実は", "実際に", "本当に"])],
    "enough": [
        ("adjective", ["十分な"]),
        ("adverb", ["十分に"]),
        ("pronoun", ["十分"]),
    ],
    "please": [
        ("adverb", ["どうぞ", "お願いします", "〜してください"]),
        ("verb", ["喜ばせる"]),
    ],
    "yes": [("interjection", ["はい", "ええ", "うん"])],
    "thanks": [("interjection", ["ありがとう"]), ("noun", ["感謝"])],
    "thank": [("verb", ["感謝する", "礼を言う"])],
    "thank you": [("expression", ["ありがとう", "ありがとうございます"])],
    "well": [
        ("adverb", ["よく", "上手に", "十分に"]),
        ("interjection", ["ええと", "さて", "まあ"]),
        ("adjective", ["健康な"]),
        ("noun", ["井戸"]),
    ],
    "right": [
        ("adjective", ["正しい", "右の"]),
        ("noun", ["権利", "右"]),
        ("adverb", ["ちょうど", "すぐに", "右に"]),
    ],
    "left": [
        ("adjective", ["左の"]),
        ("noun", ["左"]),
        ("expression", ["leave の過去形・過去分詞（去った、残した）"]),
    ],
    "sure": [
        ("adjective", ["確かな", "確信している"]),
        ("adverb", ["もちろん"]),
    ],
    "however": [("adverb", ["しかし", "どんなに〜でも"])],

    # ---- verbs / 動詞 ----
    "say": [("verb", ["言う", "述べる", "〜と書いてある"])],
    "know": [("verb", ["知っている", "わかる", "知り合いである"])],
    "want": [("verb", ["欲しい", "〜したい", "〜してほしい"])],
    "need": [("verb", ["必要とする", "〜する必要がある"]), ("noun", ["必要", "ニーズ"])],
    "find": [("verb", ["見つける", "〜だとわかる"])],
    "keep": [("verb", ["保つ", "持ち続ける", "飼う", "〜し続ける"])],
    "let": [("verb", ["〜させる", "〜させてやる"])],
    "call": [
        ("verb", ["呼ぶ", "電話をかける", "〜と呼ぶ"]),
        ("noun", ["電話", "呼び声"]),
    ],
    "set": [
        ("verb", ["置く", "設定する", "セットする"]),
        ("noun", ["セット", "一式"]),
        ("adjective", ["決まった", "準備ができた"]),
    ],
    "care": [
        ("verb", ["気にする", "気にかける", "世話をする"]),
        ("noun", ["世話", "注意", "心配"]),
    ],
    "live": [
        ("verb", ["住む", "生きる", "暮らす"]),
        ("adjective", ["生の", "ライブの"]),
    ],
    "open": [
        ("verb", ["開く", "開ける"]),
        ("adjective", ["開いている", "公開の", "率直な"]),
    ],
    "mean": [
        ("verb", ["意味する", "〜のつもりで言う"]),
        ("adjective", ["意地悪な", "卑劣な"]),
    ],
    "own": [
        ("adjective", ["自分自身の"]),
        ("verb", ["所有する", "持つ"]),
    ],
    "back": [
        ("noun", ["背中", "後ろ", "裏"]),
        ("adverb", ["戻って", "後ろへ", "元の場所に"]),
        ("verb", ["支援する", "後ろに下がる"]),
    ],
    "think": [("verb", ["思う", "考える"])],
    "believe": [("verb", ["信じる", "思う"])],

    # ---- adjectives / 形容詞 ----
    "new": [("adjective", ["新しい", "新たな", "新規の"])],
    "old": [("adjective", ["古い", "年をとった", "〜歳の"])],
    "good": [
        ("adjective", ["良い", "いい", "上手な", "おいしい"]),
        ("noun", ["善", "利益"]),
    ],
    "best": [
        ("adjective", ["最も良い", "最高の"]),
        ("adverb", ["最もよく"]),
        ("noun", ["最善"]),
    ],
    "better": [
        ("adjective", ["より良い", "より上手な"]),
        ("adverb", ["より良く", "より上手に"]),
        ("verb", ["改善する"]),
    ],
    "great": [("adjective", ["素晴らしい", "偉大な", "大きな"])],
    "high": [("adjective", ["高い"]), ("adverb", ["高く"])],
    "free": [("adjective", ["無料の", "自由な", "暇な"])],
    "full": [("adjective", ["いっぱいの", "満員の", "完全な"])],
    "real": [("adjective", ["本当の", "現実の", "本物の"])],
    "hard": [
        ("adjective", ["難しい", "硬い", "きつい"]),
        ("adverb", ["一生懸命", "激しく"]),
    ],
    "different": [("adjective", ["違う", "異なる", "別の"])],
    "small": [("adjective", ["小さい", "少ない"])],
    "far": [("adjective", ["遠い"]), ("adverb", ["遠くに", "はるかに"])],
    "long": [
        ("adjective", ["長い"]),
        ("adverb", ["長い間"]),
        ("verb", ["切望する"]),
    ],
    "last": [
        ("adjective", ["最後の", "この前の", "先〜"]),
        ("adverb", ["最後に", "前回"]),
        ("verb", ["続く"]),
    ],
    "next": [
        ("adjective", ["次の", "来〜"]),
        ("adverb", ["次に"]),
    ],
    "first": [
        ("adjective", ["最初の", "第一の"]),
        ("adverb", ["最初に", "まず"]),
        ("noun", ["最初"]),
    ],
    "based": [("adjective", ["〜に基づいた", "〜に拠点を置く"])],
    "based on": [("preposition", ["〜に基づいて"])],

    # ---- nouns / 名詞 ----
    "day": [("noun", ["日", "昼間", "一日"])],
    "world": [("noun", ["世界", "世の中", "社会"])],
    "way": [("noun", ["道", "方法", "やり方", "〜の仕方"])],
    "people": [("noun", ["人々", "人たち", "国民"])],
    "home": [
        ("noun", ["家", "家庭", "故郷"]),
        ("adverb", ["家へ", "家に"]),
    ],
    "house": [
        ("noun", ["家", "住宅", "建物"]),
        ("verb", ["住まわせる", "収容する"]),
    ],
    "job": [("noun", ["仕事", "職", "役割"])],
    "party": [("noun", ["パーティー", "政党", "一行", "当事者"])],
    "order": [("noun", ["注文", "命令", "順序", "秩序"]), ("verb", ["注文する", "命じる"])],
    "lot": [("noun", ["たくさん", "土地", "くじ引き"])],
    "a lot": [("adverb", ["とても", "たくさん", "よく"])],
    "a lot of": [("determiner", ["たくさんの", "多くの"])],
    "mr": [("noun", ["〜さん", "〜氏", "〜様"])],
    "general": [
        ("adjective", ["一般的な", "全般的な"]),
        ("noun", ["将軍", "大将"]),
    ],
    "shit": [
        ("interjection", ["くそっ（卑語）", "ちくしょう（卑語）"]),
        ("noun", ["くそ（卑語）", "たわごと（卑語）"]),
    ],
}
