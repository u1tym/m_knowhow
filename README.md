# m_knowhow

大項目・中項目・ノウハウを PostgreSQL で管理し、FastAPI で CRUD 風の参照・追加・名称変更を行う API です。

## 前提条件

- Python 3.10 以上を想定
- 起動前に PostgreSQL 上に、仕様書どおりのテーブル（`major_categories` / `middle_categories` / `knowhows`）が存在すること

## セットアップ

プロジェクトルート（本 README があるディレクトリ）で実行します。

### 1. 仮想環境と依存パッケージ

**Windows (PowerShell):**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. 環境変数（`.env`）

プロジェクトルートに `.env` を置き、DB 接続情報を記載します。例:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=tamtdb
DB_USER=tamtuser
DB_PASSWORD=your_password_here
```

`DB_HOST` / `DB_PORT` / `DB_NAME` / `DB_USER` / `DB_PASSWORD` を環境に合わせて設定してください。アプリは `postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}` で接続します。

### 3. サーバー起動

仮想環境を有効化した状態で、プロジェクトルートから:

```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

既定では `http://127.0.0.1:8000` で待ち受けます。

### 4. 動作確認・API の試し方

- **ヘルスチェック（DB は見ない）**: ブラウザまたは curl で `GET http://127.0.0.1:8000/health` → `{"status":"ok"}`
- **対話的な API ドキュメント**: `http://127.0.0.1:8000/docs`（Swagger UI）
- **ReDoc**: `http://127.0.0.1:8000/redoc`

## DB・API の仕様

テーブル定義、エンドポイント、リクエスト／レスポンス、エラーコードの詳細は次のファイルを参照してください。

- [SPECIFICATION_JA.md](SPECIFICATION_JA.md)

## ディレクトリ構成（概要）

| パス | 内容 |
|------|------|
| `app/main.py` | FastAPI アプリ・ルーター登録 |
| `app/config.py` | `.env` からの設定読み込み |
| `app/database.py` | DB セッション |
| `app/models.py` | SQLAlchemy モデル |
| `app/schemas.py` | Pydantic スキーマ |
| `app/crud.py` | DB 操作 |
| `app/routers/` | ルート定義 |
