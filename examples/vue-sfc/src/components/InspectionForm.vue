<script setup>
import { ref } from 'vue';
import { validateEquipment } from '../model.js';
const emit = defineEmits(['add-record']);
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
</script>

<template>
<form id="add-form" @submit.prevent="submit" novalidate>
    <label for="equipment">設備名稱</label>
    <input id="equipment" v-model="equipment" maxlength="80" autocomplete="off" aria-describedby="draft-note form-error">
    <label for="result">巡檢結果</label>
    <select id="result" v-model="result"><option>正常</option><option>異常</option></select>
    <p id="draft-note" class="muted">輸入是表單自己的草稿，按新增才會更新主清單。送出後保留草稿，請先確認下方訊息。</p>
    <p id="form-error" class="error" role="status">{{ error }}</p>
    <button type="submit">新增巡檢</button>
  </form>
</template>
