# unnei_achievements

運営課売上ダッシュボードの自動配信用リポジトリ。

- `public/index.html`: Firebase Authログインゲート付きダッシュボード（Cowork側のscheduled taskが毎日上書きしてpush）
- `status.json`: その日の集計成否ステータス（success/failed）。GitHub Actionsが参照
- `.github/workflows/deploy.yml`: push検知でFirebase Hostingへデプロイ、ChatWorkへ成功/失敗通知
- `add_auth_gate.py`: 集計ツール側でdashboard.html生成後にこのスクリプトでログインゲートを付与する
