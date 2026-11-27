# 第 1 階段實作｜從巡檢表單到 JavaScript 互動

更新：2026-11-19

同一張表單做三次：先寫出內容，再調整版面，最後接上資料與事件。以三個可直接開啟的版本對照，練習先預測、再修改、再驗收。

## 準備

- 先完成第 0 階段的建立 HTML 與重新整理操作。
- 將 examples/form-dom 整個資料夾複製到自己的練習位置，保留 HTML、CSS 與 JavaScript 的相對位置；頂端回教材的連結只在完整教材目錄中有效。
- 用編輯器閱讀與修改；瀏覽器可直接以 file: 開啟。練習不需套件或伺服器。全部使用虛構資料。

## 直接開啟版本對照

- [01 · 靜態 HTML](../examples/form-dom/01-static.html)
- [02 · 加入 CSS](../examples/form-dom/02-styled.html)
- [03 · JavaScript 互動](../examples/form-dom/03-interactive.html)
- [04 · 備註練習解答](../examples/form-dom/04-notes.html)

01／02 版尚未接互動；03／04 版只有當頁記憶體，重新整理會清空。所有程式碼可在對應檔案閱讀。下方片段需放回相應位置，並非每一段都可獨立執行。

## 1. 從靜態 HTML 辨認責任

開啟 01-static.html，找到 form、label、input、select、button 與 ul。用編輯器把設備欄位的提示改成自己的虛構設備範例。此版的按鈕刻意使用 type=button，尚未加入新增邏輯；不要期待點擊後出現紀錄。在欄位按 Enter 仍可能觸發瀏覽器預設送出並重新載入；第 3 步會用 JavaScript 接手提交。

**預期觀察：** 文字與欄位可見，點擊『設備名稱』標籤會聚焦對應欄位。label 的 for 對應 input 的 id；placeholder 不能取代標籤。

```html
      <form id="inspection-form">
        <label for="equipment">設備名稱（1–80 字元）</label>
        <input id="equipment" name="equipment" required maxlength="80"
               placeholder="例如：A01 月台照明">
        <label for="result">巡檢結果</label>
        <select id="result" name="result">
          <option value="正常">正常</option>
          <option value="異常">異常</option>
        </select>
        <button type="button">新增紀錄</button>
      </form>
```

## 2. 一次只調一種 CSS 間距

開啟 02-styled.html，與靜態版比較。兩者的表單內容相同，第二版多載入 form.css。先將 .card 的 padding 改小，再改 margin，每次儲存與重新整理。在開發者工具的 Computed 盒模型中比較兩者。

**預期觀察：** padding 改變卡片內容與邊框的距離；margin 改變卡片外側間距。box-sizing: border-box 讓設定寬度包含內距與邊框，並不包含 margin。將視窗縮到約 390px，欄位仍應完整顯示。

```css
* { box-sizing: border-box; }
.card { margin: 24px 0; padding: 24px; border: 1px solid #d5ddd3; }
```

## 3. 讓互動程式找得到元素

開啟 03-interactive.html，確認末尾的 script 載入 form.js，新增按鈕改為 type=submit。先閱讀 JavaScript 最上方的 getElementById，對照 HTML 的 id。將設備名稱打成 A01，再按新增。

**預期觀察：** 列表顯示一筆紀錄，頁面不導向另一個網址。submit 事件加上 preventDefault 由本程式處理提交；這不等於永久儲存。script 放在 body 末尾，讓前面的元素先建立。

```javascript
form.addEventListener('submit', event => {
  event.preventDefault();
  // 接著讀取輸入、驗證、更新陣列與 render。
});
```

## 4. 分清原生檢查與應用規則

先提交空字串，觀察瀏覽器的 required 檢查；再填三個空白提交，觀察 JavaScript 的 trim 與錯誤訊息。最後輸入頭尾有空白的設備名稱並提交。

**預期觀察：** 空字串會先被瀏覽器原生驗證擋下，未觸發 submit 處理器；全空白會進入程式後被拒絕。合法名稱會移除頭尾空白再保存到陣列。未來有後端時，後端仍需重新驗證。

