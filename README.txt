# Nikkei Leverage Analyzer

1570（日経レバ）と1360（日経平均ベア2倍）を5分足データで分析するAndroidアプリです。

## 機能
- 現在値
- SMA20
- EMA5 / EMA20
- RSI14
- トレンド
- スコア
- BUY候補 / HOLD
- 損切り・利確の機械的な目安
- 5分ごとの自動更新
- 429などの通信エラー表示
- 自動注文は行わない

## Android APK
このプロジェクトはKivy + BuildozerでAPK化できます。
Buildozerの公式手順では `buildozer -v android debug` でAPKを作成し、完成物は `bin/` に出力されます。

GitHub Actions用の `.github/workflows/build-apk.yml` も同梱しています。
GitHubへこのフォルダを置けば、ActionsからAndroid debug APKのビルドを実行できます。

## 注意
Yahoo Financeの5分足データは、常にリアルタイムまたは5分以内の遅延が保証されるものではありません。
また、このアプリは売買を保証するものではありません。
証券会社API接続・自動発注はまだ実装していません。
