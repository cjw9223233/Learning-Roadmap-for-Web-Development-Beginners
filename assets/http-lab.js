'use strict';
(() => {
  const $ = id => document.getElementById(id);
  const method = $('method'), path = $('path'), body = $('body'), condition = $('condition');
  const validBody = JSON.stringify({ equipment: 'A02 月台照明', result: '正常' }, null, 2);
  const presets = {
    read: ['GET', '/api/inspections', validBody, 'normal'],
    create: ['POST', '/api/inspections', validBody, 'normal'],
    invalid: ['POST', '/api/inspections', '{"equipment":"   ","result":"正常"}', 'normal'],
    missing: ['GET', '/api/missing', validBody, 'normal'],
    method: ['POST', '/api/inspections/1', validBody, 'normal'],
    server: ['POST', '/api/inspections', validBody, 'server'],
    network: ['POST', '/api/inspections', validBody, 'network']
  };
  let rows, nextId;
  function restoreSeed() {
    rows = [{ id: 1, equipment: 'A01 月台照明', result: '正常' }]; nextId = 2;
    renderData();
  }
  function renderData() {
    $('db-count').textContent = `目前 ${rows.length} 筆模擬巡檢`;
    $('db-output').textContent = JSON.stringify(rows, null, 2);
  }
  function syncMethod() {
    body.disabled = method.value === 'GET';
    $('body-help').textContent = body.disabled ? '目前為 GET，本模型不使用請求內容。' : '此模型要求 equipment 為 1–80 字元文字，result 為「正常」或「異常」。';
  }
  method.addEventListener('change', syncMethod);
  document.querySelectorAll('[data-preset]').forEach(button => button.addEventListener('click', () => {
    [method.value, path.value, body.value, condition.value] = presets[button.dataset.preset];
    $('prediction').value = ''; syncMethod();
    $('preset-note').textContent = `已帶入「${button.textContent}」。欄位尚未送出，先預測再操作；下方仍是上次送出的結果。`;
  }));
  $('request-form').addEventListener('submit', event => {
    event.preventDefault();
    const verb = method.value, resource = path.value.trim();
    const before = rows.length;
    const trace = [`① 瀏覽器模型：組成 ${verb} ${resource} 請求。`];
    const requestHeaders = ['Host: training.invalid'];
    if (verb === 'POST') requestHeaders.push('Content-Type: application/json');
    $('request-output').textContent = `${verb} ${resource} HTTP/1.1\n${requestHeaders.join('\n')}\n\n${verb === 'POST' ? body.value : ''}`;
    let code = null, payload = null, headers = [], explanation = '';
    const respond = (status, value, note, extra = []) => { code = status; payload = value; explanation = note; headers = extra; };
    if (condition.value === 'network') {
      trace.push('② 網路模型：連線在抵達伺服器前中斷。', '③ 伺服器模型未收到請求；沒有存取模擬資料，也沒有 HTTP 回應。');
      explanation = '本例沒有收到 HTTP 狀態碼。網路連線失敗與伺服器回覆 500 不同；真實逾時也可能發生在寫入之後，不能假設都與本模型相同。';
    } else {
      trace.push('② 網路模型：請求抵達模擬伺服器。');
      if (condition.value === 'server') {
        trace.push('③ 伺服器模型：在資料寫入前發生錯誤，停止處理。');
        respond(500, { error: '模擬伺服器暫時無法完成請求' }, '收到 500 回應表示伺服器回報失敗。本模型在寫入前停止；真實系統不保證 500 時沒有寫入。');
      } else {
        const collection = resource === '/api/inspections';
        const itemMatch = resource.match(/^\/api\/inspections\/([1-9]\d*)$/);
        if (!collection && !itemMatch) {
          trace.push('③ 路由模型：找不到這個路徑，未進行資料讀寫。');
          respond(404, { error: '資源路徑不存在' }, '404 表示找不到目標資源。本模型只實作巡檢清單與數字 ID 路徑。');
        } else if (verb === 'POST' && !collection) {
          trace.push('③ 路由模型：路徑已知，但不允許 POST，未寫入資料。');
          respond(405, { error: '此路徑只允許 GET' }, '405 表示請求方法不被目標資源允許。請查看 Allow 標頭，或將方法改成 GET。', ['Allow: GET']);
        } else if (verb === 'GET') {
          trace.push('③ 路由模型：接受 GET，讀取模擬資料。');
          const row = itemMatch ? rows.find(r => r.id === Number(itemMatch[1])) : null;
          if (itemMatch && !row) respond(404, { error: '巡檢紀錄不存在' }, '路由雖然存在，但找不到這個 ID 的紀錄；資料筆數不變。');
          else respond(200, itemMatch ? row : rows, 'GET 成功讀取資料。本模型沒有新增、修改或刪除巡檢；回應內容是資料的 JSON 表示。');
          trace.push('④ 模擬資料：只執行讀取，沒有寫入。');
        } else {
          let value;
          trace.push('③ 驗證模型：解析 JSON 並檢查 equipment 與 result。');
          try { value = JSON.parse(body.value); }
          catch { respond(400, { error: 'JSON 語法錯誤' }, '內容不是合法 JSON，請檢查引號、大括號與逗號。尚未寫入資料。'); }
          if (code === null) {
            if (!value || Array.isArray(value) || typeof value !== 'object' || typeof value.equipment !== 'string' || !value.equipment.trim() || value.equipment.trim().length > 80 || !['正常', '異常'].includes(value.result)) {
              respond(400, { error: 'equipment 須為 1–80 字元文字，result 須為正常或異常' }, 'JSON 可以解析，仍可能不符合資料規則。此模型以 400 表示驗證錯誤；實際 API 的契約可能不同。');
            } else {
              const row = { id: nextId++, equipment: value.equipment.trim(), result: value.result };
              rows.push(row);
              trace.push(`④ 模擬資料：新增 ID ${row.id} 的巡檢紀錄。`);
              respond(201, row, '201 表示建立了新資源，Location 指出其路徑。再送出相同 POST 會再建立一筆；本模型沒有重複提交保護。', [`Location: /api/inspections/${row.id}`]);
            }
          }
          if (code === 400) trace.push('④ 模擬資料：驗證未通過，沒有寫入。');
        }
      }
    }
    const labels = { 200: 'OK', 201: 'Created', 400: 'Bad Request', 404: 'Not Found', 405: 'Method Not Allowed', 500: 'Internal Server Error' };
    const expected = $('prediction').value;
    const result = code === null ? 'none' : String(code);
    const prediction = !expected ? '尚未預測；下次可先選答案。' : expected === result ? '預測正確。' : '預測與結果不同，請比較處理步驟。';
    $('result-summary').textContent = `${code === null ? '無 HTTP 回應' : `${code} ${labels[code]}`} · ${prediction}`;
    if (code === null) $('response-output').textContent = '沒有 HTTP 回應，沒有狀態碼。\n（連線在抵達伺服器前失敗的模擬）';
    else {
      $('response-output').textContent = `HTTP/1.1 ${code} ${labels[code]}\nContent-Type: application/json\n${headers.length ? headers.join('\n') + '\n' : ''}\n${JSON.stringify(payload, null, 2)}`;
      trace.push(`⑤ 回應模型：瀏覽器收到 ${code} 與 JSON 內容。`);
    }
    trace.push(`資料對照：送出前 ${before} 筆 → 送出後 ${rows.length} 筆。`);
    $('trace').replaceChildren(...trace.map(text => { const li = document.createElement('li'); li.textContent = text; return li; }));
    $('explanation').textContent = explanation;
    $('preset-note').textContent = '已送出目前欄位的模擬請求。';
    renderData();
  });
  $('reset-model').addEventListener('click', () => {
    if (!confirm('將當頁模擬資料還原為一筆起始紀錄？')) return;
    restoreSeed();
    $('request-output').textContent = '尚未送出'; $('response-output').textContent = '尚未收到回應';
    $('trace').replaceChildren(); $('explanation').textContent = '';
    $('result-summary').textContent = '已還原一筆起始資料；欄位保留，可重新預測與送出。';
    $('preset-note').textContent = '已重設模擬資料，尚未送出下一次請求。';
    $('prediction').value = '';
  });
  restoreSeed(); syncMethod();
})();
