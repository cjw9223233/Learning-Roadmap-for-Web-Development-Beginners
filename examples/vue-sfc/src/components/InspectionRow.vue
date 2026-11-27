<script setup>
import { ref } from 'vue';
import { validateEquipment } from '../model.js';
const props = defineProps({ row: { type: Object, required: true } });
const emit = defineEmits(['rename-record', 'change-result', 'remove-record']);
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
</script>

<template>
<li class="record" :data-id="row.id">
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
  </li>
</template>
