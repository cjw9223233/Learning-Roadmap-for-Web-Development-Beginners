// 這個模組不使用 document、檔案或 localStorage，供不同入口重用。
export function parseInspections(text) {
  if (typeof text !== 'string') throw new Error('輸入須為 JSON 字串');
  if (new TextEncoder().encode(text).length > 128 * 1024) throw new Error('JSON 超過 128 KiB');
  let data;
  try { data = JSON.parse(text); }
  catch { throw new Error('JSON 語法錯誤'); }
  if (!data || data.version !== 1 || !Array.isArray(data.rows) || data.rows.length > 200) {
    throw new Error('需要 version: 1 與最多 200 筆的 rows 陣列');
  }
  const ids = new Set();
  return data.rows.map((row, index) => {
    if (!row || typeof row.id !== 'string' || !/^[A-Za-z0-9_-]{1,64}$/.test(row.id) || ids.has(row.id) || typeof row.equipment !== 'string' || !row.equipment.trim() || row.equipment.trim().length > 80 || !['正常', '異常'].includes(row.result)) {
      throw new Error(`第 ${index + 1} 筆資料不符合契約`);
    }
    ids.add(row.id);
    return { id: row.id, equipment: row.equipment.trim(), result: row.result };
  });
}

// 預期接收 parseInspections 驗證通過後的清單。
export function summarize(rows) {
  return {
    total: rows.length,
    normal: rows.filter(row => row.result === '正常').length,
    abnormal: rows.filter(row => row.result === '異常').length
  };
}
