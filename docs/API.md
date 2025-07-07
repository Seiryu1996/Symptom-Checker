# API ドキュメント

症状チェッカーサービスのAPIエンドポイント一覧です。

## ベース URL

- 開発環境: `http://localhost:8000/api/v1`
- 本番環境: `https://your-backend-url.onrender.com/api/v1`

## 認証

一部のエンドポイントでは認証が必要です。JWTトークンをAuthorizationヘッダーに含めて送信してください。

```
Authorization: Bearer <token>
```

## 症状関連 API

### 症状入力

```http
POST /symptoms/input
```

症状の自由入力を解析し、構造化されたデータを返します。

**リクエストボディ:**
```json
{
  "text": "頭痛がひどくて、吐き気もあります",
  "severity": 4,
  "duration": "1日",
  "location": "頭"
}
```

**レスポンス:**
```json
{
  "id": "symptom_123",
  "text": "頭痛がひどくて、吐き気もあります",
  "severity": 4,
  "duration": "1日",
  "location": "頭",
  "category": "頭部の症状",
  "keywords": ["頭痛", "吐き気"]
}
```

### 症状候補取得

```http
GET /symptoms/suggestions?category={category}
```

指定されたカテゴリの症状候補を取得します。

**パラメータ:**
- `category` (optional): 症状カテゴリ

**レスポンス:**
```json
[
  {
    "text": "頭痛",
    "category": "頭部",
    "common": true
  }
]
```

### 症状カテゴリ取得

```http
GET /symptoms/categories
```

症状カテゴリ一覧を取得します。

**レスポンス:**
```json
{
  "categories": [
    {
      "id": "head",
      "name": "頭部",
      "icon": "🧠"
    }
  ]
}
```

## 診断関連 API

### 症状分析

```http
POST /diagnosis/analyze
```

入力された症状を分析し、推奨される診療科を返します。

**リクエストボディ:**
```json
{
  "symptoms": ["頭痛", "吐き気"],
  "patient_age": 30,
  "patient_gender": "male",
  "duration": "1日",
  "severity": 4
}
```

**レスポンス:**
```json
{
  "possible_conditions": ["偏頭痛", "緊張型頭痛"],
  "recommended_specialties": [
    {
      "id": "neurology",
      "name": "神経内科",
      "description": "脳神経に関する疾患を診療",
      "urgency": "medium"
    }
  ],
  "urgency_level": "medium",
  "advice": "症状が続く場合は医療機関を受診してください。",
  "confidence": 0.8
}
```

### 診療科一覧

```http
GET /diagnosis/specialties
```

すべての診療科を取得します。

**レスポンス:**
```json
[
  {
    "id": "internal_medicine",
    "name": "内科",
    "description": "一般的な内科疾患",
    "urgency": "medium"
  }
]
```

## 病院関連 API

### 病院検索

```http
POST /hospitals/search
```

指定された条件で病院を検索します。

**リクエストボディ:**
```json
{
  "specialties": ["内科", "外科"],
  "user_location": {
    "latitude": 35.6762,
    "longitude": 139.6503,
    "address": "東京都渋谷区"
  },
  "max_distance": 10.0,
  "emergency_only": false
}
```

**レスポンス:**
```json
[
  {
    "id": "hospital_1",
    "name": "市立総合病院",
    "location": {
      "latitude": 35.6762,
      "longitude": 139.6503,
      "address": "東京都渋谷区"
    },
    "phone": "03-1234-5678",
    "specialties": ["内科", "外科"],
    "hours": [
      {
        "day": "月",
        "open_time": "09:00",
        "close_time": "17:00",
        "is_closed": false
      }
    ],
    "distance": 1.2,
    "rating": 4.2,
    "website": "https://hospital.example.com",
    "emergency": true
  }
]
```

### 周辺病院取得

```http
GET /hospitals/nearby?latitude={lat}&longitude={lng}&radius={radius}&specialty={specialty}
```

現在地周辺の病院を取得します。

**パラメータ:**
- `latitude`: 緯度 (必須)
- `longitude`: 経度 (必須)
- `radius`: 検索半径(km) (デフォルト: 5.0)
- `specialty`: 診療科 (任意)

### 病院詳細取得

```http
GET /hospitals/{hospital_id}
```

