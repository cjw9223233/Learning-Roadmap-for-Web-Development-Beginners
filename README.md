# Web 開發初學者學習路線

以「車站設備巡檢」逐步練習 Web 開發。第一版：2026-11-17；目前更新：2026-11-26。

## 開始閱讀

- 雙擊 `index.html`：互動教材，無須安裝套件或連線即可閱讀與勾選驗收。
- 開啟 `教材.md`：同一份內容的 Markdown 自學版本。
- 初學者先開啟 `lessons/00-first-web.html`：建立第一個網頁、觀察標題與網址，再完成 HTTP 七種情境練習；同目錄有 Markdown 版。
- 接著開啟 `lessons/01-form-dom.html`：HTML 表單、CSS、JavaScript 資料與 DOM 的八步練習，附三個修改題與解答；同目錄有 Markdown 版。
- `examples/form-dom/` 有三個進度版本與備註練習完整解答，均可離線開啟。這組範例只有當頁記憶體，重新整理即清空，與下方具有本機保存的舊巡檢範例不同。
- 第 2 階段 A：開啟 `lessons/02-json-storage.html`，學習 JSON、保存與備份，附八步操作與三個驗證練習；同目錄有 Markdown 版。
- `examples/json-storage/index.html`：新增只改記憶體、保存才寫入瀏覽器；讀檔、驗證匯入與保存分開操作。包含正常、語法錯誤與欄位不合規的範例檔。這個獨立練習不讀寫舊巡檢資料。
- 第 2 階段 B：開啟 `lessons/02b-fetch.html`，學習真實 Fetch、非同步、HTTP／JSON／資料錯誤、取消與逾時；同目錄有 Markdown。實際操作先在專案根目錄執行 `python examples/fetch-lab/server.py`，再開啟印出的本機網址。結束後按 Ctrl+C。
- 第 2 階段 C：開啟 `lessons/02c-modules-npm.html`，學習共用模組、npm scripts 與鎖定檔；同目錄有 Markdown。將 `examples/modules-npm/` 複製到自己的練習位置，在副本執行 `npm run demo`、`npm test`、`npm run serve`，不需第三方套件。瀏覽器模組互動需從服務印出的 HTTP 網址開啟。
- 第 2 階段 D：開啟 `lessons/02d-typescript.html`，學習型別、縮小、真實編譯與執行期驗證；同目錄有 Markdown。完整複製 `examples/typescript-lab/` 後，依課程執行離線 `npm ci`、`npm run check`、`npm test`、`npm run serve`。隨附固定的 TypeScript 6.0.3 編譯器 API 子集與授權，無須全域安裝；四個刻意錯誤另用 `npm run check:errors`，原版預期失敗。
- 第 3 階段 A：開啟 `lessons/03a-vue-components.html`，用真正的 Vue 學元件、Props、事件、ref／computed 與穩定 key；同目錄有 Markdown。完整複製 `examples/vue-components/`，在副本執行 `npm test` 與 `npm run serve`，免建置且無須安裝套件。隨附固定 Vue 3.5.22 開發版與 MIT 授權，操作時不連 CDN；資料只保留在當頁記憶體。
- 第 3 階段 B：開啟 `lessons/03b-vue-sfc.html`，學習真正的 .vue、script setup、scoped 與 Vite dev／build／preview；同目錄有 Markdown。完整複製 `examples/vue-sfc/`（保留 vendor 與 lock、不要複製 node_modules），使用本課實測 Node.js 24.22.3 至 24.x，依課程執行 ci、測試與建置。只讀隨附產物可在副本執行 `node serve-dist.js`，免安裝依賴。
- 雙擊 `examples/http-lab.html`：完全離線的請求／回應模擬器。支援 GET、POST、200／201／400／404／405／500 與沒有 HTTP 回應的情境；資料僅保留在當頁記憶體。
- 雙擊 `examples/inspection.html`：可操作的巡檢表單，支援新增、篩選、刪除、本機保存與 JSON 匯出。

互動教材包含九階段內容、A 工作工具／B 全端系統／C AI 應用三種路線、練習步驟、程式範例、驗收清單與九題附解釋的小測驗。框架、後端、部署部分為實作導航，需搭配選定技術的官方文件；範例沒有完整後端服務或身分驗證。

所有操作使用虛構資料。驗收進度與巡檢資料儲存在目前瀏覽器；不同瀏覽器、檔案位置、私密模式與清除資料可能影響保存。請使用 JSON 匯出備份。教材的進度匯入會先確認取代；既有 `examples/inspection.html` 只有匯出。新的 `json-storage` 練習可讀取及驗證自己的版本化備份，格式與舊巡檢純陣列、主教材進度檔不同，不能直接混用。

## 如需本機 HTTP 服務

一般閱讀不需要伺服器。階段 2 的 Fetch 練習需要同來源 HTTP 服務；如已安裝 Python，在本資料夾執行：

