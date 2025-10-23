# **SALON BOARDスタイル自動投稿Webアプリケーション API仕様書**

## **1. 概要**

本ドキュメントは、SALON BOARDスタイル自動投稿Webアプリケーションが提供するREST APIの詳細仕様を定義する。

### **1.1. 基本情報**

- **ベースURL**: `https://your-domain.com/api/v1`
- **認証方式**: JWT (JSON Web Token) Bearer認証
- **データフォーマット**: JSON (一部エンドポイントでmultipart/form-data)
- **文字エンコーディング**: UTF-8

### **1.2. 共通仕様**

#### **認証ヘッダー**

認証が必要なエンドポイントでは、以下のヘッダーを含める必要がある。

```
Authorization: Bearer <JWT_TOKEN>
```

#### **共通レスポンスフォーマット**

**成功時:**

```json
{
  "success": true,
  "data": { ... }
}
```

**エラー時:**

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "エラーメッセージ",
    "details": { ... }  // オプション
  }
}
```

#### **共通HTTPステータスコード**

| コード | 説明 |
|--------|------|
| 200 | 成功 |
| 201 | 作成成功 |
| 204 | 成功（レスポンスボディなし） |
| 400 | リクエストが不正 |
| 401 | 認証エラー |
| 403 | 権限エラー |
| 404 | リソースが見つからない |
| 409 | リソースの競合 |
| 422 | バリデーションエラー |
| 500 | サーバー内部エラー |

---

## **2. 認証 (Authentication)**

### **2.1. サインイン**

**エンドポイント**: `POST /auth/token`

**説明**: ユーザー認証を行い、JWTを発行する。

**認証**: 不要

**リクエストボディ**:

```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**レスポンス (200 OK)**:

```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 3600,
    "user": {
      "id": 1,
      "email": "user@example.com",
      "role": "user",
      "is_active": true
    }
  }
}
```

**エラーレスポンス**:

- **401 Unauthorized**: 認証情報が不正

```json
{
  "success": false,
  "error": {
    "code": "INVALID_CREDENTIALS",
    "message": "メールアドレスまたはパスワードが正しくありません。"
  }
}
```

- **403 Forbidden**: アカウントが無効化されている

```json
{
  "success": false,
  "error": {
    "code": "ACCOUNT_DISABLED",
    "message": "このアカウントは無効化されています。"
  }
}
```

### **2.2. トークンリフレッシュ**

**エンドポイント**: `POST /auth/refresh`

**説明**: 既存のJWTをリフレッシュして新しいトークンを取得する。

**認証**: 要 (Bearer Token)

**リクエストボディ**: なし

**レスポンス (200 OK)**:

```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 3600
  }
}
```

### **2.3. サインアウト**

**エンドポイント**: `POST /auth/logout`

**説明**: 現在のセッションを無効化する（クライアント側でトークン削除を推奨）。

**認証**: 要 (Bearer Token)

**リクエストボディ**: なし

**レスポンス (204 No Content)**

---

## **3. ユーザー管理 (Users)**

### **3.1. 自身のユーザー情報取得**

**エンドポイント**: `GET /users/me`

**説明**: 現在サインインしているユーザーの情報を取得する。

**認証**: 要 (Bearer Token)

**リクエストパラメータ**: なし

**レスポンス (200 OK)**:

```json
{
  "success": true,
  "data": {
    "id": 1,
    "email": "user@example.com",
    "role": "user",
    "is_active": true,
    "created_at": "2025-01-15T10:00:00Z"
  }
}
```

### **3.2. ユーザー一覧取得**

**エンドポイント**: `GET /users`

**説明**: 全ユーザーの一覧を取得する。

**認証**: 要 (管理者のみ)

**クエリパラメータ**:

| パラメータ | 型 | 必須 | 説明 |
|-----------|-----|------|------|
| `page` | integer | No | ページ番号 (デフォルト: 1) |
| `per_page` | integer | No | 1ページあたりの件数 (デフォルト: 20, 最大: 100) |
| `role` | string | No | フィルタリング用ロール (`admin`, `user`) |
| `is_active` | boolean | No | アクティブ状態でフィルタ |

