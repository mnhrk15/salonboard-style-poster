# プロジェクト概要

## プロジェクト名
SALON BOARDスタイル自動投稿Webアプリケーション

## 目的
美容室スタッフが手作業で行っているSALON BOARDへのスタイル投稿作業を自動化し、業務効率を向上させる。

## 主要機能
1. **ユーザー管理**: 管理者によるクローズドなユーザーアカウント管理
2. **SALON BOARD設定管理**: ユーザーごとのSALON BOARD認証情報の暗号化保存
3. **スタイル自動投稿**: CSV/Excelファイルと画像の一括アップロードと自動投稿
4. **タスク管理**: バックグラウンドタスクの進捗確認、中断・再開機能

## 技術スタック
- **バックエンド**: Python 3.11+, FastAPI
- **フロントエンド**: Jinja2, HTML, CSS, JavaScript
- **データベース**: PostgreSQL 16.x
- **タスクキュー**: Celery + Redis
- **ブラウザ自動化**: Playwright for Python (Firefox)
- **コンテナ**: Docker, Docker Compose
- **Webサーバー**: Uvicorn, Nginx

## アーキテクチャ
マイクロサービスライクなコンテナ構成:
- Nginxコンテナ (リバースプロキシ、SSL/TLS終端)
- Webコンテナ (FastAPI + Uvicorn)
- Workerコンテナ (Celery + Playwright)
- PostgreSQLコンテナ
- Redisコンテナ

## セキュリティ
- ユーザーパスワード: bcryptでハッシュ化
- SALON BOARDパスワード: AES-256で暗号化
- 認証: JWT (JSON Web Token)
- 通信: HTTPS/TLS必須

## プロジェクト構造（予定）
```
salonboard-style-poster/
├── docs/                    # ドキュメント
├── app/                     # アプリケーションコード
│   ├── main.py             # FastAPIエントリーポイント
│   ├── api/                # APIルーター
│   ├── models/             # SQLAlchemyモデル
│   ├── schemas/            # Pydanticスキーマ
│   ├── services/           # ビジネスロジック
│   ├── tasks/              # Celeryタスク
│   ├── automation/         # Playwright自動化
│   └── core/               # 設定、セキュリティ
├── database/               # DB初期化スクリプト
├── tests/                  # テストコード
├── docker/                 # Dockerファイル
├── requirements.txt        # Python依存関係
└── docker-compose.yml      # Docker構成
```

## 開発環境
- OS: macOS (Darwin)
- Python: 3.11以上
- 仮想環境: venv

## デプロイ先
VPS (Virtual Private Server)
