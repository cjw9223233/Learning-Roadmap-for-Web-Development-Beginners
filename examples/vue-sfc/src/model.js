import { parseInspections, summarize } from './inspection.js';
export { summarize };

export function initialRecords() {
  return [
    { id: 'r-1', equipment: '月台照明 A01', result: '正常' },
    { id: 'r-2', equipment: '閘門 B02', result: '異常' },
    { id: 'r-3', equipment: '旅客資訊看板 C03', result: '正常' }
  ];
}
function validate(rows) {
  return parseInspections(JSON.stringify({ version: 1, rows }));
}
function requireId(rows, id) {
  if (!rows.some(row => row.id === id)) throw new Error('找不到這筆巡檢');
}
export function validateEquipment(value) {
  if (typeof value !== 'string' || !value.trim() || value.trim().length > 80) {
    throw new Error('設備名稱需為 1–80 字，不能只有空白');
  }
  return value.trim();
}
export function addRecord(rows, draft, id) {
  if (!draft || typeof draft !== 'object') throw new Error('新增內容不是資料物件');
  return validate([...rows, { id, equipment: validateEquipment(draft.equipment), result: draft.result }]);
}
export function renameRecord(rows, id, equipment) {
  requireId(rows, id);
  const name = validateEquipment(equipment);
  return validate(rows.map(row => row.id === id ? { ...row, equipment: name } : row));
}
export function changeResult(rows, id, result) {
  requireId(rows, id);
  return validate(rows.map(row => row.id === id ? { ...row, result } : row));
}
export function removeRecord(rows, id) {
  requireId(rows, id);
  return rows.filter(row => row.id !== id);
}
export function visibleRecords(rows, filter, reversed) {
  if (!['全部', '正常', '異常'].includes(filter)) throw new Error('未知篩選條件');
  const visible = rows.filter(row => filter === '全部' || row.result === filter);
  return reversed ? visible.reverse() : visible;
}
