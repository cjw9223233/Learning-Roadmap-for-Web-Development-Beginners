# 第 2 階段 A｜JSON、保存與備份

更新：2026-11-20

把昨天的當頁陣列接到保存與備份。你會先比較物件與 JSON 字串，再練習保存、取回、匯出及驗證匯入。本課完成第 2 階段的資料保存部分；Fetch、npm 與 TypeScript 會另以後續練習深化。

## 準備

- 先完成第 1 階段表單與 DOM；能說明為什麼記憶體資料在重新整理後消失。
- 開啟 examples/json-storage/index.html；可直接以 file: 使用互動與檔案備份。瀏覽器可能限制這類網址的 localStorage，無法保存時請先匯出備份。
- 如要複製練習，請一併保留完整教材目錄，或自行修正 stylesheet 與回教材連結。本課的 HTML、CSS、JS 是直接維護的範例來源，不會由建置程式重新產生。
- 本練習使用獨立保存項目，不自動讀取或遷移舊巡檢資料。只使用虛構設備。

[開啟保存與備份練習](../examples/json-storage/index.html)

## 本課的備份格式

```json
{
  "version": 1,
  "rows": [
    {"id": "demo-1", "equipment": "A01 月台照明", "result": "正常"},
    {"id": "demo-2", "equipment": "A02 指示燈", "result": "異常"},
    {"id": "demo-3", "equipment": "B01 廣播設備", "result": "正常"}
  ]
}
```

版本、最多 200 筆、128 KiB 與欄位規則是本課練習的資料契約，不是瀏覽器通用規範。

## 1. 先觀察沒有保存的變更

開啟練習，新增 A01，觀察『記憶體』與『瀏覽器』兩個狀態。先不要按保存，直接重新整理。若先前已有保存版本，重新整理會回到那個版本。

**預期觀察：** 新增只改變當頁 rows；未保存的新資料不會因為畫面曾經顯示就自動留下。這與第 1 階段的記憶體表單相同。

## 2. 把資料表示成 JSON 字串

新增一筆後閱讀『目前記憶體的 JSON』。對照 version、rows、id、equipment、result。帶入目前 JSON 到文字區，刪掉一個引號，再按驗證，觀察語法錯誤。

**預期觀察：** JavaScript 物件與 JSON 字串不是同一種資料。stringify 產生字串，parse 讀回資料；JSON 不接受註解、單引號字串或尾隨逗號。解析成功仍需驗證欄位。

```javascript
const text = JSON.stringify({ version: 1, rows: [] });
const value = JSON.parse(text);
console.log(typeof text);  // string
console.log(value.rows);   // []
```

## 3. 保存、取消讀取與重新取回

新增 A01 並保存，再新增 A02 而不保存。按重新讀取，先取消，確認仍有兩筆；再次按並確認，觀察回到一筆。再重新整理確認保存版本。

**預期觀察：** setItem 寫入字串，getItem 取回字串，找不到項目時為 null。讀取前的確認避免誤捨棄尚未保存的記憶體變更。清除瀏覽器資料仍可能讓保存值消失。

```javascript
// 以下是流程片段，須配合完整程式的 try/catch
localStorage.setItem(storageKey, asJSON());
const raw = localStorage.getItem(storageKey);
const loaded = raw === null ? [] : parseBackup(raw);
```

## 4. 匯出備份，不必等保存成功

再新增一筆未保存的資料，按匯出記憶體 JSON 備份。確認電腦真的下載 storage-lab-backup.json，使用編輯器閱讀檔案，核對筆數。

**預期觀察：** 匯出的內容包含未保存的記憶體資料。下載檔案與瀏覽器保存是不同途徑；檔案需自行保管。本課的備份有 version 與 rows 包裝，與舊巡檢範例的純陣列不同。

## 5. 讀檔、驗證與套用是分開的

在讀取檔案欄位選取 samples/valid.json。先確認清單沒有改變，再按驗證並取代記憶體。先取消一次，然後再次按並確認。完成後查看保存狀態。

**預期觀察：** 讀檔只會填入待驗證文字區；全部資料驗證通過且使用者確認後，才取代記憶體。這時仍未保存到瀏覽器。再次選同一個檔案也能重新讀取。

```javascript
const text = await file.text();
// 讀取成功只填入文字區，不立刻取代 rows。
document.getElementById('json-input').value = text;
```

## 6. 有效 JSON 也可能是不合規資料

依序讀取 bad-json.json 與 bad-shape.json，再按驗證。第二個檔案可解析，但第二筆設備名稱全是空白。另試著將兩筆 id 改成相同值，觀察拒絕原因。

**預期觀察：** 語法、版本、陣列、欄位、筆數及唯一 ID 都要驗證。整份通過後才改狀態，所以不會先匯入第一筆、再因第二筆失敗而留下半套資料。無效內容不改變清單與保存值。

