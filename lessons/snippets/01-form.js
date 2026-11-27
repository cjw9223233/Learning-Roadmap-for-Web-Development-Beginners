'use strict';

// 先連接畫面。id 必須與 HTML 一致；script 放在 body 的最後。
const form = document.getElementById('inspection-form');
const equipmentInput = document.getElementById('equipment');
const resultInput = document.getElementById('result');
const filter = document.getElementById('filter');
const list = document.getElementById('records');
const count = document.getElementById('count');
const message = document.getElementById('message');

// 陣列保存資料；DOM 只是把目前的資料顯示出來。
const rows = [];

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

form.addEventListener('submit', event => {
  // 由 JavaScript 處理本次提交，避免瀏覽器預設的頁面導向。
  event.preventDefault();
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
  rows.push({ equipment, result });
  form.reset();
  render();
  equipmentInput.focus();
  message.textContent = filter.value !== 'all' && filter.value !== result
    ? '已新增，但目前篩選條件隱藏了這筆紀錄。可切回全部查看。'
    : '已新增至當頁清單。重新整理會清空紀錄。';
});

filter.addEventListener('change', render);
render();
