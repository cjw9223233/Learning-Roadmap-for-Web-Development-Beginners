# Vue SFC 與 Vite 實作

完整複製此資料夾到自己的練習位置；保留 vendor 與 package-lock.json，不複製 node_modules。本課實測並要求 **Node.js 24.22.3 至 24.x**（npm 11.6.2）；啟動 Vite 前會檢查版本。這是本課重現範圍，較 Vite 7 官方基本條件嚴格；此機 Node.js 24.12.0 的打包程序曾崩潰。

```powershell
node --version
npm ci --ignore-scripts --audit=false --fund=false
npm test
npm run dev
# 結束 dev 後，或另開終端機：
npm run build
npm run preview
```

PowerShell 若擋住 npm.ps1，改用 npm.cmd。dev 預設 5173，preview 預設 4173，均只綁定 127.0.0.1。按 Ctrl+C 停止。埠被使用時會拒絕啟動，可加 `-- --port 5174` 等明確指定埠。

只讀隨附產物可用 `node serve-dist.js`，不需要 node_modules；此小服務可用既有 Node.js 24.12.0，預設 8080，可加 `--port 8081`。它只讀 dist，修改 src 不會自動重建。直接雙擊 HTML 無法編譯或正常載入模組。

- `src/main.js` 匯入 App.vue 與全域 CSS，掛載到根 HTML。
- `src/App.vue` 管主清單與 computed；`src/components/` 是三個子元件。
- `script setup` 的頂層變數可供模板使用；defineProps／defineEmits 是編譯巨集。
- `SummaryPanel.vue` 有 scoped 樣式。scoped 是選擇器轉換，不是權限或資料隔離。
- `src/model.js`／`inspection.js` 沿用第 3A 的執行期規則，`model.test.js` 的 10 個測試不掛載元件。
- `dist/` 由本課固定工具真正建置；修改來源後需成功 build。preview 只讀產物，不是正式部署伺服器。
- `public/THIRD_PARTY_NOTICES.txt` 保留 Vue 與 Vite 的授權／通知，建置時複製到 dist。

固定 Vue 3.5.22、Vite 7.3.8、Vue 外掛 6.0.11。package.json 的 overrides 使用 `vendor/rollup-wasm-node-4.68.8.tgz`，為官方未修改的 Rollup WASM 套件；授權在套件內，來源與雜湊在 vendor/SOURCE.json，下載保留 TLS 驗證，sha512 比對 registry metadata。此配置與 Node.js 24.22.3 一併實測；不宣稱 WASM 本身已修復 Node.js 24.12.0 的崩潰，也不保證所有平台相容。

安裝其他依賴仍通常需要網路；此資料夾不是完整離線安裝包。本次隔離測試使用已填入的快取離線 ci，不能推論空快取也可離線安裝。保留 lock 並使用 HTTPS registry，勿關閉 TLS 驗證。略過安裝生命週期腳本不代表後續明確執行的 build／dev 不會執行工具程式。

不手動編輯 dist，不把成功 build 當成型別檢查或操作驗證。此例使用普通 JavaScript，沒有 Router、登入、資料庫或永久保存。重新整理還原三筆虛構資料，不讀寫原教材的 localStorage。完整課程在 [第 3B 課](../../lessons/03b-vue-sfc.md)。
