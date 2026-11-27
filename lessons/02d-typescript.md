# 第 2 階段 D｜TypeScript、編譯與執行期驗證

更新：2026-11-24

為共用巡檢模組加上資料型別，親手比較編譯前的錯誤與執行時的錯誤。延續第 2C 的 JSON 契約：型別描述程式內部的預期，外部資料仍須逐欄驗證。

## 準備

- 先完成第 2C，能使用 import、export、npm scripts，並讀懂 parseInspections 的驗證規則。本課練習不需要登入、資料庫或 API 金鑰。
- 把 examples/typescript-lab 整個資料夾（包含 vendor、tools、src、dist 與鎖定檔）複製到自己的練習位置，在副本開啟終端機。不要直接修改教材原版。
- 需 Node.js 20 以上與 npm；本次實測 Node.js 24.12.0、npm 11.6.2、TypeScript 6.0.3，沒有逐版測試所有 Node.js 版本。PowerShell 若擋住 npm.ps1，可改用 npm.cmd，無須調整全域執行政策。
- 本課固定使用隨附的 TypeScript 6.0.3 編譯器 API 與標準宣告檔。vendor/typescript 是從本機 VS Code 隨附套件複製的離線子集，含授權、來源與檔案雜湊；不是完整官方 CLI 套件。tools/compiler.cjs 是教材的小型驅動程式，真正呼叫 createProgram、型別診斷與 emit。無須安裝全域 tsc。
- 在副本先執行 npm ci --ignore-scripts --offline --audit=false --fund=false；它只連結隨附的 file:vendor/typescript，不連外下載。保留完整副本與鎖定檔；不要執行 npm install typescript@latest 來取代本課固定環境。

[範例頁面](../examples/typescript-lab/index.html)；互動需 HTTP；編輯來源後先成功 build，再執行 npm run serve。

## 1. 先檢查，再執行

依序執行版本、check、build、demo。check 加上 noEmit，只檢查 src 內的正常 TypeScript 檔；build 檢查後產生 dist。cli.js 與測試是普通 JavaScript，本課未啟用 checkJs，不能宣稱每個檔案都經過型別檢查。

**預期觀察：** 編譯器版本為 6.0.3；check 不改 dist；build 成功後 demo 顯示 total: 3、normal: 2、abnormal: 1。Node.js 能直接移除部分 TypeScript 語法，不代表做過型別檢查。本課明確呼叫真正的編譯器。

```powershell
npm run compiler:version
npm run check
npm run build
npm run demo
```

## 2. 用型別描述一筆巡檢資料

閱讀 src/inspection.ts。string、number 表示值的種類；interface 描述物件欄位；InspectionResult 是只允許正常或異常的字串聯集。Backup 的 version: 1 是數字字面值型別，不是任意 number。先用自己的話解釋每一個欄位，再嘗試增加一筆合法資料到 src/examples.ts。

**預期觀察：** 少了 equipment、寫錯欄位名或把 result 寫成未知，編譯器能指出程式碼中的不一致。型別不是資料庫欄位，也不會自動產生輸入表單或把數字轉成字串。

```typescript
export type InspectionResult = '正常' | '異常';
export interface Inspection {
  id: string;
  equipment: string;
  result: InspectionResult;
}
export interface Backup { version: 1; rows: Inspection[]; }
export interface Summary { total: number; normal: number; abnormal: number; }
```

## 3. 親手讓型別檢查失敗

執行 npm run check:errors，閱讀 src/type-errors.ts 的四個錯誤。此命令預期非零退出；它使用獨立 tsconfig.errors.json，因此不阻擋原版 build。將錯誤檔的內容逐一改正再重跑；不要藉由 any、as 或關閉 strict 讓紅字消失。

**預期觀察：** 原版出現四個診斷：未知結果、數字設備名稱、字串統計總數、equpment 拼字錯誤。全部修正後，check:errors 才成功。這份設定 noEmit: true，練習檔不應產生任何 JavaScript。

```typescript
// 本檔刻意有錯，僅供 npm run check:errors；正常建置排除此檔。
import type { Inspection, Summary } from './inspection.js';

const wrongResult: Inspection = { id: 'a', equipment: 'A01', result: '未知' };
const wrongName: Inspection = { id: 'b', equipment: 42, result: '正常' };
const wrongSummary: Summary = { total: '3', normal: 2, abnormal: 1 };
const typo = wrongResult.equpment;
console.log(wrongName, wrongSummary, typo);
```

