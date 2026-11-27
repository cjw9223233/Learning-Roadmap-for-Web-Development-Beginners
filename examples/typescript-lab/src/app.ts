import { parseInspections, summarize } from './inspection.js';
import { sampleBackup } from './examples.js';
import { demonstrateAssertion } from './assertion-demo.js';

function element(id: string): HTMLElement {
  const found = document.getElementById(id);
  if (found === null) throw new Error(`找不到元素 ${id}`);
  return found;
}
function button(id: string): HTMLButtonElement {
  const found = element(id);
  if (!(found instanceof HTMLButtonElement)) throw new Error(`${id} 不是按鈕`);
  return found;
}
const foundInput = element('json-input');
if (!(foundInput instanceof HTMLTextAreaElement)) throw new Error('json-input 不是文字區');
const input: HTMLTextAreaElement = foundInput;

function apply(): void {
  try {
    const rows = parseInspections(input.value);
    const counts = summarize(rows);
    element('total').textContent = String(counts.total);
    element('normal').textContent = String(counts.normal);
    element('abnormal').textContent = String(counts.abnormal);
    const list = element('records'); list.replaceChildren();
    if (rows.length === 0) {
      const li = document.createElement('li'); li.textContent = '有效空清單。'; list.append(li);
    }
    for (const row of rows) {
      const li = document.createElement('li'); li.textContent = `${row.equipment} · ${row.result}`; list.append(li);
    }
    element('message').textContent = '執行期驗證通過，已更新統計。';
  } catch (error) {
    const message = error instanceof Error ? error.message : '未知錯誤';
    element('message').textContent = `無法套用：${message}。原結果保留。`;
  }
}
function restore(): void { input.value = JSON.stringify(sampleBackup, null, 2); apply(); }
button('apply').addEventListener('click', apply);
button('restore').addEventListener('click', () => { if (confirm('以範例取代目前輸入與結果？')) restore(); });
button('assertion').addEventListener('click', () => {
  const report = demonstrateAssertion();
  element('assertion-report').textContent = `as Backup 通過編譯，但 equipment 實際型別為 ${report.observedType}。執行期驗證${report.accepted ? '接受' : '拒絕'}此資料：${report.message}`;
});
for (const id of ['apply', 'restore', 'assertion']) button(id).disabled = false;
element('setup').textContent = '編譯後的 JavaScript 模組已載入。本頁做 JSON 執行期驗證，不在瀏覽器內執行 tsc；修改 src 後需重新建置與整理頁面。';
restore();
