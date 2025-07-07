# Symptom-Checker

症状チェッカーサービス - 症状から適切な医療機関を案内するWebアプリケーション

## 機能概要

| カテゴリ | 機能 | 目的 | 優先度 |
|----------|------|------|--------|
| 🔍 問診 | 自由入力・選択式症状入力 | 素早いヒアリング | ★★★ |
| 🧠 判断 | 症状 → 病気カテゴリ → 対応科 | 病院を特定するため | ★★★ |
| 🏥 紹介 | 病院検索 + 地図 + ワンクリック電話 | 最寄り・対応科の病院を紹介 | ★★★ |
| 📰 情報提供 | 各病院からの通知・注意喚起・ニュース | インフル流行などの予防情報 | ★★☆ |
| 🙋‍♂️ ユーザー登録 | 病院からのお知らせ通知など希望者向け | 常連患者向け機能 | ★☆☆ |
| 📞 電話連携 | スマホなら「tel:」リンクで電話発信 | 素早く行動に移せる | ★★★ |
| 📍 位置情報 | 現在地を取得して近くの病院を探す | 精度の高い紹介 | ★★☆ |

## 技術スタック

- **フロントエンド**: Go (Gin Framework)
- **バックエンド**: FastAPI (Python)
- **データベース**: PostgreSQL
- **開発環境**: Docker
- **デプロイ**: Render

## プロジェクト構造

```
Symptom-Checker/
├── backend/          # FastAPI バックエンド
│   ├── app/
│   │   ├── api/      # API エンドポイント
│   │   ├── models/   # データモデル
│   │   ├── services/ # ビジネスロジック
│   │   └── utils/    # ユーティリティ
│   └── Dockerfile
├── frontend/         # Go フロントエンド
│   ├── cmd/          # メインアプリケーション
│   ├── internal/     # 内部パッケージ
│   ├── web/          # ハンドラー
│   ├── templates/    # HTMLテンプレート
│   ├── static/       # 静的ファイル
│   └── Dockerfile
├── docker/           # Docker関連設定
├── docs/             # ドキュメント
├── docker-compose.yml
├── .env.example
└── README.md
```

## 開発環境セットアップ

### 前提条件

- Docker
- Docker Compose

### 起動手順

1. リポジトリをクローン
```bash
git clone <repository-url>
cd Symptom-Checker
```

2. 環境変数ファイルを作成
```bash
cp .env.example .env
```

3. Docker環境を起動
```bash
docker-compose up -d
```

4. アクセス
- フロントエンド: http://localhost:8080
- バックエンドAPI: http://localhost:8000
- API ドキュメント: http://localhost:8000/docs

## 開発フロー

1. 問診機能の実装
2. 症状判断ロジックの実装
3. 病院検索・紹介機能の実装
4. 電話連携機能の実装
5. 位置情報取得機能の実装
6. その他の機能

## デプロイ

Renderを使用したデプロイ設定は `/docker` ディレクトリに含まれています。