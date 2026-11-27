import { initialRecords, addRecord, renameRecord, changeResult, removeRecord, visibleRecords, summarize } from './model.js';
import { SummaryPanel, InspectionForm, InspectionRow } from './components.js';
const { createApp, ref, computed } = globalThis.Vue;

const app = createApp({
  components: { SummaryPanel, InspectionForm, InspectionRow },
  setup() {
    // 主清單只有父元件擁有；子元件收到 props 並發出事件。
    const rows = ref(initialRecords());
    const filter = ref('全部');
    const reversed = ref(false);
    const message = ref('已載入三筆虛構資料；重新整理會還原。');
    const flow = ref('等待操作：子元件事件 → 父元件驗證與更新 → Props／衍生統計');
    let nextId = 4;
    const visible = computed(() => visibleRecords(rows.value, filter.value, reversed.value));
    const allCounts = computed(() => summarize(rows.value));
    const visibleCounts = computed(() => summarize(visible.value));
    function update(action, text, origin) {
      try {
        rows.value = action();
        message.value = text;
        flow.value = `${origin} → 父元件驗證並更新主清單 → 巡檢列與統計收到新資料`;
      } catch (e) { message.value = `無法更新：${e.message}。原資料保留。`; }
    }
    function add(draft) { update(() => addRecord(rows.value, draft, `r-${nextId++}`), '已新增巡檢；表單草稿保留。', '新增表單發出 add-record'); }
    function rename(payload) { update(() => renameRecord(rows.value, payload.id, payload.equipment), '已修改設備名稱。', '巡檢列發出 rename-record'); }
    function toggle(payload) { update(() => changeResult(rows.value, payload.id, payload.result), '已變更巡檢結果；符合篩選的清單同步更新。', '巡檢列發出 change-result'); }
    function remove(id) {
      if (confirm('刪除這筆虛構巡檢資料？')) update(() => removeRecord(rows.value, id), '已刪除巡檢。', '巡檢列發出 remove-record');
    }
    return { filter, reversed, visible, allCounts, visibleCounts, message, flow, add, rename, toggle, remove };
  }
});
app.mount('#app');
document.getElementById('setup').textContent = `Vue ${globalThis.Vue.version} 已載入本機檔案。資料只保留在當頁記憶體；本課沒有讀寫 localStorage 或連接 API。`;
