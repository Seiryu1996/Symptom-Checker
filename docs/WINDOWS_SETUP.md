# Windows環境でのセットアップガイド

## 前提条件

- Docker Desktop for Windows
- WSL2の有効化（推奨）

## 1. Docker Desktop のセットアップ

### Docker Desktop のインストール

1. [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop) をダウンロード
2. インストール実行
3. WSL2 バックエンドを有効化

### WSL2 統合の設定

1. Docker Desktop を起動
2. Settings → Resources → WSL Integration
3. "Enable integration with my default WSL distro" をオン
4. 使用するWSLディストリビューションを選択してオン
5. "Apply & Restart" をクリック

## 2. プロジェクトの起動

### PowerShellまたはコマンドプロンプトで実行

```cmd
# プロジェクトディレクトリに移動
cd C:\Users\上畑成龍\Desktop\dev\Symptom-Checker

# 環境変数ファイルをコピー
copy .env.example .env

# Dockerコンテナをビルド・起動
docker-compose up -d --build
```

### WSL2環境で実行（推奨）

```bash
# WSL2でプロジェクトディレクトリに移動
cd /mnt/c/Users/上畑成龍/Desktop/dev/Symptom-Checker

# 環境変数ファイルをコピー
cp .env.example .env

# Dockerコンテナをビルド・起動
docker-compose up -d --build
```

## 3. アクセス確認

起動後、以下のURLにアクセスできることを確認：

- **フロントエンド**: http://localhost:8080
- **バックエンドAPI**: http://localhost:8000
- **API ドキュメント**: http://localhost:8000/docs
- **PostgreSQL**: localhost:5432

## 4. 開発環境での操作

### ログの確認

```cmd
docker-compose logs -f
```

### 特定のサービスのログ

```cmd
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres
```

### コンテナ内に入る

```cmd
# バックエンドコンテナ
docker-compose exec backend bash

# フロントエンドコンテナ
docker-compose exec frontend sh

# データベースコンテナ
docker-compose exec postgres psql -U user -d symptom_checker
```

### 停止・再起動

```cmd
# 停止
docker-compose stop

# 再起動
docker-compose restart

# 完全停止（コンテナ削除）
docker-compose down

# 完全停止（ボリューム含む）
docker-compose down -v
```

## 5. トラブルシューティング

### 問題: Docker Desktop が起動しない

**解決方法:**
1. Windows機能の有効化：
   - "Windows Subsystem for Linux"
   - "仮想マシンプラットフォーム"
2. WSL2の更新：
   ```cmd
   wsl --update
   ```

### 問題: ポートが使用中

**解決方法:**
```cmd
# ポート使用状況を確認
netstat -ano | findstr :8080
netstat -ano | findstr :8000

# プロセスを終了（PIDを確認してから）
taskkill /PID <プロセスID> /F
```

### 問題: ビルドエラー

**解決方法:**
```cmd
# Dockerキャッシュをクリア
docker system prune -f

# 強制リビルド
docker-compose build --no-cache
```

### 問題: WSL2でファイルパーミッションエラー

**解決方法:**
```bash
# ファイル権限を修正
chmod +x frontend/cmd/main.go
chmod -R 755 backend/
```

## 6. 便利なコマンド

### Make コマンドの使用（WSL2環境）

```bash
# 開発環境起動
make dev

# ログ確認
make logs

# テスト実行
make test

# クリーンアップ
make clean
```

### Windows向けバッチファイル

プロジェクトルートに以下のファイルを作成：

**start.bat**
```bat
@echo off
echo Starting Symptom Checker...
docker-compose up -d --build
echo.
echo Services are running:
echo   Frontend: http://localhost:8080
echo   Backend: http://localhost:8000
echo   API Docs: http://localhost:8000/docs
echo.
echo Press Ctrl+C to view logs, or close this window
docker-compose logs -f
```

**stop.bat**
```bat
@echo off
echo Stopping Symptom Checker...
docker-compose down
echo Services stopped.
pause
```

## 7. Visual Studio Code 統合

### 推奨拡張機能

- Docker
- Remote - WSL
- Go (Go開発用)
- Python (Python開発用)
- REST Client (API テスト用)

### WSL環境での VS Code 起動

```bash
# WSL2でプロジェクトディレクトリから起動
code .
```

## 8. パフォーマンス最適化

### WSL2でのファイルシステム最適化

1. プロジェクトをWSL2のファイルシステムに配置：
   ```bash
   # Windowsからファイルをコピー
   cp -r /mnt/c/Users/上畑成龍/Desktop/dev/Symptom-Checker ~/symptom-checker
   cd ~/symptom-checker
   ```

2. この場合のアクセスパス：
   ```bash
   \\wsl$\Ubuntu\home\<username>\symptom-checker
   ```

### Docker Desktop リソース設定

1. Docker Desktop → Settings → Resources
2. Memory: 4GB以上推奨
3. CPU: 2コア以上推奨
4. Disk image size: 十分な容量を確保

## 9. 本番環境デプロイ準備

### 環境変数の確認

```cmd
# .envファイルを編集
notepad .env
```

本番環境用の値を設定：
- `DEBUG=false`
- `SECRET_KEY=<強力なランダム文字列>`
- `DATABASE_URL=<本番データベースURL>`

### デプロイ確認

```cmd
# デプロイ設定確認
docker-compose -f docker-compose.yml -f docker-compose.prod.yml config
```

これでWindows環境での症状チェッカーサービスの開発環境が構築できます。