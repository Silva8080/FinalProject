import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "database" / "dictionary.db"

# Hand-picked examples. They REPLACE the automatic ones for that word.
# 手書きの例文。その単語の自動生成の例文を置き換える。
# Format: word -> list of (English, Japanese)
EXAMPLES = {
    "get": [
        ("I got a new phone yesterday.", "昨日、新しいスマホを手に入れた。"),
        ("It's getting cold.", "寒くなってきた。"),
        ("What time did you get home?", "何時に家に着いたの？"),
        ("I don't get it.", "意味がわからない。"),
    ],
    "make over": [
        ("She got a makeover at the salon.", "彼女はサロンでイメチェンした。"),
        ("They made over the old kitchen.", "彼らは古いキッチンを改装した。"),
        ("He made over the house to his son.", "彼は家を息子に譲渡した。"),
    ],
    "break down": [
        ("My car broke down on the highway.", "高速道路で車が故障した。"),
        ("She broke down in tears.", "彼女は泣き崩れた。"),
        ("Let's break down the cost.", "費用を内訳にして考えよう。"),
    ],
    "give us a break": [
        ("Oh, give us a break!", "もう勘弁してよ！"),
        ("Come on, give us a break.", "頼むから、大目に見てよ。"),
        ("Give us a break, we've been working all day.", "勘弁してよ、一日中働いてたんだから。"),
    ],
    "make sense": [
        ("That doesn't make sense.", "それは意味が通らない。"),
        ("Her explanation makes sense to me.", "彼女の説明は私には筋が通っている。"),
        ("It makes sense to leave early.", "早めに出るのが理にかなっている。"),
    ],
    "give out": [
        ("They gave out free tickets.", "彼らは無料チケットを配った。"),
        ("My voice gave out.", "声が出なくなった。"),
        ("The teacher gave out the tests.", "先生はテストを配った。"),
    ],
    "bring back": [
        ("This song brings back memories.", "この曲は思い出がよみがえる。"),
        ("Please bring back my book.", "私の本を返しに持ってきてね。"),
        ("They want to bring back the old rules.", "彼らは古いルールを復活させたい。"),
    ],
    "pull out": [
        ("He pulled out his wallet.", "彼は財布を取り出した。"),
        ("The car pulled out of the garage.", "車がガレージから出ていった。"),
        ("They pulled out of the deal.", "彼らは取引から手を引いた。"),
    ],
    "go": [
        ("I go to school by bus.", "私はバスで学校に行く。"),
        ("How is your new job going?", "新しい仕事はどう？"),
        ("The milk went bad.", "牛乳が腐った。"),
        ("It's your go.", "あなたの番だよ。"),
    ],
    "take": [
        ("Take this umbrella with you.", "この傘を持っていって。"),
        ("It takes two hours to get there.", "そこへ行くのに2時間かかる。"),
        ("Take this medicine twice a day.", "この薬を1日2回飲んでください。"),
        ("I take the train to work.", "電車で通勤している。"),
    ],
    "make": [
        ("She makes breakfast every morning.", "彼女は毎朝朝食を作る。"),
        ("The movie made me cry.", "その映画に泣かされた。"),
        ("He makes a lot of money.", "彼はたくさん稼いでいる。"),
        ("You'll make a good teacher.", "あなたはいい先生になるよ。"),
    ],
    "come": [
        ("Come here, please.", "こっちに来て。"),
        ("Spring has come.", "春が来た。"),
        ("My dream came true.", "夢が叶った。"),
    ],
    "put": [
        ("Put the book on the table.", "本をテーブルの上に置いて。"),
        ("I put sugar in my coffee.", "コーヒーに砂糖を入れる。"),
        ("Put your name here.", "ここに名前を書いてください。"),
        ("Let me put it another way.", "別の言い方をさせて。"),
    ],
    "break": [
        ("He broke the window.", "彼は窓を割った。"),
        ("Let's take a break.", "休憩しよう。"),
        ("She broke her promise.", "彼女は約束を破った。"),
    ],
    "gotta": [
        ("I gotta go.", "もう行かなきゃ。"),
        ("You gotta try this.", "これ絶対食べてみて。"),
        ("We gotta hurry.", "急がなきゃ。"),
    ],
    "kinda": [
        ("I'm kinda tired.", "ちょっと疲れた。"),
        ("It's kinda funny.", "なんかおかしいね。"),
        ("She's kinda shy.", "彼女はちょっと恥ずかしがり屋だ。"),
    ],
    "have": [
        ("I have two brothers.", "私には兄弟が2人いる。"),
        ("Let's have lunch.", "お昼を食べよう。"),
        ("We had a great time.", "とても楽しい時間を過ごした。"),
        ("I had my hair cut.", "髪を切ってもらった。"),
    ],
    "do": [
        ("What do you do on weekends?", "週末は何をしてるの？"),
        ("What do you do for a living?", "お仕事は何をされていますか？"),
        ("This will do.", "これで十分だよ。"),
    ],
    "see": [
        ("I can see the mountain from here.", "ここから山が見える。"),
        ("I'm seeing my doctor tomorrow.", "明日、医者に会う。"),
        ("I see what you mean.", "言いたいことはわかるよ。"),
    ],
    "look": [
        ("Look at that bird.", "あの鳥を見て。"),
        ("You look tired.", "疲れて見えるよ。"),
        ("Let me have a look.", "ちょっと見せて。"),
    ],
    "turn": [
        ("The wheel turns slowly.", "車輪はゆっくり回る。"),
        ("Turn left at the corner.", "角を左に曲がって。"),
        ("The leaves turned red.", "葉が赤くなった。"),
        ("It's your turn.", "あなたの番だよ。"),
    ],
    "run": [
        ("I run every morning.", "毎朝走っている。"),
        ("She runs a small shop.", "彼女は小さな店を経営している。"),
        ("The river runs through the town.", "川は町を流れている。"),
        ("We went for a run.", "走りに行った。"),
    ],
    "every single": [
        ("Every single person agreed.", "全員が一人残らず賛成した。"),
        ("I read every single page.", "1ページも残さず読んだ。"),
        ("She calls me every single day.", "彼女は毎日欠かさず電話してくる。"),
    ],
    "single": [
        ("I don't have a single dollar.", "1ドルも持っていない。"),
        ("Are you single?", "独身ですか？"),
        ("He bought a single ticket.", "彼は片道切符を1枚買った。"),
    ],
    "run out of": [
        ("We ran out of time.", "時間がなくなった。"),
        ("I'm running out of money.", "お金がなくなってきた。"),
        ("They ran out of food.", "彼らは食料を使い果たした。"),
    ],
    "bring": [
        ("Please bring your passport.", "パスポートを持ってきてください。"),
        ("The news brought tears to her eyes.", "そのニュースに彼女は涙ぐんだ。"),
    ],
    "lemme": [
        ("Lemme see.", "ちょっと見せて。"),
        ("Lemme help you.", "手伝わせて。"),
        ("Lemme think about it.", "ちょっと考えさせて。"),
    ],
    "ain't": [
        ("It ain't over yet.", "まだ終わってないよ。"),
        ("That ain't right.", "それは正しくない。"),
        ("I ain't afraid.", "怖くなんかない。"),
    ],
    "give away": [
        ("They are giving away free samples.", "彼らは無料サンプルを配っている。"),
        ("Don't give away the ending.", "結末をばらさないでね。"),
        ("I gave away my old clothes.", "古い服を人にあげた。"),
    ],
}


def main():
    conn = sqlite3.connect(DB_PATH)
    for word, pairs in EXAMPLES.items():
        conn.execute("DELETE FROM examples WHERE word = ?", (word,))
        conn.executemany(
            "INSERT INTO examples (word, english, japanese) VALUES (?, ?, ?)",
            [(word, en, ja) for en, ja in pairs],
        )
    conn.commit()
    conn.close()
    print(f"Seeded examples for {len(EXAMPLES)} words")


if __name__ == "__main__":
    main()