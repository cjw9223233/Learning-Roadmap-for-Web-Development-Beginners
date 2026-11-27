import test from 'node:test';
import assert from 'node:assert/strict';
import { parseInspections, summarize } from './inspection.js';

const record = (id, equipment = 'A01', result = '正常') => ({ id, equipment, result });
const text = rows => JSON.stringify({ version: 1, rows });

test('合法資料去空白且只留下契約欄位', () => {
  const rows = parseInspections(text([{ ...record('a', ' A01 '), station: 'extra' }]));
  assert.deepEqual(rows, [record('a')]);
});
test('不合法 JSON 被拒絕', () => assert.throws(() => parseInspections('{'), /JSON 語法錯誤/));
test('格式、版本與輸入型別都要檢查', () => {
  for (const value of ['null', '[]', '{}', '{"version":2,"rows":[]}']) assert.throws(() => parseInspections(value));
  assert.throws(() => parseInspections({ version: 1, rows: [] }));
});
test('第二筆不合規時整份拒絕', () => assert.throws(() => parseInspections(text([record('a'), record('b', '   ')])), /第 2 筆/));
test('未知結果被拒絕', () => assert.throws(() => parseInspections(text([record('a', 'A', '未知')]))));
test('ID 必須唯一且符合格式', () => {
  assert.throws(() => parseInspections(text([record('same'), record('same')])));
  assert.throws(() => parseInspections(text([record('<img>')])));
});
test('設備名稱 80 的邊界與 81 的拒絕', () => {
  assert.equal(parseInspections(text([record('a', 'A'.repeat(80))])).length, 1);
  assert.throws(() => parseInspections(text([record('a', 'A'.repeat(81))])));
});
test('最多 200 筆，超大字串也拒絕', () => {
  assert.equal(parseInspections(text(Array.from({ length: 200 }, (_, i) => record('a' + i)))).length, 200);
  assert.throws(() => parseInspections(text(Array.from({ length: 201 }, (_, i) => record('a' + i)))));
  assert.throws(() => parseInspections(' '.repeat(128 * 1024 + 1)));
});
test('統計涵蓋正常與異常', () => {
  assert.deepEqual(summarize(parseInspections(text([record('a'), record('b', 'B', '異常'), record('c')]))), { total: 3, normal: 2, abnormal: 1 });
});
test('有效空清單可以統計', () => assert.deepEqual(summarize(parseInspections(text([]))), { total: 0, normal: 0, abnormal: 0 }));