```javascript
function parseBackup(text) {
  if (new Blob([text]).size > maxBytes) throw new Error('JSON 超過 128 KiB');
  let value;
  try { value = JSON.parse(text); }
  catch { throw new Error('JSON 語法錯誤'); }
  if (!value || Array.isArray(value) || value.version !== 1 || !Array.isArray(value.rows)) {
    throw new Error('需要 version: 1 與 rows 陣列');
  }
  if (value.rows.length > maxRows) throw new Error('最多接受 200 筆紀錄');
  const ids = new Set();
  return value.rows.map((row, index) => {
    if (!row || Array.isArray(row) || typeof row.id !== 'string' || !/^[A-Za-z0-9_-]{1,64}$/.test(row.id) || ids.has(row.id)) {
      throw new Error(`第 ${index + 1} 筆 id 格式錯誤或重複`);
    }
    if (typeof row.equipment !== 'string' || !row.equipment.trim() || row.equipment.trim().length > 80 || !['正常', '異常'].includes(row.result)) {
      throw new Error(`第 ${index + 1} 筆設備名稱或巡檢結果不合規`);
    }
    ids.add(row.id);
    // 只取需要的欄位，建立新物件；不要讓匯入物件直接成為內部狀態。
    return { id: row.id, equipment: row.equipment.trim(), result: row.result };
  });
}
```

## 7. 觀察損壞保存值的處理

先匯出備份，再在此練習頁面的開發者工具 Console 執行下方指令，刻意將本練習的保存值改成壞掉的 JSON；重新整理。完成觀察後先複製原始內容留存，再按清除本練習資料並確認，接著匯入備份恢復。

**預期觀察：** 讀取失敗時保存按鈕會鎖定，原始值保留。仍可新增到記憶體並匯出。清除只移除此練習的 key，不使用 localStorage.clear()；主教材與舊巡檢保存值不受影響。

```javascript
// 先匯出本練習備份；只在本練習頁操作。
localStorage.setItem('web-storage-lab-v1', '{');
// 再用瀏覽器重新整理，觀察保存鎖定與原值保留。
```

## 8. 知道保存的失敗與範圍

閱讀保存的 try/catch。瀏覽器政策或配額可能拒絕存取；本課不要求以填滿儲存空間來製造失敗。請用自己的話寫出：保存失敗時資料在哪裡、如何備份、換瀏覽器是否還能讀取。

**預期觀察：** 寫入失敗時記憶體仍在，介面提示改用檔案備份。localStorage 依來源區隔，file: 行為可能因瀏覽器而異；它不是多人資料庫，也不應保存密碼或憑證。此範例尚未處理多分頁同時編輯。

```javascript
try {
  localStorage.setItem(storageKey, asJSON());
  // 只有成功後才將 dirty 設為 false。
} catch (error) {
  // 保留 rows，提示使用者改用 JSON 檔案備份。
  console.error(error.name);
}
```

## 自己動手驗證

### A. 辨認三種資料位置

建立一筆資料並保存，再新增第二筆但不保存，接著匯出備份。請先預測重新整理後的清單筆數，以及備份檔內的筆數，再實際驗證。

**參考解答：** 在沒有其他變更的情況下，重新整理回到一筆已保存紀錄，備份檔則含匯出當下的兩筆。頁面記憶體、瀏覽器保存與下載檔案有各自的更新時機。

### B. 做一份可被拒絕的備份

複製 valid.json，讓第二筆 id 與第一筆相同。匯入前記錄目前清單及保存筆數。驗證失敗後比較，然後修正 ID 再套用。

**參考解答：** 重複 ID 應在整份驗證時被拒絕，記憶體與保存版本都不改變。修正後確認套用只更新記憶體；仍需按保存才寫入 localStorage。

### C. 增加來源站別，先想資料契約

先在備份檔每筆加 station 欄位並匯入，觀察它是否留下。再列出真正支援此欄位時，要修改哪些位置；不必急著改完。

**參考解答：** 本課驗證器只重建 id、equipment、result 三個欄位，因此額外 station 不會留下。要支援新欄位，需要同步修改輸入、資料模型、驗證、呈現、匯出，以及版本與舊資料的遷移規則。直接在 JSON 多加一個鍵不代表應用程式已支援。

## 完成檢核

- [ ] 能分辨 JavaScript 物件、JSON 字串、瀏覽器保存值與備份檔。
- [ ] 可實際重現未保存變更在重新整理後消失，以及保存後可讀回。
- [ ] 完成一份備份檔，並驗證匯出的是目前記憶體資料。
- [ ] 讀檔不直接改清單；無效語法、空白欄位與重複 ID 都會被拒絕。
- [ ] 知道損壞保存值會被保留，能用備份恢復且不清除其他教材資料。
- [ ] 能說明 localStorage 的來源、配額、瀏覽器限制與多人共用的差別。

本課不自動勾選主教材驗收。Fetch 可接續[第 2 階段 B](02b-fetch.html)；npm 與 TypeScript 尚待後續練習。完成本課不代表整個第 2 階段已完成。

## 來源與範圍

核對日期：2026-11-20。操作順序、範例與資料契約為本教材設計。

- [MDN：Window.localStorage](https://developer.mozilla.org/en-US/docs/Web/API/Window/localStorage)：核對跨工作階段保存、來源區隔、存取例外與 file: 限制。
- [MDN：JSON.parse](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/JSON/parse)：核對解析與 JSON 語法錯誤。資料契約檢查為本課程式設計。
- [MDN：Storage.setItem](https://developer.mozilla.org/en-US/docs/Web/API/Storage/setItem)：核對字串保存與 QuotaExceededError。
- [MDN：Blob.text](https://developer.mozilla.org/en-US/docs/Web/API/Blob/text)：核對非同步讀取 UTF-8 文字；檔案選取與驗證流程由本課自行組合。