## 4. 從 unknown 縮小到可以使用的資料

JSON.parse 的結果先存成 unknown。unknown 要求我們先證明值符合條件，才能讀取欄位。依序追蹤 isRecord、版本與陣列檢查、每筆欄位檢查；typeof、null 與陣列判斷都是執行期 JavaScript。完整通過後才回傳重新建立的 Inspection[]。

**預期觀察：** isRecord 的 value is Record<string, unknown> 是型別守衛，背後仍需正確的判斷式。不要把守衛當魔法：錯誤的判斷式一樣會誤導編譯器。外部資料與未經型別檢查的 JS 呼叫，都需要這些實際檢查。

```typescript
function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

// 型別描述內部資料；這些 if 才是外部資料的執行期檢查。
export function parseInspections(text: string): Inspection[] {
  if (typeof text !== 'string') throw new Error('輸入須為 JSON 字串');
  if (new TextEncoder().encode(text).length > 128 * 1024) throw new Error('JSON 超過 128 KiB');
  let value: unknown;
  try { value = JSON.parse(text); }
  catch { throw new Error('JSON 語法錯誤'); }
  if (!isRecord(value) || value.version !== 1 || !Array.isArray(value.rows) || value.rows.length > 200) {
    throw new Error('需要 version: 1 與最多 200 筆的 rows 陣列');
  }
```

## 5. 看見 as 斷言沒有驗證資料

執行 npm run demo:assertion，再在網頁按「比較斷言與執行期驗證」。固定輸入把 equipment 設為 42、result 設為未知。as Backup 只是告訴編譯器採用這個型別；它沒有呼叫驗證器，也不會轉換資料。此示範刻意保留斷言，讓你比較兩層結果。

**預期觀察：** 這段程式可以通過 check，但 observedType 是 number，accepted 是 false。執行期驗證器拒絕整份資料。斷言示範不會覆寫目前有效清單。不要把 JSON.parse(text) as Backup 當成匯入驗證。

```typescript
import { parseInspections } from './inspection.js';
import type { Backup } from './inspection.js';

export interface AssertionReport { observedType: string; accepted: boolean; message: string; }

export function demonstrateAssertion(): AssertionReport {
  const incoming: unknown = {
    version: 1,
    rows: [{ id: 'bad', equipment: 42, result: '未知' }]
  };
  // 刻意的錯誤做法：as 不會改變或驗證 incoming。
  const assumed = incoming as Backup;
  const observedType = typeof assumed.rows[0]?.equipment;
  let accepted = false;
  let message = '';
  try {
    parseInspections(JSON.stringify(incoming));
    accepted = true;
    message = '資料被接受';
  } catch (error) {
    message = error instanceof Error ? error.message : '未知錯誤';
  }
  return { observedType, accepted, message };
}
```

## 6. 比較 TypeScript 與真正產生的 JavaScript

成功 build 後，比較 src/inspection.ts 與 dist/inspection.js，搜尋 interface、InspectionResult 與 if。執行 npm run serve，開啟印出的 127.0.0.1 網址，再從 Network 找 dist/app.js、inspection.js、examples.js、assertion-demo.js。原始碼的相對匯入寫 .js，對應編譯後執行的檔名。

