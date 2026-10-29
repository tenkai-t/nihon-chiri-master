# Cloudflare Workers + D1 で公開する

世界マスターの公開URL `https://world-master-atlas.t-t14.workers.dev/play` と同じく、Workersを公開先にする。世界マスター側のアカウント設定・ソース構成は未取得。日本地理マスターは画面とランキングAPIを同じWorkerで配信し、専用の新しいD1を使う。入口は `/`。

所有者の指定により、新しいURLで公開し、既存のChatGPT Sitesは残す。旧サイトのD1、世界マスターのWorker/DB、DNSには変更しない。旧URLの学習記録・認証・Cookie・オンライン参加資格・順位表は自動では移らない。既存の学習バックアップ復元は新ID追加方式なので、同じ本人IDを維持する移行ではない。

## ローカル開発と検証

Node.js 24以上、Python 3.8以上を用意し、リポジトリ直下で実行する。

```sh
npm ci
npm run check
npm run cf:check
npm run cf:db:local
npm run cf:dev -- --port 8787
```

別のターミナルで `npm run cf:smoke`。実際のworkerdとローカルD1に、人工データだけで参加資格・10問の採点・再送・順位保存を検証する。リモートURLは指定できない。ローカルD1は `.wrangler/state/` に残り、メモリーDBを使う `npm run dev` とは別物。Wranglerの設定・キャッシュ・ログは `.local/cloudflare/`（Git対象外）。ログに実ユーザーの情報を入れない。

`cf:check` は公開せずWorkerをビルドする。`dist/server/index.js` は既存のビルドで生成され、画面資産とAPIを含む。新しい配信版・チェックサム・明示的なSW更新を維持する。Wranglerは依存ロックで固定している。

ローカル起動時の `Request.cf` 取得警告は、地理情報メタデータ取得の失敗であり、リモートD1への接続を意味しない。このアプリの実行処理はそのメタデータを使用しない。上記のHTTP/API試験で実際の動作を確認する。

## 公開に必要な接続

この環境ではCloudflare接続が未設定。次を環境設定に登録する。秘密値をチャット・コード・設定ファイル・ログへ貼らない。

- `CLOUDFLARE_API_TOKEN`：世界マスターと同じ対象アカウントに限定したAPIトークン。Account / Workers Scripts / Edit と Account / D1 / Edit。アカウントの自動検出や照会を行う場合は Account Settings / Read も必要になり得る。DNS権限はこのworkers.dev公開には不要。
- `CLOUDFLARE_ACCOUNT_ID`：そのCloudflareアカウントのID。秘密鍵ではないが、環境変数で指定する。
- 通信許可：`api.cloudflare.com`。世界マスターの公開設定確認用に `world-master-atlas.t-t14.workers.dev` もドラフトへ追加済み。

環境設定を確認・保存し、環境をPublishする。この環境のPublishと、Cloudflareへのサイト公開は別の操作。設定反映後に `node scripts/cloudflare.mjs whoami` などの読み取りで接続を再確認する。トークンの表示・再発行・別トークン要求を先に行わない。

## 公開作業

所有者がCloudflareの画面で専用DB `nihon-chiri-master-db` を作成済み。Database ID `fd06b6db-9bf5-4907-8d0e-058f43a30ea2` とアカウントIDは `wrangler.jsonc` に設定済み。初期スキーマ適用とサイト公開はまだ未実施。GitHub連携で公開する場合、CodexへAPIトークンを登録する必要はない。以下のDB作成手順2～3は完了しているので再実行しない。

1. 正しいアカウントが選ばれていることを確認し、既存Worker一覧とD1一覧を読み取る。名前 `nihon-chiri-master` に既存リソースがある場合、所有者を確認するまで上書き・再利用しない。特に世界マスターのDBは選ばない。
2. 新規の専用D1を作る：

   ```sh
   node scripts/cloudflare.mjs d1 create nihon-chiri-master-db --location apac --update-config=false
   ```

3. 返されたUUIDだけを `wrangler.jsonc` の `database_id` に設定する。ゼロUUIDは未設定の目印であり、実DBではない（現在は実UUIDを設定済み）。未設定のままリモートSQL適用・公開を実行するとラッパーが停止する。
4. 新しく作成した空のD1であることを確認してから初期スキーマを適用する：

   ```sh
   node scripts/cloudflare.mjs d1 migrations apply DB --remote
   ```

   これは新規DBに対する操作。旧サイトや世界マスターのDBを取得・移行・初期化するコマンドではない。
5. `npm run check`、`npm run cf:check` とローカルのスモークテスト成功後、`npm run cf:deploy`。Wranglerが返す実際の公開URLを記録する。世界マスターのURLの接尾辞だけを根拠に公開成功やアカウント一致を推測しない。
6. 公開URLの `/` が200でリダイレクトなし、HTML/SWが `mixed-kana-20261030` を参照し、9配信ファイルのSHA-256が一致することを読み取りで確認する。新しいURLに必要な通信許可は、実URLが判明してから追加する。実ブラウザで混在回答、正式表記限定、PWA準備と明示更新も確認する。設定変更後の実ブラウザ・スマートフォン実機検証は別途必要。

GitHubへのPushだけで自動公開される設定は、現在は作成していない。必要なら、公開の成功を確認した後に、このWorkerだけを対象とするGit連携を別途設定する。
