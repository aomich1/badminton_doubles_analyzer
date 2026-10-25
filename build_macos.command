#!/bin/sh
set -eu
cd "$(dirname "$0")"
LOG="build_macos.log"
if ! python3 -m pip install -r requirements.txt >"$LOG" 2>&1; then
  echo "依存パッケージのインストールに失敗しました。ログ末尾:"
  tail -n 40 "$LOG"
  read -r -p "Enter キーで閉じます..."
  exit 1
fi
if ! python3 -m PyInstaller --noconfirm --clean --windowed --onedir \
  --name BadmintonDoublesAnalyzer \
  --osx-bundle-identifier com.badminton.doublesanalyzer \
  --add-data "web:web" \
  app.py >>"$LOG" 2>&1; then
  echo "Macアプリのビルドに失敗しました。ログ末尾:"
  tail -n 60 "$LOG"
  read -r -p "Enter キーで閉じます..."
  exit 1
fi
APP="dist/BadmintonDoublesAnalyzer.app"
echo "Portable app bundle: $APP"
echo "Build log: $LOG"
if /usr/bin/open "$APP"; then
  echo "アプリを起動しました。既定のブラウザーで分析画面を開きます。"
else
  echo "Launch Services から開けなかったため、アプリ本体を直接起動します。"
  "$APP/Contents/MacOS/BadmintonDoublesAnalyzer" >/dev/null 2>&1 &
  APP_PID=$!
  sleep 1
  if kill -0 "$APP_PID" 2>/dev/null; then
    echo "アプリを起動しました。既定のブラウザーで分析画面を開きます。"
  else
    echo "アプリの起動に失敗しました。Finder で $APP を開き、build_macos.log を確認してください。"
    exit 1
  fi
fi
