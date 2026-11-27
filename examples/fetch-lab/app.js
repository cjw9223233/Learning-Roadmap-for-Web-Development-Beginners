'use strict';
const $ = id => document.getElementById(id);
let rows = [];
let active = null;
let serial = 0;

class LoadError extends Error {
  constructor(kind, message) { super(message); this.kind = kind; }
}

function parsePayload(text) {
  if (new Blob([text]).size > 128 * 1024) throw new LoadError('data', '本文超過本課 128 KiB 上限');
  let data;
  try { data = JSON.parse(text); }
  catch { throw new LoadError('json', 'JSON 語法錯誤'); }
  if (!data || data.version !== 1 || !Array.isArray(data.rows) || data.rows.length > 200) {
    throw new LoadError('data', '需要 version: 1 與最多 200 筆的 rows 陣列');
  }
  const ids = new Set();
  return data.rows.map((row, index) => {
    if (!row || typeof row.id !== 'string' || !/^[A-Za-z0-9_-]{1,64}$/.test(row.id) || ids.has(row.id) || typeof row.equipment !== 'string' || !row.equipment.trim() || row.equipment.trim().length > 80 || !['正常', '異常'].includes(row.result)) {
      throw new LoadError('data', `第 ${index + 1} 筆資料不符合契約`);
    }
    ids.add(row.id);
    return { id: row.id, equipment: row.equipment.trim(), result: row.result };
  });
}

function renderRows() {
  $('count').textContent = `目前 ${rows.length} 筆`;
  $('records').replaceChildren();
  if (rows.length === 0) {
    const li = document.createElement('li'); li.textContent = '目前清單沒有資料。'; $('records').append(li);
  }
  for (const row of rows) {
    const li = document.createElement('li'); li.textContent = `${row.equipment} · ${row.result}`; $('records').append(li);
  }
  $('json-output').textContent = JSON.stringify({ version: 1, rows }, null, 2);
}

function trace(job, text) {
  if (active !== job) return;
  const li = document.createElement('li'); li.textContent = text; $('trace').append(li);
}

$('load-form').addEventListener('submit', async event => {
  event.preventDefault();
  if (!['http:', 'https:'].includes(location.protocol)) {
    $('status').textContent = '需透過本機 HTTP 開啟，請先啟動專用 server.py；本次沒有送出請求。';
    return;
  }
  const scenario = $('scenario').value;
  const timeout = Number($('deadline').value);
  if (!['success', 'empty', 'not-found', 'server-error', 'invalid-json', 'invalid-data', 'slow', 'slow-body', 'disconnect'].includes(scenario) || ![1000, 5000].includes(timeout)) {
    $('status').textContent = '請選擇有效情境與等待上限。'; return;
  }
  const previous = active;
  const job = { id: ++serial, controller: new AbortController(), reason: '', timer: null };
  active = job;
  if (previous) { previous.reason = 'superseded'; previous.controller.abort(); }
  const url = `/api/inspections?case=${encodeURIComponent(scenario)}`;
  $('status').textContent = `載入中（第 ${job.id} 次）…前次成功清單暫時保留。`;
  $('http-state').textContent = '尚未收到 HTTP 回應。';
  $('request-url').textContent = `GET ${url}`;
  $('trace').replaceChildren();
  $('result-panel').setAttribute('aria-busy', 'true'); $('cancel').disabled = false;
  trace(job, '建立本次 AbortController，開始等待 Fetch。');
  job.timer = setTimeout(() => {
    if (active === job && !job.controller.signal.aborted) { job.reason = 'timeout'; job.controller.abort(); }
  }, timeout);
  try {
    const response = await fetch(url, { signal: job.controller.signal, cache: 'no-store', headers: { Accept: 'application/json' } });
    if (active !== job) return;
    $('http-state').textContent = `收到 HTTP ${response.status}（已取得回應標頭）。`;
    trace(job, `收到 HTTP ${response.status}；檢查 response.ok。`);
    if (!response.ok) throw new LoadError('http', `HTTP ${response.status}`);
    // 計時器此時仍在：收到標頭不代表本文已讀完。
    const text = await response.text();
    if (active !== job) return;
    if (job.controller.signal.aborted) throw new DOMException('Aborted', 'AbortError');
    trace(job, '本文讀取完成，接著解析 JSON 並驗證整份資料。');
    const candidate = parsePayload(text);
    rows = candidate;
    renderRows();
    $('http-state').textContent = `HTTP ${response.status}：本文與資料驗證已完成。`;
    $('status').textContent = `載入成功：${rows.length} 筆。`;
    trace(job, '全部驗證通過，才取代清單；沒有寫入 localStorage。');
  } catch (error) {
    if (active !== job) return;
    if (job.controller.signal.aborted) {
      $('status').textContent = job.reason === 'timeout' ? '載入逾時：已中止用戶端等待，原清單保留。' : '已取消：原清單保留。';
    } else if (error.kind === 'http') {
      $('status').textContent = `HTTP 錯誤：${error.message}，原清單保留。`;
    } else if (error.kind === 'json') {
      $('status').textContent = '解析失敗：JSON 語法錯誤，原清單保留。';
    } else if (error.kind === 'data') {
      $('status').textContent = `資料驗證失敗：${error.message}，原清單保留。`;
    } else {
      $('status').textContent = '網路或本文讀取失敗：未取得可用資料，原清單保留。';
    }
    trace(job, '本次未更新清單；可調整情境後由使用者決定是否重試。');
  } finally {
    clearTimeout(job.timer);
    if (active === job) {
      active = null; $('cancel').disabled = true; $('result-panel').setAttribute('aria-busy', 'false');
    }
  }
});

$('cancel').addEventListener('click', () => {
  if (active && !active.controller.signal.aborted) { active.reason = 'user'; active.controller.abort(); }
});

$('export').addEventListener('click', () => {
  const url = URL.createObjectURL(new Blob([JSON.stringify({ version: 1, rows }, null, 2)], { type: 'application/json' }));
  const a = document.createElement('a'); a.href = url; a.download = 'fetch-lab-backup.json'; a.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
});

renderRows();
if (location.protocol === 'file:') $('status').textContent = '目前以檔案開啟；閱讀可離線，實際 Fetch 需啟動專用本機伺服器。';
