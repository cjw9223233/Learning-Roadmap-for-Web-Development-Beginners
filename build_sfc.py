"""Generate the Vue component reading lesson from its data and runnable files."""
import json
from html import escape


def build_sfc(root):
    d = json.loads((root / 'lessons/03b-vue-sfc.json').read_text(encoding='utf-8'))
    project = root / 'examples/vue-sfc'
    codes = {
        'commands': ('powershell', 'node --version\nnpm ci --ignore-scripts --audit=false --fund=false\nnpm test\nnpm run dev\n# 結束 dev 後，或另開終端機：\nnpm run build\nnpm run preview'),
        'summary': ('vue', (project / 'src/components/SummaryPanel.vue').read_text(encoding='utf-8').strip()),
        'form': ('vue', (project / 'src/components/InspectionForm.vue').read_text(encoding='utf-8').split('</script>')[0].strip() + '\n</script>'),
        'entry': ('javascript', (project / 'src/main.js').read_text(encoding='utf-8').strip()),
        'config': ('javascript', (project / 'vite.config.js').read_text(encoding='utf-8').strip()),
        'checks': ('powershell', 'npm test\nnpm run build\nnpm run preview\n# preview 後仍需實際驗證操作；不自動部署。')
    }
    ul = lambda items: '<ul>' + ''.join('<li>' + escape(x) + '</li>' for x in items) + '</ul>'
    md = ['# ' + d['title'], '', '更新：' + d['date'], '', d['intro'], '', '## 準備', ''] + ['- ' + m for m in d['materials']]
    md += ['', '[隨附建置頁面](../examples/vue-sfc/dist/index.html)；模組互動需先在範例副本依課程啟動 dev 或 preview。', '']
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
    md += ['', '本課不自動修改主教材進度。Router、TypeScript 與較完整的管理流程將在後續練習。', '', '## 來源與核對範圍', '', '核對日期：' + d['date'] + '。專案、資料規則與練習安排為本教材設計。', '']
    md += [f"- [{s['title']}]({s['url']})：{s['note']}" for s in d['sources']]
    (root / 'lessons/03b-vue-sfc.md').write_text('\n'.join(md) + '\n', encoding='utf-8')
    refs = ''.join(f'<li><a href="{escape(s["url"], quote=True)}">{escape(s["title"])}</a>：{escape(s["note"])}</li>' for s in d['sources'])
    html = f'''<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(d['title'])}</title><link rel="stylesheet" href="../assets/style.css"><style>main{{margin:0 auto;max-width:1000px}}pre{{white-space:pre-wrap;overflow-wrap:anywhere}}</style></head><body><a class="skip" href="#lesson">跳到課程內容</a><main id="lesson"><a href="../index.html#stage-3">← 回到主教材第 3 階段</a><header class="hero"><p class="eyebrow">GUIDED PRACTICE / 03 B</p><h1>從 .vue 原始碼，<br>走到真正的建置產物。</h1><p>{escape(d['intro'])}</p><p class="muted">更新：{d['date']} · 八個步驟 · 三個修改練習</p></header><section class="dashboard"><h2>準備與範例入口</h2>{ul(d['materials'])}<p><a href="../examples/vue-sfc/dist/index.html">查看隨附建置頁面 →</a> · <a href="03b-vue-sfc.md">閱讀 Markdown →</a></p><p>先在自己的範例副本依課程啟動 dev 或 preview，從印出的 HTTP 網址操作；本課開發與建置需先安裝鎖定依賴；隨附產物可用 node serve-dist.js 讀取。</p></section>{''.join(steps)}<section class="stage"><h2>自己動手修改</h2>{''.join(exercises)}</section><section class="stage"><h2>完成檢核</h2>{ul(d['checks'])}<p>本課不自動修改主教材進度。Router、TypeScript 與較完整的管理流程將在後續練習。</p></section><section class="stage"><h2>來源與核對範圍</h2><p>核對日期：{d['date']}。專案、資料規則與練習安排是本教材設計。</p><ul>{refs}</ul></section><footer><a href="03a-vue-components.html">複習元件資料流</a> · <a href="../index.html#stage-3">回到主教材</a></footer></main></body></html>'''
    (root / 'lessons/03b-vue-sfc.html').write_text(html, encoding='utf-8')
