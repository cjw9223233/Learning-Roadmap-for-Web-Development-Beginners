# 第 3 階段 B｜Vue 單檔元件與 Vite 建置

更新：2026-11-26

把第 3A 的巡檢畫面改寫成真正的 .vue 單檔元件。從來源、開發伺服器、建置到靜態預覽，親手確認瀏覽器究竟執行哪一份程式。新增、篩選與編輯等資料規則延續前課。

## 準備

- 先完成第 3A，能追蹤 Props、事件、ref、computed 與草稿。完整複製 examples/vue-sfc 到自己的位置；練習時不要修改教材原版。不要複製 node_modules，依鎖定檔重新安裝。
- Vite 7 官方基本條件為 Node.js 20.19+／22.12+；此範例為重現本次實測，另固定 Node.js 24.22.3 至 24.x 與 npm 11.6.2。此機的 24.12.0 曾在打包時崩潰，因此執行 Vite 前會檢查版本並提示更新。PowerShell 若擋住 npm.ps1，可用 npm.cmd。
- 固定 Vue 3.5.22、Vite 7.3.8、@vitejs/plugin-vue 6.0.11。透過 overrides 使用隨附官方 @rollup/wasm-node 4.68.8 tarball，作為本課實測的打包配置；保留 vendor、package.json 與 lock。這不是對所有平台的相容保證，也不代表最新版本。
- 在副本執行 npm ci --ignore-scripts --audit=false --fund=false，再執行 npm test、npm run dev。首次安裝通常需要網路與可驗證的 TLS；本課不提供完整離線套件包，也不要關閉 TLS 驗證。
- 主教材可離線閱讀。隨附 dist 是實際建置結果；只想觀察時可在副本執行 node serve-dist.js，無須安裝依賴。要修改並重新編譯 .vue，仍須完成 npm ci。所有服務只綁定 127.0.0.1，按 Ctrl+C 停止。

[隨附建置頁面](../examples/vue-sfc/dist/index.html)；模組互動需先在範例副本依課程啟動 dev 或 preview。

## 1. 先認識三個不同命令

先用 npm run 查看 scripts，再依序執行 test、dev。觀察終端機印出的本機網址；結束 dev 後執行 build，再啟動 preview。dev 預設 5173，preview 預設 4173。若已被使用，本課 strictPort 會報錯，可用 -- --port 其他埠。

**預期觀察：** dev 服務來源並提供開發更新功能；build 產生 dist 後結束；preview 讀 dist，不會替你重新建置。這三者不是後端 API，也不代表已部署上線。

```powershell
node --version
npm ci --ignore-scripts --audit=false --fund=false
npm test
npm run dev
# 結束 dev 後，或另開終端機：
npm run build
npm run preview
```

## 2. 讀懂 SFC 的三個區塊

開啟 src/components/SummaryPanel.vue。script setup 寫元件邏輯，template 描述畫面，style scoped 放該元件的樣式。再比較第 3A 的 components.js：這次不再把模板放進 JavaScript 字串。

**預期觀察：** 瀏覽器不能原生理解 .vue；官方 Vue 外掛會將它編譯。單檔元件將相關內容放在一起，仍須依責任拆成不同元件，並保留模型驗證。

```vue
<script setup>
defineProps({ title: { type: String, required: true }, counts: { type: Object, required: true } });
</script>

<template>
<section class="summary-panel" :aria-label="title">
    <h3>{{ title }}</h3><dl class="stats">
    <div><dt>總數</dt><dd class="total">{{ counts.total }}</dd></div>
    <div><dt>正常</dt><dd class="normal">{{ counts.normal }}</dd></div>
    <div><dt>異常</dt><dd class="abnormal">{{ counts.abnormal }}</dd></div>
    </dl></section>
</template>

<style scoped>
.summary-panel h3 { border-bottom: 2px solid #d5ddd3; padding-bottom: 8px; }
</style>
```

## 3. script setup 與編譯巨集

閱讀 InspectionForm.vue 的 import、ref 與 defineEmits，再看 InspectionRow.vue 的 defineProps。這些頂層變數與匯入的元件能直接用在模板，不必另外撰寫 setup 的 return。defineProps、defineEmits 是此語法的編譯巨集，不需從 vue 匯入。

**預期觀察：** JavaScript 邏輯中的 ref 仍使用 .value。Props／事件的資料流與第 3A 相同；換成 SFC 並未自動建立 TypeScript 檢查。模板中的欄位也仍需要執行期資料驗證。

```vue
<script setup>
import { ref } from 'vue';
import { validateEquipment } from '../model.js';
const emit = defineEmits(['add-record']);
const equipment = ref('');
const result = ref('正常');
const error = ref('');
function submit() {
  try {
    const name = validateEquipment(equipment.value);
    error.value = '';
    emit('add-record', { equipment: name, result: result.value });
    // emit 不是回傳父元件成功與否的函式；本課保留草稿，由使用者確認結果。
  } catch (e) { error.value = e.message; }
}
</script>
```

## 4. 從 HTML 追到 App.vue

依序追蹤根 index.html 的 src/main.js、createApp(App).mount、App.vue 的三個元件匯入，以及 model.js。dev 的 Network 會顯示經過轉換的元件模組；查看回應內容，不要只看網址仍有 .vue 就認為瀏覽器直接執行原始 SFC。

**預期觀察：** main.js 是入口，App.vue 管主清單，子元件各管自己的草稿。相對 .vue 匯入交給工具處理；Vite 不會替你設計需求、補上後端或驗證資料契約。

```javascript
import { createApp } from 'vue';
import App from './App.vue';
import './style.css';
createApp(App).mount('#app');
```

## 5. 修改來源，觀察開發更新

