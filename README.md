# Japan Stock Downloader

日本株の株価データをダウンロードしてPostgreSQLに保存するシステム。

## 機能

- JPXから全上場銘柄（約4,000銘柄）を自動取得
- GitHub Actionsで毎日16:30 JSTに自動実行
- PostgreSQLへのデータ保存（upsert対応）
- Docker Composeによる簡単デプロイ

## 必要要件

- Docker & Docker Compose
- VPS（デプロイ用）

## ローカル開発

```bash
# 環境変数ファイルをコピー
cp .env.example .env

# Dockerコンテナ起動
docker compose up -d db

# マイグレーション実行
docker compose --profile migration run --rm migration

# 日次ダウンロード実行
docker compose run --rm app
```

## 過去データの一括取得（初回のみ）

初回セットアップ時に過去1年分のデータを取得する場合:

```bash
docker compose --profile backfill run --rm backfill
```

## 環境変数

| 変数 | デフォルト | 説明 |
|------|-----------|------|
| POSTGRES_HOST | db | PostgreSQLホスト |
| POSTGRES_PORT | 5432 | PostgreSQLポート |
| POSTGRES_DB | stocks | データベース名 |
| POSTGRES_USER | stockuser | ユーザー名 |
| POSTGRES_PASSWORD | stockpass | パスワード |
| LOG_LEVEL | INFO | ログレベル |
| DOWNLOAD_BATCH_SIZE | 50 | バッチサイズ |

## VPSへのデプロイ

### 1. GitHub Secretsの設定

以下のSecretsをGitHubリポジトリのEnvironment `production` に設定:

- `VPS_HOST`: VPSのホスト名/IP
- `VPS_USER`: SSHユーザー名
- `VPS_SSH_KEY`: SSH秘密鍵

### 2. デプロイ

`main`ブランチにpushすると自動でデプロイされます。

### 3. 日次実行

GitHub Actionsが毎日16:30 JSTに自動で株価データをダウンロードします。

## データベーススキーマ

### stocks（銘柄マスタ）

| カラム | 型 | 説明 |
|--------|------|------|
| id | INT | 主キー |
| code | VARCHAR(10) | 銘柄コード |
| name | VARCHAR(255) | 銘柄名 |
| market | VARCHAR(50) | 市場区分 |
| sector | VARCHAR(100) | 業種 |

### stock_prices（株価データ）

| カラム | 型 | 説明 |
|--------|------|------|
| id | BIGINT | 主キー |
| code | VARCHAR(10) | 銘柄コード |
| trade_date | DATE | 取引日 |
| open | FLOAT | 始値 |
| high | FLOAT | 高値 |
| low | FLOAT | 安値 |
| close | FLOAT | 終値 |
| volume | BIGINT | 出来高 |
| adjusted_close | FLOAT | 調整後終値 |

## ライセンス

MIT
