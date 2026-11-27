# 第 3 階段 A｜Vue 元件、Props 與狀態

更新：2026-11-25

把巡檢畫面拆成新增表單、巡檢列與統計元件，親手追蹤草稿、主清單、Props 與事件。這一課選 Vue 示範元件觀念；不需要同時學 React，也不必立刻導入完整專案工具鏈。

## 準備

- 先完成第 1 階段及第 2C，能說明表單、陣列、函式與模組。第 2D 可協助理解型別與資料驗證；本課使用普通 JavaScript，沒有假裝它已受 TypeScript 檢查。
- 完整複製 examples/vue-components 到自己的練習位置。在副本執行 npm run serve，開啟印出的 127.0.0.1 網址；按 Ctrl+C 結束。需 Node.js 20 以上，本次實測 Node.js 24.12.0／npm 11.6.2。
- 本課免建置、無須 npm install。Vue 3.5.22 開發版已隨附於 vendor，來源、授權與 SHA-256 紀錄一併保留；開啟範例不會連 CDN。固定版本供本課重現，沒有宣稱是最新版本或正式營運設定。
- 一般教材 HTML 可離線閱讀；互動範例使用 ES 模組，需本機 HTTP。重新整理會還原三筆虛構資料；本課不讀寫 localStorage、不連 API，也沒有資料庫。
- 只專注元件、狀態與資料流。此免建置寫法使用 setup 與 template 字串，不是 .vue SFC 或 script setup；SFC、Router、TypeScript 整合與打包工具將另安排。

[範例頁面](../examples/vue-components/index.html)；模組互動需先在範例副本執行 npm run serve。

## 1. 從原生 DOM 走到宣告式畫面

啟動範例，先比較第 1 階段的 form.js 與本課 app.js。以前先修改陣列，再手動建立 li；現在修改 rows，讓 Vue 依模板更新畫面。兩者仍使用 HTML、CSS、JavaScript；框架協助組織畫面與狀態，沒有取代資料規則。

**預期觀察：** 預設三筆資料，正常 2、異常 1。修改 JS 後重新整理即可，沒有 build 命令。Network 可見本機 vendor/vue.global.js、app.js、components.js、model.js、inspection.js；Vue.version 為 3.5.22。

```powershell
npm test
npm run serve
# 不需 npm install 或 build；從印出的 HTTP 網址開啟。
```

## 2. 畫出元件樹與資料擁有者

父元件管理主清單、顯示條件與順序；InspectionForm 管自己的設備名稱與結果草稿；每個 InspectionRow 管自己的編輯草稿；SummaryPanel 只接收數字並顯示。先在新增欄位輸入文字，但不要送出，觀察統計。

**預期觀察：** 輸入草稿不會新增主清單。兩個 SummaryPanel 是同一個元件的兩個實例，分別接收全部資料與目前顯示的統計。元件不是單純把 HTML 分成檔案，還要確定誰擁有狀態。

```text
App（主清單、篩選、順序）
├─ InspectionForm（新增草稿）
├─ SummaryPanel × 2（接收不同統計）
└─ InspectionRow × N（每列自己的編輯草稿）
```

## 3. 用 ref 管理狀態，用 computed 推導結果

閱讀 rows、filter、reversed 與 visible、allCounts、visibleCounts。setup 的 JavaScript 讀寫 ref 要用 .value；模板中的頂層 ref 在本課寫法會自動解開。computed 從狀態計算結果，不另存一份需要手動同步的統計。

**預期觀察：** 切到異常時，全部資料仍為 3／2／1，目前顯示變成 1／0／1。篩選沒有刪除資料。不要直接改 visible 或手動改統計卡的 DOM，應修改其來源狀態。

```javascript
const rows = ref(initialRecords());
    const filter = ref('全部');
    const reversed = ref(false);
    const message = ref('已載入三筆虛構資料；重新整理會還原。');
    const flow = ref('等待操作：子元件事件 → 父元件驗證與更新 → Props／衍生統計');
    let nextId = 4;
    const visible = computed(() => visibleRecords(rows.value, filter.value, reversed.value));
    const allCounts = computed(() => summarize(rows.value));
    const visibleCounts = computed(() => summarize(visible.value));
```

