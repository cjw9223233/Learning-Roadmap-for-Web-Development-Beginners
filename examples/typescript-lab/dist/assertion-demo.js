import { parseInspections } from './inspection.js';
export function demonstrateAssertion() {
    const incoming = {
        version: 1,
        rows: [{ id: 'bad', equipment: 42, result: '未知' }]
    };
    // 刻意的錯誤做法：as 不會改變或驗證 incoming。
    const assumed = incoming;
    const observedType = typeof assumed.rows[0]?.equipment;
    let accepted = false;
    let message = '';
    try {
        parseInspections(JSON.stringify(incoming));
        accepted = true;
        message = '資料被接受';
    }
    catch (error) {
        message = error instanceof Error ? error.message : '未知錯誤';
    }
    return { observedType, accepted, message };
}
