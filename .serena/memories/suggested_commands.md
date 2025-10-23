# 推奨コマンド一覧

## 開発環境セットアップ

### 仮想環境作成
```bash
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
```

### 依存関係インストール
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # 開発用依存関係
```

## コード品質管理

### フォーマット
```bash
# blackでフォーマット
black app/ tests/

# isortでインポート整理
isort app/ tests/
```

### リンティング
```bash
# ruffでリンティング
ruff check app/ tests/

# mypyで型チェック
mypy app/
```

### すべてのチェックを実行
```bash
# フォーマット + リンティング + 型チェック
black app/ tests/ && isort app/ tests/ && ruff check app/ tests/ && mypy app/
```

## テスト

### 全テスト実行
```bash
pytest
```

### カバレッジ付きテスト
```bash
pytest --cov=app --cov-report=html
```

### 特定のテストファイル実行
```bash
pytest tests/test_users.py
```

### 特定のテスト関数実行
```bash
pytest tests/test_users.py::test_create_user
```

## データベース

### マイグレーション作成
```bash
alembic revision --autogenerate -m "説明"
```

### マイグレーション適用
```bash
alembic upgrade head
```

### マイグレーションロールバック
```bash
alembic downgrade -1
```

### マイグレーション履歴確認
```bash
alembic history
```

## Docker

### コンテナビルド
```bash
docker-compose build
```

### コンテナ起動
```bash
docker-compose up -d
```

### コンテナ停止
```bash
docker-compose down
```

### ログ確認
```bash
docker-compose logs -f web
docker-compose logs -f worker
```

### コンテナ内でコマンド実行
```bash
docker-compose exec web bash
docker-compose exec db psql -U postgres -d salonboard_db
```

### 初回管理者作成
```bash
docker-compose exec web python scripts/create_admin.py admin@example.com password123
```

## アプリケーション実行

### 開発サーバー起動（ローカル）
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Celeryワーカー起動（ローカル）
```bash
celery -A app.tasks.celery_app worker --loglevel=info
```

### Celery Flower起動（モニタリング）
```bash
celery -A app.tasks.celery_app flower
```

## タスク完了時の実行コマンド

### 1. フォーマット
```bash
black app/ tests/
isort app/ tests/
```

### 2. リンティング
```bash
ruff check app/ tests/
```

### 3. 型チェック
```bash
mypy app/
```

### 4. テスト実行
```bash
pytest
```

### 5. Git操作
```bash
git add .
git commit -m "feat: 実装内容の説明"
git push
```

## その他の便利なコマンド

### Python依存関係の更新
```bash
pip list --outdated
pip install --upgrade package_name
pip freeze > requirements.txt
```

### データベース接続確認
```bash
docker-compose exec db psql -U postgres -c "SELECT version();"
```

### Redis接続確認
```bash
docker-compose exec redis redis-cli ping
```

### ディスク使用量確認
```bash
docker system df
docker system prune  # 未使用リソースの削除
```

## macOS特有のコマンド

### ファイル検索
```bash
find . -name "*.py" -type f
```

### ディレクトリ内のファイル一覧
```bash
ls -la
tree -L 2  # treeがインストールされている場合
```

### プロセス確認
```bash
ps aux | grep python
lsof -i :8000  # ポート8000を使用しているプロセス
```
