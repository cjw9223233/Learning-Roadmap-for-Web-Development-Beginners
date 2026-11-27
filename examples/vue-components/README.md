# Vue 巡檢元件實驗室

先完整複製此資料夾，在自己的副本開啟終端機。使用 Node.js 20 以上；本次實測 Node.js 24.12.0／npm 11.6.2。免建置，無須安裝套件。

```powershell
npm test
npm run serve
```

若 PowerShell 擋住 npm.ps1，改用 npm.cmd。開啟服務印出的 127.0.0.1 HTTP 網址；按 Ctrl+C 結束。預設 8080，可用 `npm run serve -- --port 8081`。直接雙擊 HTML 可讀說明，ES 模組互動需 HTTP。修改 JS 後重新整理，不需 build。

- `app.js`：父元件，擁有主清單、篩選與順序；computed 推導兩組統計。
- `components.js`：InspectionForm、InspectionRow、SummaryPanel。表單與列各有自己的編輯草稿；透過事件請父元件更新。
- `model.js`：新增、改名、結果變更、刪除與篩選；使用 `inspection.js` 的執行期契約驗證。
- `inspection.js`：沿用第 2C 的 JSON 驗證與統計；本課沒有新增 JSON 匯入介面。
- `model.test.js`：10 個模型行為測試，不掛載 Vue；元件協作需要另在瀏覽器驗證。
- `index.html`：父元件模板；同一 SummaryPanel 使用兩次。`row.id` 作為清單 key，反轉順序保留列實例；篩掉列會卸載，未儲存草稿消失。

新增後保留表單草稿，請先確認訊息再決定是否再次送出。編輯、切換結果與刪除只影響當頁記憶體；重新整理回到三筆虛構資料。不讀寫 localStorage、不連 API、沒有登入或後端。

Vue 是隨附的第三方程式：固定 **3.5.22 開發版 global build**，含模板編譯器，免建置但非正式部署設定。本課使用普通 JavaScript，沒有 .vue SFC、TypeScript 檢查、Router 或打包流程。完整教材與三個修改題在 [第 3A 課](../../lessons/03a-vue-components.md)。

Vue 發行檔從固定版本 URL 下載，未修改；保留 TLS 驗證。詳見 [MIT 授權](vendor/LICENSE.txt) 與 [來源／SHA-256](vendor/SOURCE.json)。雜湊記錄本地檔案完整性，不是獨立上游身分驗證。package-lock 沒有 registry 依賴，不涵蓋 vendor 檔案的內容；保留整個資料夾才能重現。開啟範例不從 CDN 載入程式。
