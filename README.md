# Japan Stock Downloader

日本株の株価データをダウンロードしてPostgreSQLに保存するシステム。

## 機能

- 過去1年分の日本株株価データを自動ダウンロード
- PostgreSQLへのデータ保存（upsert対応）
- 毎日18:00に自動更新
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

# アプリケーション起動
docker compose up -d app
```

## 一度だけダウンロード実行

```bash
docker compose run --rm app python scripts/download_once.py
```

## VPSへのデプロイ

### 1. VPSの準備

```bash
# VPSにディレクトリ作成
mkdir -p /opt/stock-downloader
cd /opt/stock-downloader

# docker-compose.ymlと.envをコピー
# .envファイルを編集して本番用の値を設定
```

### 2. GitHub Secretsの設定

以下のSecretsをGitHubリポジトリに設定:

- `VPS_HOST`: VPSのホスト名/IP
- `VPS_USER`: SSHユーザー名
- `VPS_SSH_KEY`: SSH秘密鍵

### 3. デプロイ

`main`ブランチにpushすると自動でデプロイされます。

## データベーススキーマ

### stocks（銘柄マスタ）

| カラム | 型 | 説明 |
|--------|------|------|
| id | INT | 主キー |
| code | VARCHAR(10) | 銘柄コード |
| name | VARCHAR(255) | 銘柄名 |
| market | VARCHAR(50) | 市場 |
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

## 銘柄の追加

`src/stock_list.py`の`MAJOR_JAPANESE_STOCKS`リストに銘柄を追加:

```python
MAJOR_JAPANESE_STOCKS = [
    ("7203", "トヨタ自動車"),
    ("新しいコード", "銘柄名"),
    ...
]
```

## ライセンス

MIT