```javascript
  const equipment = equipmentInput.value.trim();
  const result = resultInput.value;
  if (!equipment || equipment.length > 80) {
    message.textContent = '設備名稱須為 1–80 字元，不能全是空白。';
    equipmentInput.focus();
    return;
  }
  if (!['正常', '異常'].includes(result)) {
    message.textContent = '請選擇正常或異常。';
    resultInput.focus();
    return;
  }
```

## 5. 從資料重畫列表

新增三筆虛構紀錄，其中一筆選異常。閱讀 rows.push 與 render：前者修改陣列，後者先清空列表，再用迴圈把資料顯示出來。在設備名稱輸入 <b>A02</b> 並提交，觀察文字。

**預期觀察：** 列表會顯示 <b>A02</b> 原文字，而不是建立粗體標籤。textContent 將輸入當文字；不要將其改成以 innerHTML 拼接使用者輸入。重新整理後清單回到零筆，因為 rows 只在記憶體。

```javascript
function render() {
  const visible = rows.filter(row =>
    filter.value === 'all' || row.result === filter.value
  );
  list.replaceChildren();
  count.textContent = `顯示 ${visible.length} / 共 ${rows.length} 筆紀錄`;
  if (visible.length === 0) {
    const empty = document.createElement('li');
    empty.textContent = rows.length === 0
      ? '尚無紀錄，先新增一筆。'
      : '沒有符合篩選條件的紀錄。';
    list.append(empty);
  }
  for (const row of visible) {
    const item = document.createElement('li');
    item.textContent = `${row.equipment} · ${row.result}`;
    list.append(item);
  }
}
```

## 6. 篩選只改變呈現

新增一筆正常與一筆異常，切換全部、只看異常、只看正常。停在只看異常時，再新增一筆正常。比較顯示筆數與總筆數，接著切回全部。

**預期觀察：** 篩選從 rows 推導 visible，不刪除原陣列。新紀錄可能被目前條件隱藏，訊息會提醒；切回全部仍能看見。按 Enter 提交表單與按新增應觸發相同規則。

```javascript
const visible = rows.filter(row =>
  filter.value === 'all' || row.result === filter.value
);
// change 事件只要求重新呈現，不刪除 rows。
filter.addEventListener('change', render);
```

## 7. 完成自己的修改與驗收

先完成下方三個練習。不要直接抄解答：先記錄預期行為，再修改自己的副本。備註練習另提供 04-notes.html 與 form-notes.js 作完整對照。

**預期觀察：** 修改後正常案例與失敗案例都能說明；新增欄位要同時連接輸入、資料物件與輸出，不只是在畫面多放一個欄位。

## 8. 用 Git 留下可回看的小改動

若已安裝 Git，在自己的練習副本中執行下方流程。先記錄原始版本，再修改並查看差異。不要在本教材原始目錄初始化，也不要在本次練習上傳遠端。

**預期觀察：** 第一次提交前用 git diff --cached 檢查暫存內容；之後的修改可用 git diff 看到。commit 建立本機版本，不會自動上傳。若提示缺少作者名稱與電子郵件，依 Git 提示設定自己的資料。

```powershell
git init
git status
git add 01-static.html 02-styled.html 03-interactive.html form.css form.js
git diff --cached
git commit -m "建立巡檢表單練習原版"
# 完成一次小修改後
git diff
git status
```

## 自己動手修改

### A. 加入可選的備註欄位

在自己的 03 版加入 note 文字區域，允許空白、最多 120 字元。新增後顯示備註；正常與異常篩選仍可使用。先用空備註、一般備註及 <b>待查</b> 測試。

**參考解答：** HTML 加入有標籤的 textarea（id=note、maxlength=120），JavaScript 取得 noteInput，提交時 trim 後檢查長度，再放入 rows 的物件。render 用 textContent 拼入備註，空備註不顯示額外字樣。可對照 04-notes.html 與 form-notes.js；此版同樣只有記憶體資料。

