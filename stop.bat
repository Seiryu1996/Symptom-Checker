@echo off
echo ====================================
echo  症状チェッカー サービス停止
echo ====================================
echo.

echo サービスを停止中...
docker-compose stop

if %ERRORLEVEL% NEQ 0 (
    echo ❌ 停止中にエラーが発生しました
) else (
    echo ✅ サービスを停止しました
)

echo.
echo 🗑️  コンテナとボリュームも削除しますか？
echo    [Y] はい（完全削除）
echo    [N] いいえ（再起動可能な状態で保持）
echo.
set /p choice="選択してください (Y/N): "

if /i "%choice%"=="Y" (
    echo.
    echo コンテナとボリュームを削除中...
    docker-compose down -v
    echo ✅ 完全に削除しました
) else (
    echo ✅ コンテナは保持されました（docker-compose up で再起動可能）
)

echo.
pause