只在副本將 App.vue 的 SFC 原始版改成 SFC 修改版，儲存後觀察 dev 頁面。再把 SummaryPanel.vue 的 scoped 邊框改色。嘗試在 InspectionForm.vue 刻意留下不完整的 script 語法，閱讀終端機或開發錯誤提示，修好再繼續。

**預期觀察：** dev 可在儲存後更新；更新方式可能影響元件狀態，不要假設未儲存草稿永遠保留。語法錯誤應被編譯流程指出，不能因模型測試仍通過就宣稱 SFC 沒問題。

## 6. scoped 是樣式範圍，不是安全邊界

在 devtools 比較 SummaryPanel 的 DOM 屬性與樣式選擇器。編譯器為 scoped 樣式加入對應的範圍屬性。全域 style.css 仍可影響元件；父元件的 scoped 樣式也可能影響子元件根節點。

**預期觀察：** scoped 不等於 Shadow DOM、資料隔離或權限控管。它協助管理樣式選擇器，不能保護機密，也不取代模板插值、資料驗證或後端授權。

## 7. 建置後再預覽，分辨來源與產物

執行 npm run build，檢查 dist/index.html 與 assets 的 JavaScript、CSS。啟動 preview，確認目前文字。接著只修改 src/App.vue，重新整理 preview；最後成功 build 再整理。不要手動修改 dist，下一次建置會重新產生它。

**預期觀察：** 未重新 build 時，preview 保持舊文字；成功建置後才看到新文字。資產檔名的雜湊可能改變，不應硬記檔名。錯誤建置可能留下舊或不完整的 dist，不能把舊畫面正常當作新來源通過；本課不保證失敗時保留所有舊產物。

```javascript
import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';

export default defineConfig({
  plugins: [vue()],
  base: './',
  server: { host: '127.0.0.1', strictPort: true },
  preview: { host: '127.0.0.1', strictPort: true },
  build: { sourcemap: false }
});
```

## 8. 分開驗證模型、編譯與操作

執行 npm test，確認 10 個模型測試，再成功執行 build。在 dev 與 preview 各驗證新增異常、篩選、編輯、切換結果與刪除。把設備名稱輸入成像 HTML 的文字，確認只呈現文字。最後重新整理，確認還原三筆資料。

**預期觀察：** 模型測試不掛載 Vue；build 通過也不等於型別檢查、安全驗證或操作測試。preview 是本機檢視建置產物的工具，不是正式營運伺服器。此範例沒有資料庫、登入、Router 或持久保存。

```powershell
npm test
npm run build
npm run preview
# preview 後仍需實際驗證操作；不自動部署。
```

## 自己動手修改

### 練習一：讓修改進入產物

將 App.vue 的 SFC 原始版改成今天已重建。分別記錄 dev 更新、preview 重整，以及 build 後 preview 的文字。

**參考解答：** dev 在儲存後更新；只重整 preview 仍看舊產物；成功 build 再重整 preview 才顯示今天已重建。先修好任何 SFC 編譯錯誤，不靠手改 dist 達成結果。

### 練習二：沿用同一個 SFC

將 App.vue 第二個 SummaryPanel 的 title 改成篩選後統計，保留 :counts=visibleCounts。切到異常，記錄兩卡結果。

**參考解答：** 第一卡仍是全部資料 3／2／1，第二卡標題改變且為 1／0／1。這是重用同一個 SummaryPanel.vue 並傳入不同 Props；不必複製一個新元件或另存計數。

### 練習三：指出各項檢查的盲點

在副本的 InspectionForm.vue 留下 const broken = ;，先執行 npm test，再執行 build。記錄結果後還原並重新建置。

**參考解答：** 模型測試只匯入 model.js，仍可能全部通過；build 必須拒絕錯誤的 SFC 腳本。還原後 build 成功，再到 preview 驗證操作。不能把其中一項檢查的通過外推成所有層次都正確。

## 完成檢核

- [ ] 能從根 HTML 追到 main.js、App.vue、子元件與模型。
- [ ] 能說明 script setup、template、style scoped 與編譯巨集的角色。
- [ ] 能執行 ci、dev、test、build、preview，分辨每個命令讀取的內容。
- [ ] 能用文字修改與語法錯誤證明模型測試、編譯及瀏覽器操作的責任不同。
- [ ] 知道 dist 需成功重建，preview 不代表正式部署；進度不會自動勾選。

本課不自動修改主教材進度。Router、TypeScript 與較完整的管理流程將在後續練習。

## 來源與核對範圍

核對日期：2026-11-26。專案、資料規則與練習安排為本教材設計。

- [Vue：Single-File Components](https://vuejs.org/guide/scaling-up/sfc.html)：核對 SFC 與建置工具的關係。
- [Vue：script setup](https://vuejs.org/api/sfc-script-setup.html)：核對頂層可用項目與 defineProps／defineEmits 巨集。
- [Vue：SFC CSS Features](https://vuejs.org/api/sfc-css-features.html)：核對 scoped 樣式轉換與子元件根節點。
- [Vite 7：Getting Started](https://v7.vite.dev/guide/)：使用本課主要版本的文件，核對 Node 條件、入口與 scripts。
- [Vite：Building for Production](https://vite.dev/guide/build.html)：只參考來源到靜態輸出的共同概念；本課實際執行的是固定 Vite 7。
- [Rollup：Migrating to Rollup 4](https://rollupjs.org/migration/)：核對官方 @rollup/wasm-node 可作為原生套件的替代實作。
- [Vite v7.3.8](https://github.com/vitejs/vite/releases/tag/v7.3.8)：本次核對並實測的固定版。
- [Vue 外掛 6.0.11](https://github.com/vitejs/vite-plugin-vue/releases/tag/plugin-vue@6.0.11)：本次核對並實測的固定版。
