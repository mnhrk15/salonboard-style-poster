# SALON BOARD スタイル自動投稿Webアプリケーション

美容室スタッフのSALON BOARDへのスタイル投稿作業を自動化するWebアプリケーションです。

## 📋 機能

- **ユーザー管理**: 管理者によるクローズドなユーザーアカウント管理
- **SALON BOARD設定管理**: ユーザーごとのSALON BOARD認証情報の暗号化保存
- **スタイル自動投稿**: CSV/Excelファイルと画像の一括アップロードと自動投稿
- **タスク管理**: バックグラウンドタスクの進捗確認、中断・再開機能

## 🛠 技術スタック

- **バックエンド**: Python 3.11+, FastAPI
- **データベース**: PostgreSQL 16
- **タスクキュー**: Celery + Redis
- **ブラウザ自動化**: Playwright for Python (Firefox)
- **コンテナ**: Docker, Docker Compose

## 📦 必要要件

- Docker 20.10以上
- Docker Compose 2.0以上
- (開発環境) Python 3.11以上

## 🚀 セットアップ

### 1. リポジトリのクローン

```bash
git clone <repository-url>
cd salonboard-style-poster
```

### 2. 環境変数の設定

`.env.example`をコピーして`.env`を作成し、必要な値を設定します。

```bash
cp .env.example .env
```

`.env`ファイルを編集して、以下の重要な値を変更してください:

```env
# セキュリティ関連（必ず変更してください）
SECRET_KEY=your-secret-key-here-change-this-in-production
ENCRYPTION_KEY=your-32-byte-encryption-key-here-change-this
JWT_SECRET_KEY=your-jwt-secret-key-here-change-this

# データベース
DB_PASSWORD=your-secure-password

# その他の設定は必要に応じて変更
```

**暗号化キーの生成方法:**

```python
# Python インタープリタで実行
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())
```

### 3. SSL証明書の準備（本番環境）

本番環境では、SSL証明書を`docker/nginx/ssl/`ディレクトリに配置します。

```bash
mkdir -p docker/nginx/ssl
# 証明書ファイルを配置
# - cert.pem
# - key.pem
```

開発環境では自己署名証明書を作成できます:

```bash
mkdir -p docker/nginx/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout docker/nginx/ssl/key.pem \
  -out docker/nginx/ssl/cert.pem \
  -subj "/CN=localhost"
```

### 4. Dockerコンテナの起動

```bash
docker-compose build
docker-compose up -d
```

### 5. データベースマイグレーション

```bash
docker-compose exec web alembic upgrade head
```

### 6. 初回管理者アカウントの作成

```bash
docker-compose exec web python scripts/create_admin.py admin@example.com SecurePassword123!
```

### 7. アプリケーションへのアクセス

- **Web UI**: https://localhost (または設定したドメイン)
- **API ドキュメント**: https://localhost/docs
- **ヘルスチェック**: https://localhost/health

## 📖 使い方

### 管理者の操作

1. 管理者アカウントでサインイン
2. ユーザー管理画面で一般ユーザーアカウントを作成
3. 作成したアカウント情報をユーザーに共有

### 一般ユーザーの操作

1. 配布されたID/パスワードでサインイン
2. **設定画面**でSALON BOARD設定を登録
   - SALON BOARD ID
   - SALON BOARD パスワード
   - サロンID/名前（複数店舗の場合）
3. **新規スタイル投稿画面**でタスクを作成
   - SALON BOARD設定を選択
   - スタイル情報ファイル（CSV/Excel）をアップロード
   - 画像ファイルをアップロード
4. **タスク一覧画面**で進捗を確認

### スタイル情報ファイルの形式

CSV/Excelファイルには以下のカラムを含めてください:

| カラム名 | 説明 | 必須 |
|---------|------|------|
| image_filename | 画像ファイル名 | ○ |
| stylist_name | スタイリスト名 | ○ |
| style_name | スタイル名 | ○ |
| stylist_comment | スタイリストコメント | |
| category | カテゴリ（ladies/mens） | ○ |
| length | 髪の長さ | ○ |
| menu_detail | メニュー詳細 | |
| coupon_name | クーポン名 | |
| hashtags | ハッシュタグ（カンマ区切り） | |

**例:**
```csv
image_filename,stylist_name,style_name,stylist_comment,category,length,menu_detail,coupon_name,hashtags
style001.jpg,山田太郎,大人かわいいボブ,柔らかい印象に,ladies,ミディアム,カット+カラー,新規限定クーポン,ボブ,ナチュラル,大人可愛い
```

## 🔧 開発

### ローカル開発環境のセットアップ

```bash
# 仮想環境の作成
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 依存関係のインストール
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Playwright ブラウザのインストール
playwright install firefox
```

### コード品質チェック

```bash
# フォーマット
black app/ tests/
isort app/ tests/

# リンティング
ruff check app/ tests/

# 型チェック
mypy app/

# テスト
pytest
```

### データベースマイグレーション

```bash
# 新しいマイグレーションを作成
alembic revision --autogenerate -m "description"

# マイグレーションを適用
alembic upgrade head

# ロールバック
alembic downgrade -1
```

## 📝 API ドキュメント

起動後、以下のURLでインタラクティブなAPIドキュメントを確認できます:

- **Swagger UI**: https://localhost/docs
- **ReDoc**: https://localhost/redoc

## 🐛 トラブルシューティング

### Dockerコンテナが起動しない

```bash
# ログを確認
docker-compose logs web
docker-compose logs worker

# コンテナを再起動
docker-compose restart
```

### データベース接続エラー

```bash
# データベースコンテナのヘルスチェック
docker-compose ps db

# データベースに直接接続
docker-compose exec db psql -U postgres -d salonboard_db
```

### Celeryタスクが実行されない

```bash
# Workerのログを確認
docker-compose logs -f worker

# Redisの接続確認
docker-compose exec redis redis-cli ping
```

### Playwright エラー

ブラウザの起動に失敗する場合、ヘッドレスモードの設定を確認してください:

```env
PLAYWRIGHT_HEADLESS=True
```

## 🔒 セキュリティ

- ユーザーパスワードはbcryptでハッシュ化して保存
- SALON BOARDパスワードはAES-256で暗号化して保存
- JWT認証による安全なAPI通信
- HTTPS/TLS通信の強制

## 📜 ライセンス

このプロジェクトは非公開プロジェクトです。

## 👥 サポート

問題が発生した場合は、開発チームまでお問い合わせください。
