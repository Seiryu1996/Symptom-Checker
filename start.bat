@echo off
echo ====================================
echo  症状チェッカー サービス
echo ====================================
echo.

echo Docker Desktopが起動していることを確認してください...
timeout /t 3 >nul

echo 環境変数ファイルをコピー中...
if not exist .env (
    copy .env.example .env >nul
    echo ✓ .env ファイルを作成しました
) else (
    echo ✓ .env ファイルは既に存在します
)

echo.
echo Dockerコンテナをビルド・起動中...
docker-compose up -d --build

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ エラーが発生しました
    echo.
    echo 以下を確認してください:
    echo 1. Docker Desktop が起動している
    echo 2. WSL2 統合が有効になっている
    echo 3. ポート 8080, 8000, 5432 が空いている
    echo.
    pause
    exit /b 1
)

echo.
echo ✅ サービスが起動しました！
echo.
echo 📍 アクセスURL:
echo   フロントエンド: http://localhost:8080
echo   バックエンドAPI: http://localhost:8000  
echo   API ドキュメント: http://localhost:8000/docs
echo.
echo 🔧 管理コマンド:
echo   ログ確認: docker-compose logs -f
echo   停止: docker-compose stop
echo   完全停止: docker-compose down
echo.
echo ブラウザを開いています...
timeout /t 2 >nul
start http://localhost:8080

echo.
echo ログを表示します（Ctrl+C で終了）:
echo.
docker-compose logs -f