## 4. Props 向下傳，子元件負責呈現

找出 :counts 與 :row。冒號讓 Vue 把 JavaScript 值傳入；title=全部資料則是字串。SummaryPanel 不改 counts，InspectionRow 不直接改 row.equipment。Object 類型的 props 宣告不會驗證每個欄位，也不是 JSON 契約檢查。

**預期觀察：** 父元件更新後，子元件收到新的 props。Props 是單向資料流；物件的巢狀欄位仍可能被不當修改，並非深層自動鎖定。以自己的草稿編輯，再發出事件請父元件更新，較容易追蹤。

```javascript
export const SummaryPanel = {
  props: { title: { type: String, required: true }, counts: { type: Object, required: true } },
  template: `<section class="summary-panel" :aria-label="title">
    <h3>{{ title }}</h3><dl class="stats">
    <div><dt>總數</dt><dd class="total">{{ counts.total }}</dd></div>
    <div><dt>正常</dt><dd class="normal">{{ counts.normal }}</dd></div>
    <div><dt>異常</dt><dd class="abnormal">{{ counts.abnormal }}</dd></div>
    </dl></section>`
};
```

## 5. 事件向上送，父元件驗證再更新

新增一筆異常設備，並查看最近一次資料流。從 InspectionForm 的 emit 追到父元件 add，再到 model.js 的 addRecord。接著按一列的改為正常或改為異常，追蹤 change-result。子元件沒有自行寫入父元件陣列。

**預期觀察：** 新增異常後，全部統計變成 4／2／2。emit 不是回傳成功結果的函式，本課新增後保留草稿，請先確認訊息；再次送出會再新增一筆。元件事件需由直接父元件監聽，不像原生 DOM 事件一路冒泡。

```javascript
export const InspectionForm = {
  emits: ['add-record'],
  setup(_props, { emit }) {
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
    return { equipment, result, error, submit };
  },
  // 省略下方模板；完整程式見 components.js
};
```

## 6. 編輯草稿與穩定 key

切回全部，編輯 r-1 的名稱但先不儲存；按反轉顯示順序。確認草稿仍附在相同識別碼。取消再編輯並儲存，觀察名稱改變、統計不變。父元件以 row.id 作 key，編輯只更新欄位而保留 id。

**預期觀察：** 反轉順序不應把草稿移到另一筆資料。不要用陣列索引當作這種可重排清單的 key。若篩選把該列排除，元件會卸載，未儲存的局部草稿會消失；key 不提供跨卸載的草稿保存。

```html
<inspection-row v-for="row in visible" :key="row.id" :row="row"
  @rename-record="rename" @change-result="toggle"
  @remove-record="remove"></inspection-row>
```

## 7. 框架不取代驗證與安全呈現

只輸入空白再新增，確認失敗且清單不變；編輯名稱成空白也應保留原名稱。再輸入像 HTML 的設備名稱，觀察它只顯示文字。本課使用模板插值，不使用 v-html；也不把使用者內容拼成 template。父元件在事件邊界仍經過模型驗證。

**預期觀察：** 模板插值可避免把名稱當 HTML 插入，卻不代表整個系統已安全。Vue 的 props 檢查、HTML maxlength 與前端驗證都不能取代後端授權及資料驗證。這個本機練習沒有登入、外部 API 或後端。

```javascript
export function validateEquipment(value) {
  if (typeof value !== 'string' || !value.trim() || value.trim().length > 80) {
    throw new Error('設備名稱需為 1–80 字，不能只有空白');
  }
  return value.trim();
}
export function addRecord(rows, draft, id) {
  if (!draft || typeof draft !== 'object') throw new Error('新增內容不是資料物件');
  return validate([...rows, { id, equipment: validateEquipment(draft.equipment), result: draft.result }]);
}
```

## 8. 測試資料規則，再驗證元件協作

執行 npm test，檢查模型的 10 個行為測試。這些測試不會掛載 Vue，必須再實際驗證新增、篩選、編輯、切換結果、取消刪除與確認刪除。試著在異常篩選下把唯一異常改為正常，再查看全部統計。

