<script setup>
import { ref, computed } from 'vue';
import { initialRecords, addRecord, renameRecord, changeResult, removeRecord, visibleRecords, summarize } from './model.js';
import SummaryPanel from './components/SummaryPanel.vue';
import InspectionForm from './components/InspectionForm.vue';
import InspectionRow from './components/InspectionRow.vue';
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
</script>

<template>
<main><header><p class="eyebrow">VUE SFC / VITE / BUILD</p><h1>把元件寫進 .vue，<br>再把來源變成產物。</h1><p id="build-marker">SFC 原始版</p><p id="setup" role="status">Vue SFC 已掛載。修改來源後，dev 通常會熱更新；preview 需先重新 build 再整理。資料只保留在當頁記憶體。</p></header>
  <section class="card" id="workspace"><h2>1. 表單擁有自己的草稿</h2><inspection-form @add-record="add"></inspection-form>
    <p id="message" role="status" aria-live="polite">{{ message }}</p></section>
  <section class="card"><h2>2. 同一個統計元件，兩份不同 Props</h2>
    <div class="summary-grid"><summary-panel title="全部資料" :counts="allCounts"></summary-panel><summary-panel title="目前顯示" :counts="visibleCounts"></summary-panel></div>
  </section>
  <section class="card"><h2>3. 狀態改變，畫面跟著更新</h2>
    <div class="toolbar"><div><label for="filter">顯示條件</label><select id="filter" v-model="filter"><option>全部</option><option>正常</option><option>異常</option></select></div>
    <button type="button" class="secondary" id="reverse" @click="reversed = !reversed">反轉顯示順序</button></div>
    <p class="muted">篩選不刪除原資料；反轉順序時，編輯草稿仍跟著相同識別碼。被篩掉的列會卸載，其未儲存草稿也會消失。</p>
    <ul id="records"><inspection-row v-for="row in visible" :key="row.id" :row="row" @rename-record="rename" @change-result="toggle" @remove-record="remove"></inspection-row></ul>
    <p id="empty" v-if="visible.length === 0">目前條件沒有資料；可切換條件或新增一筆。</p>
  </section>
  <aside class="flow-box"><h2>最近一次資料流</h2><p id="flow" aria-live="polite">{{ flow }}</p></aside>
<footer>第 3B 階段 · 真正的 .vue 與 Vite 建置 · 重新整理還原三筆資料</footer></main>
</template>
