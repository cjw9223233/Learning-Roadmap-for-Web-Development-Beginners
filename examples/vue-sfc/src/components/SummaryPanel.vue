<script setup>
defineProps({ title: { type: String, required: true }, counts: { type: Object, required: true } });
</script>

<template>
<section class="summary-panel" :aria-label="title">
    <h3>{{ title }}</h3><dl class="stats">
    <div><dt>總數</dt><dd class="total">{{ counts.total }}</dd></div>
    <div><dt>正常</dt><dd class="normal">{{ counts.normal }}</dd></div>
    <div><dt>異常</dt><dd class="abnormal">{{ counts.abnormal }}</dd></div>
    </dl></section>
</template>

<style scoped>
.summary-panel h3 { border-bottom: 2px solid #d5ddd3; padding-bottom: 8px; }
</style>