**預期觀察：** 唯一異常變正常後，目前顯示空狀態，全部仍有 3 筆且正常 3、異常 0。Node 測試通過不能證明元件已正確接線；本課另外用實際瀏覽器驗證。重新整理後回到三筆原始資料，沒有自動保存。

```powershell
npm test
# 10 個模型測試；另需在瀏覽器驗證元件操作與接線。
```

## 自己動手修改

### 練習一：區分 Props 與本地草稿

把 index.html 第一個統計元件的 title 改為主清單統計。再輸入新設備但不送出，預測哪些畫面應改變。

**參考解答：** 只改第一個 SummaryPanel 的標題；第二個仍為目前顯示。新增表單的輸入草稿變動，主清單與兩組統計保持原值。title 是父元件傳入的顯示資料，equipment 草稿由表單實例擁有。

### 練習二：用操作證明 key 的用途

在全部條件編輯 r-1，將草稿改成尚未儲存，反轉兩次順序並記錄。接著改成只顯示異常，再回全部，觀察差異。

**參考解答：** 反轉時相同 row.id 的元件實例被保留，草稿仍屬於 r-1。改成異常時 r-1 被卸載；回全部會建立新實例，未儲存草稿消失。若需要跨篩選保留草稿，應另外設計由父元件以 id 管理草稿，而非假設 key 自動保存。

### 練習三：再加一份衍生統計

在 app.js 新增 abnormalCounts，使用 computed、visibleRecords 與 summarize 取得全部異常的統計，加入 setup 的 return；在 index.html 再放一個 SummaryPanel。

**參考解答：** 在 setup 內加入下方 computed，並把 abnormalCounts 加入既有 return（保留其他欄位）。模板加入下方第三個 SummaryPanel。原版此卡為 1／0／1；切到正常篩選仍應是 1／0／1；把 r-2 改正常才變成 0／0／0。這個值依主清單推導，無須再手動同步一份計數。

```javascript
const abnormalCounts = computed(() =>
  summarize(visibleRecords(rows.value, '異常', false))
);
// 在 setup 的既有 return 物件加入 abnormalCounts，保留其他欄位。
```

```html
<summary-panel title="全部異常" :counts="abnormalCounts"></summary-panel>
```

## 完成檢核

- [ ] 能畫出父元件與三種子元件，指出主清單、篩選與局部草稿的擁有者。
- [ ] 能區分 ref 狀態與 computed 衍生值，說明兩個統計元件為何不同。
- [ ] 能從 props、emit、父元件處理函式一路追到模型驗證與更新。
- [ ] 能以反轉與篩選實測 key 與元件卸載對草稿的不同影響。
- [ ] 能完成新增、篩選、編輯、切換結果、刪除與失敗驗證；知道重新整理不保存。

本課不自動修改主教材進度。SFC、Router 與工具鏈將在後續課程練習。

## 來源與核對範圍

核對日期：2026-11-25。專案、資料規則與練習安排為本教材設計。

- [Vue：Quick Start](https://vuejs.org/guide/quick-start.html)：核對 global build、免建置與本機保存發行檔的方式。
- [Vue：Components Basics](https://vuejs.org/guide/essentials/component-basics.html)：核對普通 JS 元件、setup、props 與事件的入門結構。
- [Vue：Reactivity Fundamentals](https://vuejs.org/guide/essentials/reactivity-fundamentals.html)：核對 ref 與本課模板中的解開方式。
- [Vue：Computed Properties](https://vuejs.org/guide/essentials/computed.html)：核對從狀態推導數值的 computed 用法。
- [Vue：Props](https://vuejs.org/guide/components/props.html)：核對單向資料流與物件 props 的巢狀修改限制。
- [Vue：Component Events](https://vuejs.org/guide/components/events.html)：核對事件資料與元件事件不冒泡的特性。
- [Vue：List Rendering](https://vuejs.org/guide/essentials/list.html)：核對可重排元件清單使用穩定 key 的目的。
- [Vue：Security](https://vuejs.org/guide/best-practices/security.html)：核對文字插值、HTML 與不可信模板的界線。
- [Vue Core：v3.5.22](https://github.com/vuejs/core/releases/tag/v3.5.22)：核對本課固定版本；本課未宣稱它是最新發行版。