**レスポンス (200 OK)**:

```json
{
  "success": true,
  "data": {
    "users": [
      {
        "id": 1,
        "email": "admin@example.com",
        "role": "admin",
        "is_active": true,
        "created_at": "2025-01-15T10:00:00Z"
      },
      {
        "id": 2,
        "email": "user@example.com",
        "role": "user",
        "is_active": true,
        "created_at": "2025-01-16T11:00:00Z"
      }
    ],
    "pagination": {
      "total": 25,
      "page": 1,
      "per_page": 20,
      "total_pages": 2
    }
  }
}
```

### **3.3. ユーザー作成**

**エンドポイント**: `POST /users`

**説明**: 新しいユーザーアカウントを作成する。

**認証**: 要 (管理者のみ)

**リクエストボディ**:

```json
{
  "email": "newuser@example.com",
  "password": "SecurePassword123!",
  "role": "user"
}
```

**バリデーションルール**:
- `email`: 必須、メール形式、最大255文字、ユニーク
- `password`: 必須、最小8文字、最大128文字
- `role`: 必須、`admin` または `user`

**レスポンス (201 Created)**:

```json
{
  "success": true,
  "data": {
    "id": 3,
    "email": "newuser@example.com",
    "role": "user",
    "is_active": true,
    "created_at": "2025-01-17T12:00:00Z"
  }
}
```

**エラーレスポンス**:

- **409 Conflict**: メールアドレスが既に登録されている

```json
{
  "success": false,
  "error": {
    "code": "EMAIL_ALREADY_EXISTS",
    "message": "このメールアドレスは既に登録されています。"
  }
}
```

### **3.4. ユーザー更新**

**エンドポイント**: `PUT /users/{user_id}`

**説明**: 指定したユーザーの情報を更新する。

**認証**: 要 (管理者のみ)

**パスパラメータ**:
- `user_id`: 更新対象のユーザーID

**リクエストボディ**:

```json
{
  "email": "updated@example.com",
  "password": "NewPassword123!",  // オプション
  "role": "admin",
  "is_active": false
}
```

**レスポンス (200 OK)**:

```json
{
  "success": true,
  "data": {
    "id": 3,
    "email": "updated@example.com",
    "role": "admin",
    "is_active": false,
    "created_at": "2025-01-17T12:00:00Z"
  }
}
```

### **3.5. ユーザー削除**

**エンドポイント**: `DELETE /users/{user_id}`

**説明**: 指定したユーザーを削除する。

**認証**: 要 (管理者のみ)

**パスパラメータ**:
- `user_id`: 削除対象のユーザーID

**レスポンス (204 No Content)**

**エラーレスポンス**:

- **403 Forbidden**: 自分自身を削除しようとした場合

```json
{
  "success": false,
  "error": {
    "code": "CANNOT_DELETE_SELF",
    "message": "自分自身のアカウントは削除できません。"
  }
}
```

---

## **4. SALON BOARD設定管理 (Salon Board Settings)**

### **4.1. 設定一覧取得**

**エンドポイント**: `GET /sb-settings`

**説明**: 自身のSALON BOARD設定一覧を取得する。

**認証**: 要 (Bearer Token)

**クエリパラメータ**: なし

**レスポンス (200 OK)**:

```json
{
  "success": true,
  "data": {
    "settings": [
      {
        "id": 1,
        "user_id": 2,
        "setting_name": "A店舗",
        "sb_user_id": "sb_user_001",
        "salon_id": "12345",
        "salon_name": "サロンA",
        "created_at": "2025-01-15T10:00:00Z",
        "updated_at": "2025-01-15T10:00:00Z"
      },
      {
        "id": 2,
        "user_id": 2,
        "setting_name": "B店舗",
        "sb_user_id": "sb_user_002",
        "salon_id": "67890",
        "salon_name": "サロンB",
        "created_at": "2025-01-16T11:00:00Z",
        "updated_at": "2025-01-16T11:00:00Z"
      }
    ]
  }
}
```