```powershell
python -m http.server 8000 --bind 127.0.0.1
```

然後開啟 <http://localhost:8000>，結束後按 Ctrl+C。這個伺服器僅供本機練習，沒有將網站公開上線。

第 2 階段 B 要觀察完整 API 情境，改用專用命令 `python examples/fetch-lab/server.py`，預設網址為 <http://127.0.0.1:8765/>。若連接埠被使用，可加 `--port 8766`。此服務只綁定 127.0.0.1；提供固定虛構資料與教學錯誤情境，沒有資料庫或正式部署。直接雙擊 Fetch 練習頁仍可閱讀，但不會發出 API 請求。

## 編輯教材

- `course.json`：共用教材來源。內容更動後執行 `python build.py`，同步產生 HTML 與 Markdown。
- `build.py`：使用 Python 標準函式庫，不需安裝依賴。
- `build_lessons.py` 與 `lessons/00-first-web.json`：逐步練習的共用來源與產生器；一併由 `python build.py` 更新兩種格式與起始 HTML。
- `build_stage1.py`、`lessons/01-form-dom.json` 與 `lessons/snippets/01-form.*`：第 1 階段共用來源。修改來源後執行 `python build.py`；會同步更新課程與 `examples/form-dom/`，請在自己的副本練習以免被重新產生覆寫。
- `build_stage2.py` 與 `lessons/02-json-storage.json`：產生第 2 階段 A 的 HTML／Markdown；互動程式直接維護於 `examples/json-storage/`，不由建置器覆寫。`samples/bad-json.json` 刻意為不合法 JSON，供失敗測試使用。
- `build_fetch.py` 與 `lessons/02b-fetch.json`：產生第 2 階段 B 的兩種閱讀格式；`examples/fetch-lab/` 的 HTML、JS、CSS、資料與 Python 伺服器直接維護，不會在建置時被覆寫。
- `build_modules.py` 與 `lessons/02c-modules-npm.json`：產生第 2 階段 C 的兩種閱讀格式；`examples/modules-npm/` 是直接維護的零依賴 npm 範例，不會由建置器覆寫。原版含 10 個 Node.js 測試。本課實測 Node.js 24.12.0／npm 11.6.2，沒有全域套件安裝。
- `build_typescript.py` 與 `lessons/02d-typescript.json`：產生第 2 階段 D 的 HTML／Markdown。`examples/typescript-lab/src/` 是 TypeScript 來源，`dist/` 是真正編譯輸出；修改來源後在該專案成功執行 `npm run build`，教材建置不會代為編譯。`tools/compiler.cjs` 是教材驅動程式，使用隨附 6.0.3 API 做型別診斷與 emit；來源、Apache 2.0 授權與完整性紀錄在 `vendor/typescript/`。
- `build_vue.py` 與 `lessons/03a-vue-components.json`：產生第 3 階段 A 的 HTML／Markdown。`examples/vue-components/` 的程式直接維護，主教材建置不覆寫。Vue 發行檔、MIT 授權、固定網址與雜湊在 `vendor/`；沒有 registry 依賴，lock 不記錄隨附 Vue 檔案的內容。
- `build_sfc.py` 與 `lessons/03b-vue-sfc.json`：產生第 3B 階段的兩種閱讀格式。`examples/vue-sfc/src/` 為來源，dist 為真正 Vite 建置輸出；主教材 build.py 不代為編譯 SFC。此例固定 Vite 7.3.8／Vue 外掛 6.0.11／Vue 3.5.22，並使用隨附的官方 Rollup WASM tarball override。`scripts/check-node.js` 在工具啟動前檢查本課 Node.js 範圍。
- `assets/style.css`：響應式閱讀版面。
- `assets/app.js`：路線篩選、進度、測驗與備份。
- `examples/inspection.html`：可讀取原始碼的獨立練習範例。
- `assets/http-lab.js` 與 `examples/http-lab.html`：離線 HTTP 教學模型，不會發出真實 API 請求；重新整理會還原起始資料。
- `驗證紀錄.md`：本次檢查結果及限制。

## 排程來源

此教材由既有 `web-2026` 任務在本專案產出，原排程為每天台北時間下午 3:00。本檔僅記錄來源，不建立或修改排程。

資料來源、核對範圍與日期列於教材末尾。九階段與三種路線為本教材的教學設計，不是官方認證課綱或保證完成時程。

## 後續深化

目前已有九階段導航，以及第 0、1、2A、2B、2C、2D、3A、3B 階段的逐步實作。第 2 階段已涵蓋 JSON／保存、Fetch、模組／npm 與 TypeScript 入門；第 3A 已提供元件與資料流，第 3B 已實作 SFC 與 Vite 開發／建置／預覽；下一步銜接路由及較完整的管理畫面。更新教材時保留原有驗收項目與進度鍵；不可把既有使用者勾選推論成已掌握新增內容。
