[English](README.md) | 日本語

# EasyRead

EasyReadは、日本人の英語学習者のための「逆Yomitan」です。YouTubeの英語字幕の単語にマウスを乗せると、日本語の意味と例文が表示され、ワンクリックでAnkiに保存できます。

## 現在の状況

プロトタイプです。バックエンド（辞書検索とAnkiカード作成）は動作します。Chrome拡張機能は開発中です。

## プロジェクト構成

- `backend/`: FastAPIのバックエンド（辞書検索、Anki連携）
- `extension/`: Chrome拡張機能（字幕の検出、ホバーポップアップ）

## バックエンドの起動方法

フロントエンド担当の方は、バックエンドを起動しなくても大丈夫です。下の「API仕様」のサンプルJSONをモックデータとして使い、バックエンドは後から動かしてください。

### 1. データをダウンロードする（Gitには含まれません）

- **JMdict（英語版）:** GitHubの jmdict-simplified (scriptin) のReleasesから英語版JSONをダウンロードし、`backend/data/jmdict-eng.json` として保存します。
- **Tatoebaの文ペア（任意）:** manythings.org の `jpn-eng.zip` を解凍し、`backend/data/jpn-eng.txt` として保存します。ない場合、`examples` は常に空のリストになります。

### 2. インストールとデータベースの作成

```
cd backend
uv sync
uv run python import_jmdict.py
uv run python seed.py
uv run python import_examples.py    # Tatoebaのファイルがある場合のみ
```

スクリプトは必ずこの順番で実行してください。`import_jmdict.py` は `senses` テーブルを作り直すため、直後に `seed.py` を実行します（手書きのデータが自動生成のデータを置き換えます）。データを変更したときは、もう一度実行してください。

### 3. サーバーを起動する

```
uv run uvicorn main:app --reload
```

APIは http://127.0.0.1:8000 で動き、API仕様のページは http://127.0.0.1:8000/docs で見られます。

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
    { "english": "Choose your favorite racket.", "japanese": "好きなラケットを選びなさい。" }
  ]
}
```

- `word`: 正規化（小文字化、句読点の除去）した単語です。送った文字列そのままではありません。`Give up!` は `give up` として検索され、そのまま返ります。
- `senses`: 意味のまとまりのリストで、重要な順に並んでいます。各要素は品詞 `type` と、日本語の意味のリスト `meanings` を持ちます。
- `examples`: 日本語訳つきの例文のリストです。空のリスト `[]` になることがあるので、ポップアップ側で空の場合を処理してください。

見つからない場合 (404 Not Found):

```json
{ "detail": "Word not found" }
```

現時点の制限: 辞書の見出し形だけが一致します。`gave up`、`running`、`dogs` のような活用形は、見出し語への変換（レンマ化）を追加するまで404になります。

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

- `word` と `meaning` は必須です。`sentence` は省略できます。

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

### APIを変更するとき

JSONの形を変えるときは、必ず事前にチームに連絡します。拡張機能のコードが動かなくなる可能性があるためです。

## クレジット

- 辞書データ: JMdict/EDRDG（CC BY-SA 4.0）https://www.edrdg.org/ 。jmdict-simplified プロジェクト経由で利用しています。
- 例文: Tatoeba（CC BY 2.0 FR）https://tatoeba.org/