**注意**: セキュリティのため、暗号化されたパスワードは返却しない。

### **4.2. 設定詳細取得**

**エンドポイント**: `GET /sb-settings/{setting_id}`

**説明**: 指定したSALON BOARD設定の詳細を取得する。

**認証**: 要 (Bearer Token)

**パスパラメータ**:
- `setting_id`: 設定ID

**レスポンス (200 OK)**:

```json
{
  "success": true,
  "data": {
    "id": 1,
    "user_id": 2,
    "setting_name": "A店舗",
    "sb_user_id": "sb_user_001",
    "salon_id": "12345",
    "salon_name": "サロンA",
    "created_at": "2025-01-15T10:00:00Z",
    "updated_at": "2025-01-15T10:00:00Z"
  }
}
```

### **4.3. 設定作成**

**エンドポイント**: `POST /sb-settings`

**説明**: 新しいSALON BOARD設定を作成する。

**認証**: 要 (Bearer Token)

**リクエストボディ**:

```json
{
  "setting_name": "新店舗",
  "sb_user_id": "sb_user_003",
  "sb_password": "salon_password_123",
  "salon_id": "11111",
  "salon_name": "サロンC"
}
```

**バリデーションルール**:
- `setting_name`: 必須、最大100文字
- `sb_user_id`: 必須、最大255文字
- `sb_password`: 必須、最大255文字
- `salon_id`: オプション、最大100文字
- `salon_name`: オプション、最大255文字

**レスポンス (201 Created)**:

```json
{
  "success": true,
  "data": {
    "id": 3,
    "user_id": 2,
    "setting_name": "新店舗",
    "sb_user_id": "sb_user_003",
    "salon_id": "11111",
    "salon_name": "サロンC",
    "created_at": "2025-01-18T13:00:00Z",
    "updated_at": "2025-01-18T13:00:00Z"
  }
}
```

### **4.4. 設定更新**

**エンドポイント**: `PUT /sb-settings/{setting_id}`

**説明**: 指定したSALON BOARD設定を更新する。

**認証**: 要 (Bearer Token)

**パスパラメータ**:
- `setting_id`: 設定ID

**リクエストボディ**:

```json
{
  "setting_name": "更新後の店舗名",
  "sb_user_id": "sb_user_003_updated",
  "sb_password": "new_salon_password",  // オプション（未指定時は変更なし）
  "salon_id": "22222",
  "salon_name": "更新後サロン名"
}
```

**レスポンス (200 OK)**:

```json
{
  "success": true,
  "data": {
    "id": 3,
    "user_id": 2,
    "setting_name": "更新後の店舗名",
    "sb_user_id": "sb_user_003_updated",
    "salon_id": "22222",
    "salon_name": "更新後サロン名",
    "created_at": "2025-01-18T13:00:00Z",
    "updated_at": "2025-01-18T14:00:00Z"
  }
}
```

### **4.5. 設定削除**

**エンドポイント**: `DELETE /sb-settings/{setting_id}`

**説明**: 指定したSALON BOARD設定を削除する。

**認証**: 要 (Bearer Token)

**パスパラメータ**:
- `setting_id`: 設定ID

**レスポンス (204 No Content)**

**エラーレスポンス**:

- **404 Not Found**: 設定が存在しない

```json
{
  "success": false,
  "error": {
    "code": "SETTING_NOT_FOUND",
    "message": "指定された設定が見つかりません。"
  }
}
```

---

## **5. タスク管理 (Tasks)**

### **5.1. タスク一覧取得**

**エンドポイント**: `GET /tasks`

**説明**: 自身が作成したタスクの一覧を取得する。

**認証**: 要 (Bearer Token)

**クエリパラメータ**:

| パラメータ | 型 | 必須 | 説明 |
|-----------|-----|------|------|
| `page` | integer | No | ページ番号 (デフォルト: 1) |
| `per_page` | integer | No | 1ページあたりの件数 (デフォルト: 20, 最大: 100) |
| `status` | string | No | ステータスでフィルタ (`PENDING`, `PROCESSING`, `SUCCESS`, `FAILURE`, `INTERRUPTED`) |

**レスポンス (200 OK)**:

```json
{
  "success": true,
  "data": {
    "tasks": [
      {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "user_id": 2,
        "status": "PROCESSING",
        "total_items": 10,
        "completed_items": 3,
        "log_file_path": null,
        "screenshot_path": null,
        "created_at": "2025-01-18T15:00:00Z",
        "completed_at": null
      },
      {
        "id": "660e8400-e29b-41d4-a716-446655440001",
        "user_id": 2,
        "status": "SUCCESS",
        "total_items": 5,
        "completed_items": 5,
        "log_file_path": "/logs/task_660e8400.log",
        "screenshot_path": null,
        "created_at": "2025-01-17T12:00:00Z",
        "completed_at": "2025-01-17T12:15:00Z"
      }
    ],
    "pagination": {
      "total": 12,
      "page": 1,
      "per_page": 20,
      "total_pages": 1
    }
  }
}
```

### **5.2. タスク詳細取得**

**エンドポイント**: `GET /tasks/{task_id}`

**説明**: 指定したタスクの詳細を取得する。

**認証**: 要 (Bearer Token)

**パスパラメータ**:
- `task_id`: タスクID (UUID)

**レスポンス (200 OK)**:

```json
{
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "user_id": 2,
    "status": "PROCESSING",
    "total_items": 10,
    "completed_items": 3,
    "log_file_path": null,
    "screenshot_path": null,
    "created_at": "2025-01-18T15:00:00Z",
    "completed_at": null,
    "progress_percentage": 30.0
  }
}
```

### **5.3. スタイル投稿タスク作成**

**エンドポイント**: `POST /tasks/style-post`

**説明**: 新しいスタイル自動投稿タスクを作成し、バックグラウンドで実行する。

**認証**: 要 (Bearer Token)

**Content-Type**: `multipart/form-data`

**フォームデータ**:

| フィールド | 型 | 必須 | 説明 |
|-----------|-----|------|------|
| `sb_setting_id` | integer | Yes | 使用するSALON BOARD設定ID |
| `data_file` | file | Yes | スタイル情報ファイル (CSV/Excel) |
| `images` | file[] | Yes | 画像ファイル（複数可） |

**リクエスト例**:

```
POST /tasks/style-post
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary

------WebKitFormBoundary
Content-Disposition: form-data; name="sb_setting_id"

1
------WebKitFormBoundary
Content-Disposition: form-data; name="data_file"; filename="styles.csv"
Content-Type: text/csv

[ファイル内容]
------WebKitFormBoundary
Content-Disposition: form-data; name="images"; filename="image1.jpg"
Content-Type: image/jpeg

[画像データ]
------WebKitFormBoundary
Content-Disposition: form-data; name="images"; filename="image2.jpg"
Content-Type: image/jpeg

[画像データ]
------WebKitFormBoundary--
```

**レスポンス (201 Created)**:

```json
{
  "success": true,
  "data": {
    "task_id": "770e8400-e29b-41d4-a716-446655440002",
    "status": "PENDING",
    "message": "タスクが正常に作成されました。バックグラウンドで実行されます。"
  }
}
```

**エラーレスポンス**:

- **422 Unprocessable Entity**: ファイル検証エラー

```json
{
  "success": false,
  "error": {
    "code": "FILE_VALIDATION_ERROR",
    "message": "ファイルの検証に失敗しました。",
    "details": {
      "missing_images": ["image3.jpg", "image5.jpg"]
    }
  }
}
```

### **5.4. タスク中断**

**エンドポイント**: `POST /tasks/{task_id}/interrupt`

**説明**: 実行中のタスクを中断する。

**認証**: 要 (Bearer Token)

**パスパラメータ**:
- `task_id`: タスクID (UUID)

**リクエストボディ**: なし