```text
<label for="note">備註（可留白，最多 120 字元）</label>
        <textarea id="note" name="note" maxlength="120" rows="3"></textarea>

// 取得欄位
const noteInput = document.getElementById('note');

// 提交時，取代原本 rows.push 那一行
  const note = noteInput.value.trim();
  if (note.length > 120) {
    message.textContent = '備註最多 120 字元。';
    noteInput.focus();
    return;
  }
  rows.push({ equipment, result, note });

// render 迴圈中，取代原本 item.textContent 那一行
    const noteText = row.note ? ` · 備註：${row.note}` : '';
    item.textContent = `${row.equipment} · ${row.result}${noteText}`;
```

### B. 將設備名稱限制改成 20

將自己的副本改成最多 20 字元。找出哪些地方應一起調整，並測試 20 個 A 與 21 個 A。

**參考解答：** 至少同步修改 HTML 的 maxlength、欄位標籤、JavaScript 長度檢查與錯誤訊息。20 字元應成功，21 字元應拒絕或在使用者輸入時受到原生限制。測試程式直接設定 value 時，仍要靠 JavaScript 驗證長度。原教材參考版維持 80 字元。

```text
HTML：maxlength="20"，標籤顯示 1–20 字元
JavaScript：equipment.length > 20
錯誤訊息：設備名稱須為 1–20 字元，不能全是空白。
```

### C. 為什麼資料沒有不見？又為什麼不見了？

填入三筆資料，篩選到一筆，再切回全部，最後重新整理。用陣列、衍生資料與 DOM 三個詞說明觀察結果。

**參考解答：** 篩選只建立 visible 這份衍生結果，rows 原始陣列沒有被刪除，所以切回全部可再看見三筆。重新整理會建立全新的頁面與空 rows，因此資料才消失。把畫面寫出來不是保存到檔案；資料持久化留到第 2 階段。

## 完成檢核

- [ ] 能指出 HTML、CSS、JavaScript 分別負責什麼。
- [ ] label 與欄位正確對應，可用 Tab、Shift+Tab 與 Enter 操作。
- [ ] 空白名稱被拒絕，頭尾空白被移除，正常與異常都能新增。
- [ ] 篩選不會改變總筆數；空結果有明確訊息。
- [ ] 使用者輸入以文字顯示，重新整理會清空記憶體紀錄。
- [ ] 完成至少一項修改，並記下成功與失敗案例；如使用 Git，有檢查差異後的本機提交。

本課不自動修改主教材進度；完成實作後再回主教材第 1 階段勾選原有驗收。

## 排除卡點

### 按鈕完全沒有作用

先確認開的是 03 版；01／02 版尚未接事件。檢查 form.js 是否在同一資料夾、script 檔名是否一致，以及 Console 是否有找不到元素的錯誤。

### 新增後頁面重新載入

確認 script 已載入、按鈕為 submit、submit 處理器內有 event.preventDefault()，並先查看 Console 的錯誤。

### 輸入後看不到新增項目

先看總筆數與訊息，再切回全部。新增正常紀錄時若停在只看異常，這筆資料仍在原陣列。

### CSS 看起來沒有載入

確認 form.css 與 HTML 在同一資料夾，link 的 href 正確，且已儲存修改。01 靜態版刻意不載入 CSS。

### 按新增後沒有自訂空字串訊息

空字串會先被 required 的原生驗證阻止，所以 submit 處理器尚未執行。全空白則可用來觀察 trim 的自訂驗證。

## 來源與範圍

核對日期：2026-11-19。版本安排、練習與解答是本教材的教學設計。

- [MDN：Your first form](https://developer.mozilla.org/en-US/docs/Learn_web_development/Extensions/Forms/Your_first_form)：核對表單結構、標籤與欄位。
- [MDN：The box model](https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Styling_basics/Box_model)：核對內距、邊框、外距與 border-box。
- [MDN：submit event](https://developer.mozilla.org/en-US/docs/Web/API/HTMLFormElement/submit_event)：核對提交事件、原生驗證與阻止預設行為。
- [MDN：textContent](https://developer.mozilla.org/en-US/docs/Web/API/Node/textContent)：核對以文字呈現輸入與 innerHTML 的差別。
- [Git 官方 gittutorial](https://git-scm.com/docs/gittutorial)：核對 status、add、diff 與 commit 的本機基本流程。
