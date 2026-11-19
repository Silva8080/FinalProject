[English](README.md) | 日本語

# EasyRead

EasyReadは、日本人の英語学習者のための「逆Yomitan」です。YouTubeの英語字幕の単語にマウスを乗せると、日本語の意味と例文が表示され、ワンクリックでAnkiに保存できます。

## 現在の状況

プロトタイプです。バックエンド（レンマ化つきの辞書検索、例文、Ankiカード作成）は動作します。Chrome拡張機能は開発中です。

## プロジェクト構成

- `backend/`: FastAPIのバックエンド（辞書検索、Anki連携）
- `extension/`: Chrome拡張機能（字幕の検出、ホバーポップアップ）

## バックエンドの起動方法

フロントエンド担当の方は、バックエンドを起動しなくても大丈夫です。下の「API仕様」のサンプルJSONをモックデータとして使い、バックエンドは後から動かしてください。

### 1. データをダウンロードする（Gitには含まれません）

データファイルは大きいため `.gitignore` に入れています。コミットしないでください。

- **JMdict（英語版）:** GitHubの jmdict-simplified (scriptin) のReleasesから英語版JSONをダウンロードし、`backend/data/jmdict-eng.json` として保存します。
- **Tatoebaの文ペア（任意）:** manythings.org の `jpn-eng.zip` を解凍し、中のテキストファイルを `backend/data/jpn-eng.txt` として保存します。ない場合、自動の例文は作られません（手書きの例文は使えます）。

### 2. インストールとデータベースの作成

```
cd backend
uv sync
uv run python import_jmdict.py
uv run python seed.py
uv run python import_examples.py
uv run python seed_examples.py
```

スクリプトは**必ずこの順番**で実行してください。それぞれが前のスクリプトの結果に依存しています。

| スクリプト | 内容 |
| --- | --- |
| `import_jmdict.py` | JMdict（英語→日本語）から `senses` テーブルを作ります。テーブルは毎回作り直されます。 |
| `seed.py` | 手書きの意味データです。同じ単語の自動データを置き換えます。JMdictにない句動詞、イディオム、スラングもここに追加します。 |
| `import_examples.py` | Tatoebaから `examples` テーブルを作ります。`senses` の単語を読み込み、テーブルは毎回作り直されます。Tatoebaのファイルがない場合は省略できます。 |
| `seed_examples.py` | 手書きの例文です。同じ単語の自動の例文を置き換えます。 |

データやスクリプトを変更したときは、この順番で全部もう一度実行してください。`uv sync` で、レンマ化に使うspaCyと英語モデル（`en_core_web_sm`）、順位付けに使う `wordfreq` も一緒にインストールされます。

### 3. 不足している単語の確認（任意）

```
uv run python check_coverage.py
```

辞書にないフレーズや、例文が3件未満のフレーズを一覧で表示します。それらを `seed.py` と `seed_examples.py` に追加し、再構築してからもう一度実行してください。新しいフレーズは、スクリプト内の `CANDIDATES` リストに追加します。

### 4. サーバーを起動する

```
uv run uvicorn main:app --reload
```

起動時にspaCyのモデルを1回だけ読み込むため、最初の起動は少し時間がかかります。

APIは http://127.0.0.1:8000 で動き、API仕様のページは http://127.0.0.1:8000/docs で見られます。

## データについて

- **自動生成のデータ:** JMdictは日本語→英語の辞書なので、インポート時に逆引きしています。具体的な名詞はうまくいきますが、基本動詞（`get`、`go`、`take`、`make`）や、JMdictにほとんど載っていない句動詞、イディオム、スラングは苦手です。
- **手書きのデータ:** `seed.py` と `seed_examples.py` に、それらの単語を手書きで入れています。これらのファイルの日本語は、公開前にネイティブの方に確認してもらってください。
- **例文:** Tatoebaの文は、単語の形が完全に一致するものだけが対象で、最も長い既知のフレーズが優先されます（"give up" を含む文は `give` ではなく `give up` に入ります）。同じ単語の別の意味は、自動の例文では区別されません。

## API仕様

ベースURL: `http://127.0.0.1:8000`

### GET /lookup?word=racket

英単語またはフレーズを検索します。

成功 (200 OK):