指定された病院の詳細情報を取得します。

**パラメータ:**
- `hospital_id`: 病院ID

## ユーザー関連 API

### ユーザー登録

```http
POST /users/register
```

新しいユーザーを登録します。

**リクエストボディ:**
```json
{
  "email": "user@example.com",
  "name": "山田太郎",
  "age": 30,
  "gender": "male",
  "phone": "090-1234-5678",
  "notification_preferences": ["hospital_news", "health_info"]
}
```

**レスポンス:**
```json
{
  "id": "user_123",
  "email": "user@example.com",
  "name": "山田太郎",
  "age": 30,
  "gender": "male",
  "phone": "090-1234-5678",
  "notification_preferences": ["hospital_news", "health_info"],
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### ユーザープロフィール取得

```http
GET /users/profile
```

**認証必須**

現在のユーザーのプロフィールを取得します。

### ユーザープロフィール更新

```http
PUT /users/profile
```

**認証必須**

ユーザープロフィールを更新します。

**リクエストボディ:**
```json
{
  "name": "田中太郎",
  "age": 31,
  "notification_preferences": ["health_info"]
}
```

### 通知設定取得

```http
GET /users/notification-preferences
```

利用可能な通知設定オプションを取得します。

**レスポンス:**
```json
[
  {
    "type": "hospital_news",
    "enabled": true,
    "description": "病院からのお知らせ"
  }
]
```

### アカウント削除

```http
DELETE /users/account
```

**認証必須**

ユーザーアカウントを削除します。

## ニュース・情報 API

### 健康ニュース取得

```http
GET /news/health-news?category={category}&limit={limit}
```

健康情報・ニュースを取得します。

**パラメータ:**
- `category`: ニュースカテゴリ (任意)
- `limit`: 取得件数 (デフォルト: 10)

**レスポンス:**
```json
[
  {
    "id": "news_1",
    "title": "インフルエンザの流行状況について",
    "content": "今シーズンのインフルエンザが...",
    "category": "感染症情報",
    "hospital_id": "hospital_1",
    "hospital_name": "市立総合病院",
    "published_at": "2024-01-01T00:00:00Z",
    "priority": "high",
    "tags": ["インフルエンザ", "予防"],
    "image_url": "https://example.com/image.jpg"
  }
]
```

### 健康アラート取得

```http
GET /news/health-alerts?area={area}&severity={severity}
```

健康アラート・緊急情報を取得します。

**パラメータ:**
- `area`: 地域 (任意)
- `severity`: 重要度 ("info", "warning", "danger") (任意)

**レスポンス:**
```json
[
  {
    "id": "alert_1",
    "title": "インフルエンザ流行警報",
    "message": "インフルエンザの感染者数が警報レベルに達しました。",
    "severity": "warning",
    "area": "東京都",
    "valid_until": "2024-01-15T00:00:00Z",
    "action_required": true
  }
]
```

### 病院ニュース取得

```http
GET /news/hospital-news/{hospital_id}?limit={limit}
```

特定の病院からのお知らせを取得します。

**パラメータ:**
- `hospital_id`: 病院ID
- `limit`: 取得件数 (デフォルト: 5)

### ニュースカテゴリ取得

```http
GET /news/categories
```

ニュースカテゴリ一覧を取得します。

**レスポンス:**
```json
{
  "categories": [
    {
      "id": "infection",
      "name": "感染症情報",
      "icon": "🦠"
    }
  ]
}
```

## エラーレスポンス

APIエラーは以下の形式で返されます：

```json
{
  "detail": "エラーメッセージ"
}
```

### HTTPステータスコード

- `200`: 成功
- `400`: リクエストエラー
- `401`: 認証エラー
- `404`: リソースが見つからない
- `500`: サーバーエラー

## レート制限

APIには以下のレート制限があります：

- 認証なし: 100リクエスト/分
- 認証あり: 1000リクエスト/分

制限に達した場合、HTTPステータス429が返されます。

## API バージョニング

現在のAPIバージョンは v1 です。URLパスに `/api/v1` を含めてアクセスしてください。

## OpenAPI/Swagger

インタラクティブなAPI ドキュメントは以下のURLで確認できます：

- 開発環境: `http://localhost:8000/docs`
- 本番環境: `https://your-backend-url.onrender.com/docs`