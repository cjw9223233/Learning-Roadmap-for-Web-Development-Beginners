import test from 'node:test';
import assert from 'node:assert/strict';
import { parseInspections, summarize } from './dist/inspection.js';
import { demonstrateAssertion } from './dist/assertion-demo.js';

const record = (id, equipment = 'A01', result = '正常') => ({ id, equipment, result });
const text = rows => JSON.stringify({ version: 1, rows });
test('合法資料會去空白並重建欄位', () => assert.deepEqual(parseInspections(text([{ ...record('a', ' A01 '), extra: true }])), [record('a')]));
test('壞 JSON 拒絕', () => assert.throws(() => parseInspections('{'), /JSON 語法錯誤/));
test('根資料與版本拒絕', () => {
  for (const input of ['null', '[]', '{}', '{"version":2,"rows":[]}']) assert.throws(() => parseInspections(input));
});
test('第二筆不合規時整份拒絕', () => assert.throws(() => parseInspections(text([record('a'), record('b', ' ')])), /第 2 筆/));
test('未知結果與數字名稱在執行期拒絕', () => {
  assert.throws(() => parseInspections(text([record('a', 'A', '未知')])));
  assert.throws(() => parseInspections(text([record('a', 42)])));
});
test('重複或非法 ID 拒絕', () => {
  assert.throws(() => parseInspections(text([record('a'), record('a')])));
  assert.throws(() => parseInspections(text([record('<img>')])));
});
test('名稱 80 接受、81 拒絕', () => {
  assert.equal(parseInspections(text([record('a', 'A'.repeat(80))])).length, 1);
  assert.throws(() => parseInspections(text([record('a', 'A'.repeat(81))])));
});
test('200 筆接受、201 筆與超大輸入拒絕', () => {
  assert.equal(parseInspections(text(Array.from({ length: 200 }, (_, i) => record('id' + i)))).length, 200);
  assert.throws(() => parseInspections(text(Array.from({ length: 201 }, (_, i) => record('id' + i)))));
  assert.throws(() => parseInspections(' '.repeat(128 * 1024 + 1)));
});
test('統計正常與異常', () => assert.deepEqual(summarize(parseInspections(text([record('a'), record('b', 'B', '異常')]))), { total: 2, normal: 1, abnormal: 1 }));
test('有效空清單', () => assert.deepEqual(summarize(parseInspections(text([]))), { total: 0, normal: 0, abnormal: 0 }));
test('型別斷言沒有改變真實型別，驗證器仍拒絕', () => {
  const report = demonstrateAssertion(); assert.equal(report.observedType, 'number'); assert.equal(report.accepted, false);
});
test('未經 TypeScript 檢查的 JS 呼叫仍受執行期檢查', () => assert.throws(() => parseInspections(42), /JSON 字串/));
