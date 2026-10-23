[English](README.md) | 日本語

# EasyRead

EasyReadは、日本人の英語学習者のための「逆Yomitan」です。YouTubeの英語字幕の単語にマウスを乗せると、日本語の意味と例文が表示され、ワンクリックでAnkiに保存できます。

## プロジェクト構成

- `backend/`: FastAPIのバックエンド（辞書検索、Anki連携）
- `extension/`: Chrome拡張機能（字幕の検出、ホバーポップアップ）

## バックエンドの起動方法

フロントエンド担当の方は、バックエンドが完成するまでは起動しなくても大丈夫です。下の「API仕様」のJSONをモックデータとして使ってください。

1. データファイルをダウンロードします（Gitには含まれていません）。
   - JMdict（英語版）: GitHubの jmdict-simplified (scriptin) のReleasesから英語版JSONをダウンロードし、`backend/data/jmdict-eng.json` として保存
   - Tatoeba の文ペア: manythings.org の `jpn-eng.zip` を解凍し、`backend/data/jpn-eng.txt` として保存

2. 依存パッケージのインストールとデータベースの作成:

```
cd backend
uv sync
uv run python import_jmdict.py
uv run python seed.py
uv run python import_examples.py
```

この3つのスクリプトは、必ずこの順番で実行してください。データを変更したときは、もう一度実行します。

3. サーバーを起動します。

```
uv run uvicorn main:app --reload
```

APIは http://127.0.0.1:8000 で動き、API仕様のページは http://127.0.0.1:8000/docs で見られます。

## API仕様

### GET /lookup?word=racket

成功 (200 OK):

```json
{
  "word": "racket",
  "senses": [
    { "type": "noun", "meanings": ["ラケット"] },
    { "type": "noun", "meanings": ["騒音", "どんちゃん騒ぎ"] }
  ],
  "examples": [
    { "english": "Choose your favorite racket.", "japanese": "好きなラケットを選びなさい。" }
  ]
}
```

- `word`: 正規化（小文字化、句読点の除去）した単語です。送った文字列そのままではありません。
- `senses`: 意味のまとまりのリストです。各要素は品詞 `type` と、日本語の意味のリスト `meanings` を持ちます。
- `examples`: 例文のリストです。見つからない場合は空のリスト `[]` になるので、ポップアップ側で空の場合を処理してください。

見つからない場合 (404 Not Found):

```json
{ "detail": "Word not found" }
```

### 拡張機能からの呼び出しについて

- 呼び出し先は `http://127.0.0.1:8000/lookup` です。
- `manifest.json` の `host_permissions` にこのURLを追加してください。
- CORSはバックエンド側で許可済みです。

### 変更があるとき

APIのJSONの形を変えるときは、必ず事前にチームに連絡します。拡張機能のコードが動かなくなる可能性があるためです。

## クレジット

- 辞書データ: JMdict/EDRDG（CC BY-SA 4.0）https://www.edrdg.org/ 。jmdict-simplified プロジェクト経由で利用しています。
- 例文: Tatoeba（CC BY 2.0 FR）https://tatoeba.org/