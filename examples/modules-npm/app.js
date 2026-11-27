import { parseInspections, summarize } from './inspection.js';
import { sampleBackup } from './sample.js';

const $ = id => document.getElementById(id);
function apply() {
  try {
    const rows = parseInspections($('json-input').value);
    const counts = summarize(rows);
    for (const key of ['total', 'normal', 'abnormal']) $(key).textContent = counts[key];
    $('records').replaceChildren();
    if (rows.length === 0) {
      const li = document.createElement('li'); li.textContent = '有效空清單。'; $('records').append(li);
    }
    for (const row of rows) {
      const li = document.createElement('li'); li.textContent = `${row.equipment} · ${row.result}`; $('records').append(li);
    }
    $('message').textContent = '驗證通過，已更新統計。';
  } catch (error) { $('message').textContent = `無法套用：${error.message}。原結果保留。`; }
}
function restore() { $('json-input').value = JSON.stringify(sampleBackup, null, 2); apply(); }
$('apply').addEventListener('click', apply);
$('restore').addEventListener('click', () => { if (confirm('用範例取代目前輸入及結果？')) restore(); });
$('apply').disabled = false; $('restore').disabled = false;
$('setup').textContent = '模組已載入：app.js 匯入 inspection.js，與命令列及測試使用同一份規則。';
restore();
