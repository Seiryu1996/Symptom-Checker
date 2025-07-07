# デプロイガイド

このドキュメントでは、症状チェッカーサービスをRenderにデプロイする方法を説明します。

## 前提条件

- Gitリポジトリがセットアップ済み
- Renderアカウントの作成
- GitHub連携の設定

## Renderでのデプロイ手順

### 1. リポジトリをGitHubにプッシュ

```bash
git add .
git commit -m "Initial deployment setup"
git push origin main
```

### 2. Renderでのサービス作成

#### データベースの作成

1. Render Dashboard → "New" → "PostgreSQL"
2. 設定:
   - Name: `symptom-checker-db`
   - Database Name: `symptom_checker`
   - User: `symptom_user`
   - Plan: Free

#### バックエンドサービス（FastAPI）

1. Render Dashboard → "New" → "Web Service"
2. リポジトリを選択
3. 設定:
   - Name: `symptom-checker-backend`
   - Environment: `Python 3`
   - Build Command: `pip install -r backend/requirements.txt`
   - Start Command: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Plan: Free

4. 環境変数を設定:
   ```
   DATABASE_URL=<PostgreSQLの接続文字列>
   FASTAPI_HOST=0.0.0.0
   FASTAPI_PORT=$PORT
   SECRET_KEY=<ランダムな秘密鍵>
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   DEBUG=false
   CORS_ORIGINS=https://symptom-checker-frontend.onrender.com
   ```

#### フロントエンドサービス（Go）

1. Render Dashboard → "New" → "Web Service"
2. リポジトリを選択
3. 設定:
   - Name: `symptom-checker-frontend`
   - Environment: `Go`
   - Build Command: `go build -o main ./cmd/main.go`
   - Start Command: `./main`
   - Plan: Free

4. 環境変数を設定:
   ```
   GO_HOST=0.0.0.0
   GO_PORT=$PORT
   BACKEND_URL=https://symptom-checker-backend.onrender.com
   DEBUG=false
   ```

### 3. YAMLファイルでのデプロイ（推奨）

`render.yaml`ファイルを使用してインフラストラクチャをコードとして管理:

```bash
# リポジトリルートに render.yaml を配置済み
git add render.yaml
git commit -m "Add Render deployment configuration"
git push origin main
```

Render Dashboard で "New" → "Blueprint" を選択し、リポジトリからデプロイ。

## 環境変数の設定

### バックエンド

| 変数名 | 説明 | 例 |
|--------|------|-----|
| `DATABASE_URL` | PostgreSQL接続文字列 | `postgresql://user:pass@host:port/db` |
| `SECRET_KEY` | JWT署名用秘密鍵 | `your-secret-key-here` |
| `CORS_ORIGINS` | CORS許可オリジン | `https://your-frontend.onrender.com` |

### フロントエンド

| 変数名 | 説明 | 例 |
|--------|------|-----|
| `BACKEND_URL` | バックエンドAPI URL | `https://your-backend.onrender.com` |
| `GO_PORT` | ポート番号 | `$PORT` (Renderが自動設定) |

## データベースマイグレーション

初回デプロイ後、データベースのセットアップが必要です:

```bash
# Renderのシェルアクセスまたはローカルでの実行
# データベースURLを環境変数に設定して実行
python -m alembic upgrade head
```

## SSL/TLS証明書

Renderは自動的にSSL証明書を提供します。カスタムドメインを使用する場合:

1. Render Dashboard → Service → "Settings" → "Custom Domains"
2. ドメインを追加
3. DNS設定でCNAMEレコードを設定

## 監視とログ

### ログの確認

```bash
# Render Dashboard → Service → "Logs"
# またはRender CLIを使用
render logs --service symptom-checker-backend
```

### ヘルスチェック

各サービスには以下のヘルスチェックエンドポイントが設定されています:

- バックエンド: `https://your-backend.onrender.com/health`
- フロントエンド: `https://your-frontend.onrender.com/health`

## トラブルシューティング

### よくある問題

1. **ビルドエラー**
   ```bash
   # 依存関係の問題
   pip install -r backend/requirements.txt
   go mod tidy
   ```

2. **データベース接続エラー**
   ```bash
   # 環境変数を確認
   echo $DATABASE_URL
   ```

3. **CORS エラー**
   ```python
   # backend/app/main.py でCORS設定を確認
   origins = config("CORS_ORIGINS", default="*").split(",")
   ```

### パフォーマンス最適化

1. **静的ファイルの最適化**
   - CSS/JSファイルの圧縮
   - 画像の最適化

2. **データベースクエリの最適化**
   - インデックスの追加
   - クエリの最適化

3. **キャッシングの実装**
   - Redisキャッシュ（有料プランで利用可能）
   - アプリケーションレベルキャッシング

## スケーリング

Renderの無料プランには制限があります。本格運用時は以下を検討:

1. **有料プランへのアップグレード**
   - より多くのリソース
   - 常時稼働
   - 高速ビルド

2. **データベースのスケーリング**
   - より大きなインスタンス
   - 読み取り専用レプリカ

3. **CDNの使用**
   - 静的ファイルの配信最適化
   - 画像の最適化

## セキュリティ

1. **環境変数の管理**
   - 秘密情報はRenderの環境変数で管理
   - `.env`ファイルをGitにコミットしない

2. **HTTPS の強制**
   ```python
   # 本番環境ではHTTPS リダイレクトを有効化
   if not config("DEBUG", default=False, cast=bool):
       app.add_middleware(HTTPSRedirectMiddleware)
   ```

3. **セキュリティヘッダー**
   ```python
   # セキュリティミドルウェアの追加
   app.add_middleware(
       SecurityHeadersMiddleware,
       csp="default-src 'self'",
       hsts=True
   )
   ```

## バックアップ

1. **データベースバックアップ**
   - Renderの自動バックアップ機能
   - 手動バックアップの定期実行

2. **コードのバックアップ**
   - GitHubリポジトリ
   - 複数ブランチでの管理

## 本番運用チェックリスト

- [ ] 環境変数の設定確認
- [ ] データベースマイグレーション実行
- [ ] ヘルスチェックエンドポイントの確認
- [ ] SSL証明書の確認
- [ ] ログ出力の確認
- [ ] エラー監視の設定
- [ ] バックアップの設定
- [ ] セキュリティ設定の確認
- [ ] パフォーマンステストの実行

## サポートとメンテナンス

定期的なメンテナンス作業:

1. **依存関係の更新**
   ```bash
   pip-review --local --auto
   go get -u all
   ```

2. **セキュリティアップデート**
   - 定期的な脆弱性スキャン
   - パッケージのセキュリティアップデート

3. **パフォーマンス監視**
   - レスポンス時間の監視
   - リソース使用量の確認

4. **ログ分析**
   - エラーログの分析
   - アクセスパターンの分析