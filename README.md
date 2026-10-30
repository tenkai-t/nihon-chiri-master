# 日本地理マスター — Codex移行用 v15

移行後の変更：漢字とかなの混在回答に対応しました（例：「北かいどう」「ほっかい道」「富士さん」）。「正式表記のみ正解」の設定は維持しています。現在の配信版は `startup-header-20261030` です。起動画面で重複していた上部のプレイヤー選択ボタンを非表示にし、選択後のプレイヤー切り替えは維持しています。以下の同一性・移行報告は取得時点の記録で、本番サイトへの公開を示すものではありません。

公開中の日本地理マスターを引き継ぐためのプロジェクトです。新しいゲームや公開サイトは作成していません。

- 元サイト：https://nihon-chiri-master.prime-otter-8314.chatgpt.site
- 確認した公開版：v15（2026-10-28に管理情報を再確認）
- 元コミット：`b7a01ab65fe2a9fa852514e3a6a3ed63da7335f6`
- ブラウザ実行コード、教材、地図、認識モデル、サーバーの採点・認証コードは元版と同一です。
- ZIPには本番DB、実プレイヤーデータ、本人/先生用パスワード、復旧コード、APIトークンを含めません。

## 最初の起動

Node.js 24以上、npm、Python 3.8以上が必要です。検証環境はNode.js 24.22.1 / Python 3.12.14です。WindowsではPythonをPATHへ追加してください。

ZIPを解凍し、このREADMEとpackage.jsonがあるフォルダで実行します。

```sh
npm ci
npm run dev
```

自動ビルド後、`http://localhost:4173/` をブラウザで開きます。終了はターミナルでCtrl+Cです。HTMLファイルのダブルクリック（file://）では起動しないでください。

Pythonの検出順は `python3` → `python` → `py -3`。必要なら環境変数 `JAPAN_GEOGRAPHY_PYTHON` に実行ファイルを指定できます。Windowsの日本語データ読み込みに備え、ビルド時はUTF-8モードを有効にします。

```sh
npm run build          # 教材の整合した配信版とWorkerを生成。公開しない
npm test               # 元版の18スイート
npm run test:migration # 同一性とlocalhost/APIアダプターの追加検証
npm run check          # ビルド＋上記すべて
```

開発サーバーのランキングDBは**ローカルのメモリー内だけ**です。停止すると人工的な公式挑戦のデータは消えます。端末内学習記録はブラウザに残ります。実際の児童のバックアップは開発環境へ入れず、人工データを使用してください。

## 実装されている内容

47都道府県・47件の県庁所在地情報・地形160件。4択、文字入力、単文字手書き候補認識、地図タップ、輪郭・説明形式。地方別、地形難易度、練習、ヒントなしテスト、復習、全問制覇、90秒、日替わり、図鑑、記録・自己ベスト、児童別オンライン公式ランキング、本人/先生の保護、バックアップ、PWAを含みます。

詳細は [GAME_SPEC.md](GAME_SPEC.md)、Codexの作業ルールは [AGENTS.md](AGENTS.md)、移行の境界と手順は [MIGRATION.md](MIGRATION.md)、今回の取得・試験結果は [MIGRATION_REPORT.md](MIGRATION_REPORT.md) を参照してください。

## 主なファイル

| 場所 | 内容 |
|---|---|
| dist/index.html / app.js / style.css | 配信入口と画面・学習処理 |
| dist/security.js / online.js | 端末内保護と公式ランキングのクライアント |
| dist/assets/ | 地理教材、地図、構造化ヒント、手書き認識データ |
| dist/releases/ | 既存の不変な配信版。現在の参照先も含む |
| dist/sw.js / bootstrap.js / repair.html | オフライン、初期起動、起動修復 |
| dist/manifest.json / icons/ / licenses/ | PWA、画像・SVG、利用条件 |
| server/ | WorkerのAPI処理、旧順位表、ローカルSQLite互換層 |
| db/ / drizzle/ | DB構造定義とマイグレーション。実データなし |
| scripts/ | ビルド、教材編集、Work用・localhost用の開発処理 |
| tests/ | DOM、SQLite、採点、認証、ヒント、オフライン等の回帰試験 |
| UPSTREAM_SOURCE.json | 元コミットと元ファイルごとのSHA-256、除外・補助変更の記録 |

## Cloudflareでの開発・公開

Workers＋専用D1向けの設定を追加しています。`npm run cf:check` で公開せずにビルド確認、`npm run cf:db:local` と `npm run cf:dev` でローカル起動できます。手順と認証設定は [Cloudflare手順](docs/CLOUDFLARE.md) を参照してください。Cloudflareへの公開は未実施です。旧サイトは残し、新しいURLで公開する方針です。

## 公開とデータ

このZIPをGitHubに登録しても、現在のSitesやDBへ自動反映されません。公開変更には別途、所有者の明示的な承認が必要です。GitHub PagesだけではサーバーAPI/D1は動きません。

**別のURLでは、既存ブラウザ内の学習記録・認証・キャッシュを自動で引き継げません。現在の学習バックアップ復元は「新しいIDで追加」する仕様です。既存IDのまま別環境へ移す処理は今回実装・実行していません。** 同じ公開URL・同じDBを維持する公開手順が確定するまでは、元サイトを使い続けてください。

## GitHubへの登録（Windows）

1. ZIPを解凍する。ZIPそのものをリポジトリへアップロードしない。
2. GitHub Desktopでリポジトリのローカルフォルダを開く。
3. このプロジェクトの中身をそのフォルダへコピーする。package.jsonとAGENTS.mdがリポジトリ直下に来るようにする。
4. `.gitignore` が含まれていることを確認し、node_modules、生成Worker、DB、個人バックアップを追加しない。
5. Commit → Pushを行い、Codexでそのリポジトリを選ぶ。公開情報だけのコードでも、まず非公開リポジトリでの運用を推奨する。

## ライセンスと既知の制約

第三者の地図・水系・KanjiVGなどの利用条件は、教材の出典とdist/licenses/を維持してください。プロジェクト全体に新しいオープンソースライセンスを勝手に付与していません。

スマートフォン実機、OSキーボード、物理ピンチ、Windows PCでの実行は今回未確認です。HTTPプレビューでのPWA/安全なCookieの挙動には環境差があります。テストの人工筆跡の成績は、人の筆跡の認識精度を示すものではありません。

<!-- Migration verification note -->
旧Git履歴がなくてもテストできるよう、過去公開コードの比較fixtureとSHA-256を同梱しています。元の学習ロジック比較を省略していません。
