# 技術スタックと規約

## Python規約

### バージョン
- Python 3.11以上

### コードスタイル
- PEP 8に準拠
- フォーマッター: black
- リンター: ruff または flake8
- 型チェック: mypy

### 命名規則
- **関数/変数**: スネークケース (例: `get_user_by_id`, `user_count`)
- **クラス**: パスカルケース (例: `UserService`, `SalonBoardSettings`)
- **定数**: 大文字スネークケース (例: `MAX_RETRY_COUNT`, `API_VERSION`)
- **プライベート**: アンダースコアプレフィックス (例: `_internal_method`)

### 型ヒント
- すべての関数には型ヒントを必須とする
```python
def get_user(user_id: int) -> User | None:
    pass
```

### Docstring
- Google形式を採用
```python
def example_function(param1: str, param2: int) -> bool:
    """関数の簡潔な説明.

    Args:
        param1: パラメータ1の説明
        param2: パラメータ2の説明

    Returns:
        戻り値の説明

    Raises:
        ValueError: エラー条件の説明
    """
    pass
```

## FastAPI規約

### ルーター構成
- 機能ごとにルーターを分割
- プレフィックスを明示的に設定

### レスポンスモデル
- Pydanticスキーマを必ず定義
- `response_model` を明示的に指定

### エラーハンドリング
- HTTPExceptionを使用
- カスタムエラーハンドラーで統一フォーマット

## SQLAlchemy規約

### モデル定義
- DeclarativeBaseを継承
- テーブル名は複数形（例: `users`, `tasks`）
- リレーションシップは明示的に定義

### マイグレーション
- Alembicを使用
- 自動生成 + 手動レビュー

## Playwright規約

### セレクタ管理
- すべてのセレクタは `selectors.yaml` で外部管理
- コード内にハードコーディングしない

### エラーハンドリング
- スクリーンショット自動撮影
- ログファイルへの詳細記録

## Git規約

### コミットメッセージ
```
<type>: <subject>

<body>
```

**Type:**
- feat: 新機能
- fix: バグ修正
- docs: ドキュメント変更
- refactor: リファクタリング
- test: テスト追加・修正
- chore: その他の変更

### ブランチ戦略
- main: 本番環境
- develop: 開発環境
- feature/*: 新機能開発
- hotfix/*: 緊急修正

## セキュリティ規約

### 機密情報管理
- 環境変数で管理（`.env` ファイル）
- `.env` ファイルは `.gitignore` に含める
- `.env.example` をサンプルとして提供

### パスワード
- ユーザーパスワード: bcryptでハッシュ化
- SALON BOARDパスワード: AES-256で暗号化
- 平文での保存・ログ出力厳禁

## ディレクトリ構造規約

### app/
```
app/
├── main.py              # FastAPIアプリケーション
├── api/
│   ├── __init__.py
│   ├── deps.py          # 依存性注入
│   └── v1/              # APIバージョン1
│       ├── __init__.py
│       ├── auth.py      # 認証エンドポイント
│       ├── users.py     # ユーザー管理
│       ├── settings.py  # SALON BOARD設定
│       └── tasks.py     # タスク管理
├── models/              # SQLAlchemyモデル
│   ├── __init__.py
│   ├── user.py
│   ├── salon_board_setting.py
│   └── task.py
├── schemas/             # Pydanticスキーマ
│   ├── __init__.py
│   ├── user.py
│   ├── salon_board_setting.py
│   └── task.py
├── services/            # ビジネスロジック
│   ├── __init__.py
│   ├── user_service.py
│   ├── auth_service.py
│   └── task_service.py
├── tasks/               # Celeryタスク
│   ├── __init__.py
│   └── style_post_task.py
├── automation/          # Playwright自動化
│   ├── __init__.py
│   ├── salon_board_poster.py
│   └── selectors.yaml
└── core/                # 設定・共通機能
    ├── __init__.py
    ├── config.py        # 設定管理
    ├── security.py      # セキュリティ機能
    └── database.py      # DB接続
```
