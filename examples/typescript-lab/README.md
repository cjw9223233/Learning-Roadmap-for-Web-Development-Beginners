# TypeScript 巡檢練習

先完整複製此資料夾，再在副本開啟終端機。Node.js 20 以上；本次實測 Node.js 24.12.0／npm 11.6.2。使用虛構資料，沒有瀏覽器保存。

```powershell
npm ci --ignore-scripts --offline --audit=false --fund=false
npm run compiler:version
npm run check
npm run build
npm run demo
npm test
npm run demo:assertion
npm run serve
```

PowerShell 若擋住 npm.ps1，使用 npm.cmd 代替。從 serve 印出的 127.0.0.1 HTTP 網址操作；按 Ctrl+C 結束。預設 8080，可用 `npm run serve -- --port 8081`。隨附真正編譯的 dist 可供預覽；修改 src 後重新 build 再整理。完整教學在教材的 [第 2D 課](../../lessons/02d-typescript.md)。

- `src/inspection.ts`：型別與執行期驗證；`src/examples.ts`：有型別的範例資料。
- `src/app.ts`：瀏覽器入口；`src/assertion-demo.ts`：刻意使用 as 展示其限制。
- `src/type-errors.ts`：四個刻意錯誤，正常建置排除。`npm run check:errors` 原版預期失敗；修正後才成功，不輸出 JS。
- `dist/`：由真正 TypeScript 編譯器產生的 JS。`noEmitOnError` 阻止錯誤建置產生新輸出，但不移除舊 dist。
- `cli.js`、`assertion-cli.js` 與測試為普通 JS，沒有納入本課 TS 檢查。`npm test` 先建置再測試；`npm run test:runtime` 只測既有 dist。

本課的離線 devDependency 是 `file:vendor/typescript`，固定版本 6.0.3。`npm ci` 只連結這個隨附資料夾，不需要 registry 或已有快取。必須保留 vendor 與 lock；此結果不代表任意 npm 專案皆可離線安裝。

`vendor/typescript` 的編譯器 API 與標準宣告檔來自本機已安裝 VS Code 的 TypeScript 套件，未修改程式內容；包裝 metadata 已替換並省略官方 CLI、server、API typings 與翻譯。詳見 [NOTICE](vendor/typescript/NOTICE.txt)、[授權](vendor/typescript/LICENSE.txt)、[SHA-256 紀錄](vendor/typescript/SHA256.json)。雜湊用於偵測隨附檔案變動，不是獨立的上游身分驗證。

`tools/compiler.cjs` 是本教材的小型 API 驅動程式，讀取 tsconfig，以 createProgram、getPreEmitDiagnostics、emit 做真正的型別檢查與輸出；只支援本課的 --project、--noEmit 與 --version，不冒充完整 tsc。無須全域安裝套件，也沒有關閉 TLS 驗證。