**レスポンス (200 OK)**:

```json
{
  "success": true,
  "data": {
    "task_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "INTERRUPTED",
    "message": "タスクを中断しました。"
  }
}
```

**エラーレスポンス**:

- **400 Bad Request**: 中断できない状態

```json
{
  "success": false,
  "error": {
    "code": "CANNOT_INTERRUPT_TASK",
    "message": "このタスクは中断できません。ステータス: SUCCESS"
  }
}
```

### **5.5. タスク再開**

**エンドポイント**: `POST /tasks/{task_id}/resume`

**説明**: 中断中のタスクを再開する。

**認証**: 要 (Bearer Token)

**パスパラメータ**:
- `task_id`: タスクID (UUID)

**リクエストボディ**: なし

**レスポンス (200 OK)**:

```json
{
  "success": true,
  "data": {
    "task_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "PROCESSING",
    "message": "タスクを再開しました。"
  }
}
```

### **5.6. タスクログダウンロード**

**エンドポイント**: `GET /tasks/{task_id}/logs`

**説明**: タスクのログファイルをダウンロードする。

**認証**: 要 (Bearer Token)

**パスパラメータ**:
- `task_id`: タスクID (UUID)

**レスポンス (200 OK)**:

```
Content-Type: text/plain
Content-Disposition: attachment; filename="task_550e8400.log"

[ログ内容]
```

### **5.7. タスクスクリーンショットダウンロード**

**エンドポイント**: `GET /tasks/{task_id}/screenshot`

**説明**: タスクのエラースクリーンショットをダウンロードする。

**認証**: 要 (Bearer Token)

**パスパラメータ**:
- `task_id`: タスクID (UUID)

**レスポンス (200 OK)**:

```
Content-Type: image/png
Content-Disposition: attachment; filename="error_screenshot_550e8400.png"

[画像データ]
```

---

## **6. ヘルスチェック (Health Check)**

### **6.1. システムヘルスチェック**

**エンドポイント**: `GET /health`

**説明**: システムの稼働状況を確認する。

**認証**: 不要

**レスポンス (200 OK)**:

```json
{
  "status": "healthy",
  "timestamp": "2025-01-18T15:30:00Z",
  "services": {
    "database": "healthy",
    "redis": "healthy",
    "worker": "healthy"
  }
}
```

---

## **7. エラーコード一覧**

| コード | 説明 |
|--------|------|
| `INVALID_CREDENTIALS` | 認証情報が不正 |
| `ACCOUNT_DISABLED` | アカウントが無効化されている |
| `TOKEN_EXPIRED` | トークンの有効期限切れ |
| `TOKEN_INVALID` | トークンが不正 |
| `PERMISSION_DENIED` | 権限がない |
| `EMAIL_ALREADY_EXISTS` | メールアドレスが既に登録済み |
| `USER_NOT_FOUND` | ユーザーが見つからない |
| `CANNOT_DELETE_SELF` | 自分自身を削除しようとした |
| `SETTING_NOT_FOUND` | 設定が見つからない |
| `TASK_NOT_FOUND` | タスクが見つからない |
| `FILE_VALIDATION_ERROR` | ファイル検証エラー |
| `CANNOT_INTERRUPT_TASK` | タスクを中断できない |
| `CANNOT_RESUME_TASK` | タスクを再開できない |
| `VALIDATION_ERROR` | バリデーションエラー |
| `INTERNAL_SERVER_ERROR` | サーバー内部エラー |

---

## **8. レート制限**

- **認証エンドポイント**: 5リクエスト/分/IP
- **その他のエンドポイント**: 100リクエスト/分/ユーザー

レート制限を超えた場合、`429 Too Many Requests` が返される。

```json
{
  "success": false,
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "リクエスト制限を超えました。しばらくしてから再試行してください。",
    "retry_after": 60
  }
}
```

---

## **9. バージョニング**

APIのバージョンはURLに含まれる (`/api/v1/`)。後方互換性のない変更を行う場合は、新しいバージョン (`/api/v2/`) を作成する。
