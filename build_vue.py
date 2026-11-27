"""Generate the Vue component reading lesson from its data and runnable files."""
import json
from html import escape


def build_vue(root):
    d = json.loads((root / 'lessons/03a-vue-components.json').read_text(encoding='utf-8'))
    project = root / 'examples/vue-components'
    components = (project / 'components.js').read_text(encoding='utf-8')
    app = (project / 'app.js').read_text(encoding='utf-8')
    model = (project / 'model.js').read_text(encoding='utf-8')
    codes = {
        'start': ('powershell', 'npm test\nnpm run serve\n# 不需 npm install 或 build；從印出的 HTTP 網址開啟。'),
        'tree': ('text', 'App（主清單、篩選、順序）\n├─ InspectionForm（新增草稿）\n├─ SummaryPanel × 2（接收不同統計）\n└─ InspectionRow × N（每列自己的編輯草稿）'),
        'state': ('javascript', app[app.index('    const rows'):app.index('    function update')].strip()),
        'props': ('javascript', components[components.index('export const SummaryPanel'):components.index('export const InspectionForm')].strip()),
        'events': ('javascript', components[components.index('export const InspectionForm'):components.index('  template: `<form')].strip() + '\n  // 省略下方模板；完整程式見 components.js\n};'),
        'list': ('html', '<inspection-row v-for="row in visible" :key="row.id" :row="row"\n  @rename-record="rename" @change-result="toggle"\n  @remove-record="remove"></inspection-row>'),
        'boundary': ('javascript', model[model.index('export function validateEquipment'):model.index('export function renameRecord')].strip()),
        'test': ('powershell', 'npm test\n# 10 個模型測試；另需在瀏覽器驗證元件操作與接線。')
    }
    ul = lambda items: '<ul>' + ''.join('<li>' + escape(x) + '</li>' for x in items) + '</ul>'
    md = ['# ' + d['title'], '', '更新：' + d['date'], '', d['intro'], '', '## 準備', ''] + ['- ' + m for m in d['materials']]
    md += ['', '[範例頁面](../examples/vue-components/index.html)；模組互動需先在範例副本執行 npm run serve。', '']
    steps = []
    for s in d['steps']:
        md += ['## ' + s['title'], '', s['text'], '', '**預期觀察：** ' + s['expected'], '']
        code = ''
        if s.get('code'):
            lang, text = codes[s['code']]
            md += ['```' + lang, text, '```', '']
            code = '<pre><code>' + escape(text) + '</code></pre>'
        steps.append('<section class="stage"><h2>' + escape(s['title']) + '</h2><p>' + escape(s['text']) + '</p><aside class="note"><strong>預期觀察</strong><p>' + escape(s['expected']) + '</p></aside>' + code + '</section>')
    exercises = []
    md += ['## 自己動手修改', '']
    for e in d['exercises']:
        md += ['### ' + e['title'], '', e['task'], '', '**參考解答：** ' + e['answer'], '']
        solution = ''
        for lang in ['javascript', 'html']:
            if e.get(lang):
                md += ['```' + lang, e[lang], '```', '']
                solution += '<pre><code>' + escape(e[lang]) + '</code></pre>'
        exercises.append('<h3>' + escape(e['title']) + '</h3><p>' + escape(e['task']) + '</p><details><summary>完成操作後看解答</summary><p>' + escape(e['answer']) + '</p>' + solution + '</details>')
    md += ['## 完成檢核', ''] + ['- [ ] ' + c for c in d['checks']]
    md += ['', '本課不自動修改主教材進度。SFC、Router 與工具鏈將在後續課程練習。', '', '## 來源與核對範圍', '', '核對日期：' + d['date'] + '。專案、資料規則與練習安排為本教材設計。', '']
    md += [f"- [{s['title']}]({s['url']})：{s['note']}" for s in d['sources']]
    (root / 'lessons/03a-vue-components.md').write_text('\n'.join(md) + '\n', encoding='utf-8')
    refs = ''.join(f'<li><a href="{escape(s["url"], quote=True)}">{escape(s["title"])}</a>：{escape(s["note"])}</li>' for s in d['sources'])
    html = f'''<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(d['title'])}</title><link rel="stylesheet" href="../assets/style.css"><style>main{{margin:0 auto;max-width:1000px}}pre{{white-space:pre-wrap;overflow-wrap:anywhere}}</style></head><body><a class="skip" href="#lesson">跳到課程內容</a><main id="lesson"><a href="../index.html#stage-3">← 回到主教材第 3 階段</a><header class="hero"><p class="eyebrow">GUIDED PRACTICE / 03 A</p><h1>把畫面拆成元件，<br>看懂資料如何流動。</h1><p>{escape(d['intro'])}</p><p class="muted">更新：{d['date']} · 八個步驟 · 三個修改練習</p></header><section class="dashboard"><h2>準備與範例入口</h2>{ul(d['materials'])}<p><a href="../examples/vue-components/index.html">開啟巡檢元件實驗室 →</a> · <a href="03a-vue-components.md">閱讀 Markdown →</a></p><p>先在自己的範例副本執行 npm run serve，從印出的 HTTP 網址操作；本課免建置且無須安裝套件。</p></section>{''.join(steps)}<section class="stage"><h2>自己動手修改</h2>{''.join(exercises)}</section><section class="stage"><h2>完成檢核</h2>{ul(d['checks'])}<p>本課不自動修改主教材進度。SFC、Router 與工具鏈將在後續課程練習。</p></section><section class="stage"><h2>來源與核對範圍</h2><p>核對日期：{d['date']}。專案、資料規則與練習安排是本教材設計。</p><ul>{refs}</ul></section><footer><a href="02d-typescript.html">複習 TypeScript</a> · <a href="../index.html#stage-3">回到主教材</a></footer></main></body></html>'''
    (root / 'lessons/03a-vue-components.html').write_text(html, encoding='utf-8')
