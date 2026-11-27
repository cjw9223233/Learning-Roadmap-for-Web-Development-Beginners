// 本檔刻意有錯，僅供 npm run check:errors；正常建置排除此檔。
import type { Inspection, Summary } from './inspection.js';

const wrongResult: Inspection = { id: 'a', equipment: 'A01', result: '未知' };
const wrongName: Inspection = { id: 'b', equipment: 42, result: '正常' };
const wrongSummary: Summary = { total: '3', normal: 2, abnormal: 1 };
const typo = wrongResult.equpment;
console.log(wrongName, wrongSummary, typo);
