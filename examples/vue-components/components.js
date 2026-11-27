import { validateEquipment } from './model.js';
const { ref } = globalThis.Vue;

export const SummaryPanel = {
  props: { title: { type: String, required: true }, counts: { type: Object, required: true } },
  template: `<section class="summary-panel" :aria-label="title">
    <h3>{{ title }}</h3><dl class="stats">
    <div><dt>總數</dt><dd class="total">{{ counts.total }}</dd></div>
    <div><dt>正常</dt><dd class="normal">{{ counts.normal }}</dd></div>
    <div><dt>異常</dt><dd class="abnormal">{{ counts.abnormal }}</dd></div>
    </dl></section>`
};

export const InspectionForm = {
  emits: ['add-record'],
  setup(_props, { emit }) {
    const equipment = ref('');
    const result = ref('正常');
    const error = ref('');
    function submit() {
      try {
        const name = validateEquipment(equipment.value);
        error.value = '';
        emit('add-record', { equipment: name, result: result.value });
        // emit 不是回傳父元件成功與否的函式；本課保留草稿，由使用者確認結果。
      } catch (e) { error.value = e.message; }
    }
    return { equipment, result, error, submit };
  },
  template: `<form id="add-form" @submit.prevent="submit" novalidate>
    <label for="equipment">設備名稱</label>
    <input id="equipment" v-model="equipment" maxlength="80" autocomplete="off" aria-describedby="draft-note form-error">
    <label for="result">巡檢結果</label>
    <select id="result" v-model="result"><option>正常</option><option>異常</option></select>
    <p id="draft-note" class="muted">輸入是表單自己的草稿，按新增才會更新主清單。送出後保留草稿，請先確認下方訊息。</p>
    <p id="form-error" class="error" role="status">{{ error }}</p>
    <button type="submit">新增巡檢</button>
  </form>`
};

export const InspectionRow = {
  props: { row: { type: Object, required: true } },
  emits: ['rename-record', 'change-result', 'remove-record'],
  setup(props, { emit }) {
    const editing = ref(false);
    const draft = ref('');
    const error = ref('');
    function startEdit() { draft.value = props.row.equipment; error.value = ''; editing.value = true; }
    function save() {
      try {
        const equipment = validateEquipment(draft.value);
        error.value = '';
        emit('rename-record', { id: props.row.id, equipment });
        editing.value = false;
      } catch (e) { error.value = e.message; }
    }
    function toggle() {
      emit('change-result', { id: props.row.id, result: props.row.result === '正常' ? '異常' : '正常' });
    }
    return { editing, draft, error, startEdit, save, toggle };
  },
  template: `<li class="record" :data-id="row.id">
    <div class="record-heading"><strong class="equipment-name">{{ row.equipment }}</strong>
    <span class="badge" :class="{ abnormal: row.result === '異常' }">{{ row.result }}</span></div>
    <p class="muted record-id">識別碼 {{ row.id }}</p>
    <form v-if="editing" @submit.prevent="save" novalidate class="edit-form">
      <label :for="'edit-' + row.id">修改設備名稱</label>
      <input :id="'edit-' + row.id" v-model="draft" maxlength="80" :aria-describedby="'error-' + row.id">
      <p class="error" :id="'error-' + row.id" role="status">{{ error }}</p>
      <div class="actions"><button type="submit">儲存修改</button>
      <button type="button" class="secondary" @click="editing = false">取消編輯</button></div>
    </form>
    <div class="actions"><button type="button" class="secondary edit-button" @click="startEdit">編輯名稱</button>
    <button type="button" class="secondary toggle-button" @click="toggle">{{ row.result === '正常' ? '改為異常' : '改為正常' }}</button>
    <button type="button" class="secondary remove-button" @click="$emit('remove-record', row.id)">刪除</button></div>
  </li>`
};