**預期觀察：** 介面、型別註記與斷言消失；if、throw、JSON.parse 保留。瀏覽器載入 dist 的 JavaScript，沒有在頁面內執行編譯器。直接雙擊 HTML 可讀說明，但模組互動需 HTTP。修改 src 後要重新 build 並重新整理。

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "lib": ["ES2022", "DOM"],
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "noEmitOnError": true,
    "rootDir": "src",
    "outDir": "dist"
  },
  "include": ["src/**/*.ts"],
  "exclude": ["src/type-errors.ts"]
}
```

## 7. 建置失敗時，留意舊輸出

只在自己的副本操作：先成功 build，記下畫面與 dist/examples.js。再把 src/examples.ts 的一個正常改成未知，執行 npm run build，預期失敗。觀察 dist 與瀏覽器仍可能保留舊結果。修正來源，再確認 build 成功與頁面更新。

**預期觀察：** 本課 noEmitOnError: true 阻止這次錯誤建置產生新輸出，並不刪除以前成功的 dist。舊畫面正常不能證明新程式已通過。正式流程應先檢查建置的退出結果，再決定是否測試或部署；此課沒有自動部署。

## 8. 用測試與瀏覽器驗證另一層責任

執行 npm test，它先 build，成功才測試 dist。12 個測試涵蓋契約、邊界、統計、斷言以及普通 JS 呼叫傳入錯誤型別。再到網頁把第二筆設備名稱改成數字，確認舊清單保留；嘗試空清單與正常資料。畫面只使用 textContent，沒有將輸入當 HTML 插入。

**預期觀察：** 原版 12 個測試通過；數字名稱在執行時遭拒，即使輸入只是瀏覽器裡的 JSON 文字。check 通過不能取代資料驗證或測試，測試通過也不代表安全與所有情境皆已證明。此範例不讀寫 localStorage。

```powershell
npm test
# 只測既有 dist，不重新編譯：
npm run test:runtime
# 此命令不可當成最新 src 已通過檢查的證據。
```

## 自己動手修改

### 練習一：修好四個型別錯誤

在副本逐一修正 src/type-errors.ts；每修一個執行 check:errors，記錄錯誤數是否減少。

**參考解答：** wrongResult.result 改成正常或異常；wrongName.equipment 改成字串；wrongSummary.total 改成數字；equpment 改成 equipment。最後命令成功且不產生練習檔輸出。不要使用型別斷言掩蓋錯誤。

### 練習二：讓原始資料改變畫面

把 src/examples.ts 第一筆的 result 改成異常，重新 build、demo 並重新整理 HTTP 頁面，再還原。

**參考解答：** 第一筆原本正常，修改後總數仍為 3、正常 1、異常 2。只改 src 卻沒有 build，cli 與頁面仍讀到舊 dist。還原來源後再 build，應恢復 3／2／1。

### 練習三：寫下兩層拒絕的證據

比較 type-errors.ts 的 equipment: 42，與網頁 JSON 的 equipment: 42。記錄各自在何時被誰拒絕，以及 as Backup 為何沒有提供保護。

**參考解答：** 前者是有型別約束的來源程式，在 check 時被編譯器拒絕；後者是執行時讀到的文字，由 parseInspections 的 typeof 檢查拒絕。as 只影響編譯器的認知，輸出中不存在這個驗證動作。

## 完成檢核

- [ ] 能說明 interface、聯集與字面值型別，並修正四個刻意錯誤。
- [ ] 能執行離線 ci、check、build、demo 與 12 個測試，分辨預期失敗與意外失敗。
- [ ] 能指出 unknown 的縮小過程，以及真正保護外部 JSON 的執行期條件。
- [ ] 能用斷言示範證明 as 不做資料轉換或驗證。
- [ ] 能說明瀏覽器讀 dist，以及錯誤建置可能留下舊輸出的原因。

本課不自動修改主教材進度。型別檢查、測試與執行期驗證各有責任；完成本課後再評估前端框架。

## 來源與核對範圍

核對日期：2026-11-24。專案、資料規則與練習安排為本教材設計。

- [TypeScript：Everyday Types](https://www.typescriptlang.org/docs/handbook/2/everyday-types.html)：核對物件、聯集、字面值與型別斷言的用途。
- [TypeScript：Narrowing](https://www.typescriptlang.org/docs/handbook/2/narrowing.html)：核對 typeof、控制流程與型別守衛。
- [TypeScript：noEmitOnError](https://www.typescriptlang.org/tsconfig/noEmitOnError.html)：核對錯誤時阻止輸出；本課明確啟用此選項。
- [TypeScript：Compiler API](https://github.com/microsoft/TypeScript/wiki/Using-the-Compiler-API)：核對本課 6.0 編譯器的 Program、診斷與 emit 流程；此 API 範例適用 6.0 與更早版本，不外推到新版編譯器。
- [Node.js：Modules — TypeScript](https://nodejs.org/api/typescript.html)：核對內建型別移除不執行型別檢查，避免把執行成功當成 check 通過。
