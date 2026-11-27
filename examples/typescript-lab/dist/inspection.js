function isRecord(value) {
    return typeof value === 'object' && value !== null && !Array.isArray(value);
}
// 型別描述內部資料；這些 if 才是外部資料的執行期檢查。
export function parseInspections(text) {
    if (typeof text !== 'string')
        throw new Error('輸入須為 JSON 字串');
    if (new TextEncoder().encode(text).length > 128 * 1024)
        throw new Error('JSON 超過 128 KiB');
    let value;
    try {
        value = JSON.parse(text);
    }
    catch {
        throw new Error('JSON 語法錯誤');
    }
    if (!isRecord(value) || value.version !== 1 || !Array.isArray(value.rows) || value.rows.length > 200) {
        throw new Error('需要 version: 1 與最多 200 筆的 rows 陣列');
    }
    const rawRows = value.rows;
    const ids = new Set();
    return rawRows.map((row, index) => {
        if (!isRecord(row))
            throw new Error(`第 ${index + 1} 筆不是資料物件`);
        const { id, equipment, result } = row;
        if (typeof id !== 'string' || !/^[A-Za-z0-9_-]{1,64}$/.test(id) || ids.has(id) || typeof equipment !== 'string' || !equipment.trim() || equipment.trim().length > 80 || (result !== '正常' && result !== '異常')) {
            throw new Error(`第 ${index + 1} 筆資料不符合契約`);
        }
        ids.add(id);
        return { id, equipment: equipment.trim(), result };
    });
}
// 呼叫端仍應先以 parseInspections 驗證外部資料。
export function summarize(rows) {
    return {
        total: rows.length,
        normal: rows.filter(row => row.result === '正常').length,
        abnormal: rows.filter(row => row.result === '異常').length
    };
}
