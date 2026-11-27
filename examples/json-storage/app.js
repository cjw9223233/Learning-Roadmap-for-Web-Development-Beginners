'use strict';
const storageKey = 'web-storage-lab-v1';
const maxBytes = 128 * 1024;
const maxRows = 200;
const $ = id => document.getElementById(id);
let rows = [];
let dirty = false;
let locked = false;
let storageLabel = '尚未讀取保存版本。';

// JSON 能解析，還不代表欄位、版本與每筆資料都正確。
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

function makeBackup() { return { version: 1, rows }; }
function asJSON() { return JSON.stringify(makeBackup(), null, 2); }
function say(text) { $('message').textContent = text; }

function render() {
  $('memory-state').textContent = dirty ? '記憶體：有尚未保存的變更。' : locked ? '記憶體：保留可讀清單，無法與保存版本比較。' : '記憶體：與最近讀取／保存的版本一致。';
  $('save-state').textContent = storageLabel;
  $('save').disabled = locked;
  $('count').textContent = `記憶體共 ${rows.length} 筆紀錄`;
  $('records').replaceChildren();
  if (rows.length === 0) {
    const li = document.createElement('li'); li.textContent = '目前沒有紀錄。'; $('records').append(li);
  }
  for (const row of rows) {
    const li = document.createElement('li');
    li.textContent = `${row.equipment} · ${row.result}`;
    $('records').append(li);
  }
  $('current-json').textContent = asJSON();
}

function loadSaved() {
  let didRead = false;
  try {
    const raw = localStorage.getItem(storageKey);
    didRead = true;
    $('original').textContent = raw === null ? '沒有此練習的保存內容。' : raw;
    const loaded = raw === null ? [] : parseBackup(raw);
    rows = loaded;
    dirty = false; locked = false;
    storageLabel = raw === null ? '瀏覽器：尚無保存版本。' : `瀏覽器：已讀取 ${rows.length} 筆保存紀錄。`;
    say('讀取完成。新增與匯入仍需另外按保存。');
  } catch (error) {
    locked = true;
    storageLabel = '瀏覽器：讀取失敗，保存已鎖定。';
    if (!didRead) $('original').textContent = '本次無法取得原始保存內容。';
    say(`無法讀取：${error.message}。記憶體資料保留，原保存值不自動覆寫；可先匯出備份。`);
  }
  render();
}

$('entry-form').addEventListener('submit', event => {
  event.preventDefault();
  const equipment = $('equipment').value.trim();
  const result = $('result').value;
  if (!equipment || equipment.length > 80 || !['正常', '異常'].includes(result)) {
    say('設備名稱須為 1–80 字元，結果須為正常或異常。'); $('equipment').focus(); return;
  }
  if (rows.length >= maxRows) { say('最多 200 筆；請先匯出目前資料，再整理備份。'); return; }
  rows.push({ id: crypto.randomUUID(), equipment, result });
  dirty = true; render(); $('entry-form').reset(); $('equipment').focus();
  say(locked ? '已新增到記憶體。保存目前鎖定，請匯出備份。' : '已新增到記憶體，尚未保存到瀏覽器。');
});

$('save').addEventListener('click', () => {
  if (locked) { say('保存已鎖定，請先處理原保存資料。'); return; }
  try {
    const text = asJSON();
    localStorage.setItem(storageKey, text);
    dirty = false;
    storageLabel = `瀏覽器：已保存 ${rows.length} 筆紀錄。`;
    $('original').textContent = text;
    say('保存成功。現在重新整理可嘗試還原；仍建議另外匯出備份。');
  } catch (error) {
    storageLabel = '瀏覽器：本次保存失敗。';
    say(`保存失敗：${error.name}。記憶體仍在，請匯出 JSON 備份。`);
  }
  render();
});

$('reload').addEventListener('click', () => {
  if (dirty && !confirm('重新讀取會捨棄尚未保存的記憶體變更。是否繼續？')) return;
  loadSaved();
});

$('export').addEventListener('click', () => {
  const url = URL.createObjectURL(new Blob([asJSON()], { type: 'application/json' }));
  const a = document.createElement('a'); a.href = url; a.download = 'storage-lab-backup.json'; a.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
  say('已產生目前記憶體的備份下載，請確認檔案實際存到電腦。');
});

$('fill-json').addEventListener('click', () => {
  if ($('json-input').value !== asJSON() && !confirm('以目前記憶體 JSON 取代文字區內容？尚未套用的編輯會被捨棄。')) return;
  $('json-input').value = asJSON(); say('已帶入目前 JSON；編輯文字區不會立刻改變清單。');
});

$('apply').addEventListener('click', () => {
  try {
    const candidate = parseBackup($('json-input').value);
    if (!confirm(`驗證通過，共 ${candidate.length} 筆。取代目前記憶體清單？此步不會寫入瀏覽器保存版本。`)) return;
    rows = candidate; dirty = true; render();
    say('已取代記憶體清單，尚未保存到瀏覽器。');
  } catch (error) { say(`匯入失敗：${error.message}。記憶體與保存版本都未更動。`); }
});

$('import-file').addEventListener('change', async event => {
  const file = event.target.files[0]; if (!file) return;
  $('controls').disabled = true;
  try {
    if (file.size > maxBytes) throw new Error('檔案超過 128 KiB');
    const text = await file.text();
    $('json-input').value = text;
    say('檔案已讀入文字區。清單未改變；請再按驗證並取代記憶體。');
  } catch (error) { say(`讀檔失敗：${error.message}。原文字區與清單保留。`); }
  finally { event.target.value = ''; $('controls').disabled = false; render(); }
});

$('clear').addEventListener('click', () => {
  if (!confirm('清空此練習的當頁紀錄與保存項目？請先匯出可讀資料；若原值損壞，請先複製原始內容留存。其他教材資料不受影響。')) return;
  try {
    localStorage.removeItem(storageKey);
    rows = []; dirty = false; locked = false;
    storageLabel = '瀏覽器：已清除此練習的保存項目。';
    $('original').textContent = '沒有此練習的保存內容。';
    $('json-input').value = asJSON();
    say('已清除此練習資料，可重新開始。');
  } catch (error) { say(`無法清除：${error.name}。當頁紀錄未清空。`); }
  render();
});

loadSaved();
$('json-input').value = asJSON();