```json
{
  "word": "racket",
  "senses": [
    { "type": "noun", "meanings": ["ラケット"] }
  ],
  "examples": [
    { "english": "You have the same racket as I have.", "japanese": "君は僕と同じラケットを持っている。" },
    { "english": "Tom laid his racket on the ground.", "japanese": "トムはラケットを地面に置いた。" },
    { "english": "I bought this racket at a 20 percent discount.", "japanese": "私はこのラケットを２０％引きで買った。" }
  ]
}
```

- `word`: 実際に見つかった辞書の見出し語です。送った文字列そのままではありません。まず入力を正規化（小文字化、句読点の除去）し、完全一致しない場合は基本形（レンマ）に直してもう一度検索します。例えば、`Give up!` は `give up` を返し、`gave up` も `give up` を返します。`running` は `run` を返します。
- `senses`: 意味のまとまりのリストで、重要な順に並んでいます。各要素は品詞 `type` と、日本語の意味のリスト `meanings` を持ちます。
- `examples`: 日本語訳つきの例文のリストで、最大3件です。空のリスト `[]` になることがある（珍しい単語やフレーズの場合）ので、ポップアップ側で空の場合を処理してください。

見つからない場合 (404 Not Found):

```json
{ "detail": "Word not found" }
```

現時点の制限:

- レンマ化は文脈なしで単語やフレーズ単体に対して行うため、曖昧な単語（例: `left`）では間違うことがあります。
- 文章全体の中からフレーズを探す機能はまだありません。"I won't give up" の `give` にマウスを乗せても、`give up` ではなく `give` が返ります。1回のリクエストでは、1つの単語またはフレーズを送ってください。
- 例文は単語の形が完全に一致するものだけが対象です。`give up` は "Don't give up." を見つけますが、"He gave up." は見つけません。

### POST /anki/add

AnkiConnect経由でAnkiのカードを作成します。

リクエストボディ:

```json
{
  "word": "give up",
  "meaning": "諦める",
  "sentence": "I won't give up."
}
```

- `word` と `meaning` は必須です。
- `sentence` は省略できます。省略した場合や空の場合は、その単語の最初の例文（英語と日本語訳）が使われます。例文がなければ、例文なしでカードが作成されます。

成功 (200 OK):

```json
{ "status": "ok", "note_id": 1234567890 }
```

エラー:

| ステータス | 意味 | ボディ |
| --- | --- | --- |
| 409 | 同じカードが既にある | `{ "detail": "Card already exists" }` |
| 503 | Ankiに接続できない | `{ "detail": "Cannot connect to Anki. Open Anki and install AnkiConnect." }` |
| 400 | その他のAnkiのエラー | `{ "detail": "<Ankiからのメッセージ>" }` |
| 422 | リクエストの形が不正（例: `word` がない） | FastAPIのバリデーションエラー |

カードの形式: デッキは `EasyRead`、ノートタイプは `Basic` です。表面は単語、裏面は意味とその下に例文が入ります。デッキは自動で作成されます。

### Ankiの利用条件

- バックエンドと同じPCでAnkiを起動しておく必要があります。
- アドオンAnkiConnect（コード `2055492159`）をインストールし、Ankiを再起動してください。
- `Basic` ノートタイプに `Front` と `Back` のフィールドが必要です。

### 拡張機能からの呼び出しについて

- `manifest.json` の `host_permissions` に `http://127.0.0.1:8000/*` を追加してください。
- CORSはバックエンド側で許可済みです。
- バックグラウンド（service worker）でAPIを呼び出し、結果を `chrome.runtime.sendMessage` でcontent scriptに渡す方法が最も安全です。

### APIを変更するとき

JSONの形を変えるときは、必ず事前にチームに連絡します。拡張機能のコードが動かなくなる可能性があるためです。

## Gitに関する注意

- `backend/data/`、`*.db`、`.venv/`、`__pycache__/` は絶対にコミットしないでください。`.gitignore` に入っています。GitHubは100MBを超えるファイルを受け付けません。
- 作業を始める前と、pushする前に `git pull` を実行してください。

## クレジット

- 辞書データ: JMdict/EDRDG（CC BY-SA 4.0）https://www.edrdg.org/ 。jmdict-simplified プロジェクト経由で利用しています。
- 例文: Tatoeba（CC BY 2.0 FR）https://tatoeba.org/
- レンマ化: spaCy（https://spacy.io/）と `en_core_web_sm` モデル
- 単語の頻度: wordfreq（https://github.com/rspeer/wordfreq）