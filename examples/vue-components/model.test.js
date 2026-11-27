import test from 'node:test';
import assert from 'node:assert/strict';
import { initialRecords, addRecord, renameRecord, changeResult, removeRecord, visibleRecords, summarize } from './model.js';

test('初始化不共用可變資料，預設統計為 3／2／1', () => {
  const a = initialRecords(); a[0].equipment = '修改';
  assert.notEqual(initialRecords()[0].equipment, '修改');
  assert.deepEqual(summarize(initialRecords()), { total: 3, normal: 2, abnormal: 1 });
});
test('新增去空白、保留舊資料，且不能偷偷加入其他欄位', () => {
  const a = initialRecords(); const next = addRecord(a, { equipment: ' A01 ', result: '正常', secret: 'ignored' }, 'r-4');
  assert.equal(a.length, 3); assert.equal(next.length, 4);
  assert.deepEqual(next[3], { id: 'r-4', equipment: 'A01', result: '正常' });
});
test('不合法名稱與外部事件資料拒絕，來源不變', () => {
  const a = initialRecords(); const before = JSON.stringify(a);
  for (const equipment of [' ', 42, 'x'.repeat(81)]) assert.throws(() => addRecord(a, { equipment, result: '正常' }, 'r-4'));
  assert.throws(() => addRecord(a, null, 'r-4'));
  assert.equal(JSON.stringify(a), before);
});
test('資料模型拒絕重複識別碼與未知結果', () => {
  const a = initialRecords();
  assert.throws(() => addRecord(a, { equipment: 'A', result: '正常' }, 'r-1'));
  assert.throws(() => addRecord(a, { equipment: 'A', result: '未知' }, 'r-4'));
  assert.throws(() => changeResult(a, 'r-1', '未知'));
});
test('編輯保留識別碼，僅更改指定資料，來源不變', () => {
  const a = initialRecords(); const next = renameRecord(a, 'r-2', ' 新名稱 ');
  assert.equal(next[1].id, 'r-2'); assert.equal(next[1].equipment, '新名稱');
  assert.equal(a[1].equipment, '閘門 B02'); assert.deepEqual(next[0], a[0]);
});
test('不存在的識別碼不能修改或刪除', () => {
  const a = initialRecords();
  assert.throws(() => renameRecord(a, 'missing', 'A'));
  assert.throws(() => changeResult(a, 'missing', '正常'));
  assert.throws(() => removeRecord(a, 'missing'));
});
test('切換結果後，異常篩選與全量統計反映相同資料', () => {
  const a = changeResult(initialRecords(), 'r-2', '正常');
  assert.deepEqual(visibleRecords(a, '異常', false), []);
  assert.deepEqual(summarize(a), { total: 3, normal: 3, abnormal: 0 });
});
test('刪除一筆不修改來源，剩下資料保留識別碼', () => {
  const a = initialRecords(); const next = removeRecord(a, 'r-2');
  assert.equal(a.length, 3); assert.deepEqual(next.map(r => r.id), ['r-1', 'r-3']);
});
test('反轉顯示與篩選不修改主清單順序，未知條件拒絕', () => {
  const a = initialRecords(); const before = JSON.stringify(a);
  assert.deepEqual(visibleRecords(a, '正常', true).map(r => r.id), ['r-3', 'r-1']);
  assert.equal(JSON.stringify(a), before); assert.throws(() => visibleRecords(a, '未知', false));
});
test('200 筆上限拒絕第 201 筆，空清單統計有效', () => {
  const full = Array.from({ length: 200 }, (_, i) => ({ id: `x-${i}`, equipment: 'A', result: '正常' }));
  assert.throws(() => addRecord(full, { equipment: 'B', result: '正常' }, 'r-new'));
  assert.equal(full.length, 200); assert.deepEqual(summarize([]), { total: 0, normal: 0, abnormal: 0 });
});
