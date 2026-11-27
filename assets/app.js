'use strict';
(() => {
  const data = JSON.parse(document.getElementById('course-data').textContent);
  const key = 'web-learning-progress-v1';
  const validKeys = new Set(data.stages.flatMap(s => s.checks.map((_, i) => `${s.id}-${i}`)));
  const status = document.getElementById('storage-status');
  const track = document.getElementById('track');
  let state = { track: 'B', checks: {} };
  const validate = value => {
    if (!value || typeof value !== 'object' || !data.tracks[value.track] || !value.checks || typeof value.checks !== 'object' || Array.isArray(value.checks)) throw new Error('進度檔格式不符');
    const checks = {};
    for (const [k, v] of Object.entries(value.checks)) {
      if (!validKeys.has(k) || typeof v !== 'boolean') throw new Error('進度檔含未知項目');
      checks[k] = v;
    }
    return { track: value.track, checks };
  };
  try { const saved = localStorage.getItem(key); if (saved) state = validate(JSON.parse(saved)); }
  catch { status.textContent = '無法讀取已存進度，本次從空白開始。仍可操作並匯出備份。'; }
  const save = () => {
    try { localStorage.setItem(key, JSON.stringify(state)); status.textContent = '進度已儲存在此瀏覽器。'; }
    catch { status.textContent = '瀏覽器無法保存進度，請使用匯出備份。'; }
  };
  const update = () => {
    track.value = state.track;
    const path = data.tracks[state.track];
    document.getElementById('track-description').textContent = path.description;
    document.querySelectorAll('[data-stage]').forEach(el => { el.hidden = !path.stages.includes(Number(el.dataset.stage)); });
    document.querySelectorAll('[data-nav]').forEach(el => { el.hidden = !path.stages.includes(Number(el.dataset.nav)); });
    document.querySelectorAll('[data-check]').forEach(el => { el.checked = Boolean(state.checks[el.dataset.check]); });
    const visible = data.stages.filter(s => path.stages.includes(s.id));
    const keys = visible.flatMap(s => s.checks.map((_, i) => `${s.id}-${i}`));
    const done = keys.filter(k => state.checks[k]).length;
    const finished = visible.filter(s => s.checks.every((_, i) => state.checks[`${s.id}-${i}`])).length;
    const progress = document.getElementById('progress');
    progress.max = keys.length; progress.value = done;
    progress.textContent = `${Math.round(done / keys.length * 100)}%`;
    document.getElementById('progress-text').textContent = `${done} / ${keys.length} 項驗收`;
    document.getElementById('stage-text').textContent = `${finished} / ${visible.length} 階段完成`;
  };
  track.addEventListener('change', () => { state.track = track.value; save(); update(); });
  document.querySelectorAll('[data-check]').forEach(el => el.addEventListener('change', () => { state.checks[el.dataset.check] = el.checked; save(); update(); }));
  document.querySelectorAll('[data-quiz]').forEach(form => form.addEventListener('submit', event => {
    event.preventDefault();
    const answer = new FormData(form).get(`q${form.dataset.quiz}`);
    const quiz = data.stages.find(s => s.id === Number(form.dataset.quiz)).quiz;
    form.querySelector('.feedback').textContent = answer === null ? '請先選擇一個答案。' : `${Number(answer) === quiz.answer ? '答對了。' : '再想一想。'}${quiz.explanation}`;
  }));
  document.querySelectorAll('.copy').forEach(button => button.addEventListener('click', async () => {
    try { await navigator.clipboard.writeText(button.closest('.code-head').nextElementSibling.textContent); button.textContent = '已複製'; }
    catch { button.textContent = '請選取下方程式碼複製'; }
  }));
  const download = (name, value) => {
    const url = URL.createObjectURL(new Blob([JSON.stringify(value, null, 2)], { type: 'application/json' }));
    const a = document.createElement('a'); a.href = url; a.download = name; a.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  };
  document.getElementById('export').addEventListener('click', () => download('web-learning-progress.json', { version: 1, ...state }));
  document.getElementById('import').addEventListener('change', async event => {
    const file = event.target.files[0]; if (!file) return;
    try {
      if (file.size > 100000) throw new Error('進度檔過大');
      const value = JSON.parse(await file.text());
      if (value.version !== 1) throw new Error('不支援此進度檔版本');
      const imported = validate(value);
      if (confirm('以匯入檔取代目前驗收進度？可先取消並匯出備份。')) { state = imported; save(); update(); }
    } catch (error) { status.textContent = `匯入失敗：${error.message}。原進度保留。`; }
    event.target.value = '';
  });
  document.getElementById('reset').addEventListener('click', () => {
    if (!confirm('清除所有路線的驗收勾選？可先取消並匯出備份。')) return;
    state.checks = {}; save(); update();
  });
  // A shared stage remains available when following a deep link from a different track.
  const revealHash = () => {
    const target = document.getElementById(location.hash.slice(1));
    if (target?.matches('[data-stage]') && target.hidden) { state.track = 'B'; update(); save(); target.scrollIntoView(); }
  };
  update(); revealHash(); window.addEventListener('hashchange', revealHash);
})();
