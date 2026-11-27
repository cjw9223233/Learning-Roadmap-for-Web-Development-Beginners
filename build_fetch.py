"""Build the Fetch lesson in HTML and Markdown from a common source."""
import json
from html import escape


def build_fetch(root):
    d = json.loads((root / 'lessons/02b-fetch.json').read_text(encoding='utf-8'))
    js = (root / 'examples/fetch-lab/app.js').read_text(encoding='utf-8')
    codes = {
        'server': ('powershell', 'python examples/fetch-lab/server.py\n# 如需改連接埠\npython examples/fetch-lab/server.py --port 8766\n# 在執行中的終端機按 Ctrl+C 結束，不要同時執行兩個相同連接埠的服務。'),
        'await': ('javascript', 'const response = await fetch(url, { signal: controller.signal });\nconst text = await response.text();\n// 之後仍需解析、驗證，並確認本次請求仍為最新。'),
        'http': ('javascript', "if (!response.ok) {\n  throw new LoadError('http', `HTTP ${response.status}`);\n}"),
        'parse': ('javascript', js[js.index('function parsePayload'):js.index('function renderRows')].strip()),
        'timeout': ('javascript', "job.timer = setTimeout(() => {\n  if (active === job && !job.controller.signal.aborted) {\n    job.reason = 'timeout';\n    job.controller.abort();\n  }\n}, timeout);\n// 計時器保留至本文與驗證完成，在 finally 清除。"),
        'cancel': ('javascript', "if (active && !active.controller.signal.aborted) {\n  active.reason = 'user';\n  active.controller.abort();\n}"),
        'latest': ('javascript', 'const response = await fetch(url, options);\nif (active !== job) return;\nconst text = await response.text();\nif (active !== job) return;\n// catch 與 finally 也必須檢查是否仍是本次 job。')
    }
    ul = lambda items: '<ul>' + ''.join('<li>' + escape(s) + '</li>' for s in items) + '</ul>'
    md = ['# ' + d['title'], '', '更新：' + d['date'], '', d['intro'], '', '## 準備', ''] + ['- ' + s for s in d['materials']]
    md += ['', '[開啟 Fetch 練習頁](../examples/fetch-lab/index.html)', '', '程式片段需配合完整 app.js 的上下文閱讀，不是每段都能獨立執行。', '']
    steps = []
    for s in d['steps']:
        md += ['## ' + s['title'], '', s['text'], '', '**預期觀察：** ' + s['expected'], '']
        snippet = ''
        if s.get('code'):
            language, text = codes[s['code']]
            md += ['```' + language, text, '```', '']
            snippet = '<p class="muted">重點片段，請配合完整程式的上下文閱讀。</p><pre><code>' + escape(text) + '</code></pre>'
        steps.append('<section class="stage"><h2>' + escape(s['title']) + '</h2><p>' + escape(s['text']) + '</p><aside class="note"><strong>預期觀察</strong><p>' + escape(s['expected']) + '</p></aside>' + snippet + '</section>')
    md += ['## 自己動手驗證', '']
    exercises = []
    for e in d['exercises']:
        md += ['### ' + e['title'], '', e['task'], '', '**參考解答：** ' + e['answer'], '']
        exercises.append('<h3>' + escape(e['title']) + '</h3><p>' + escape(e['task']) + '</p><details><summary>完成操作後看解答</summary><p>' + escape(e['answer']) + '</p></details>')
    md += ['## 完成檢核', ''] + ['- [ ] ' + s for s in d['checks']]
    md += ['', '本課不自動勾選主教材進度。npm 與 TypeScript 尚待後續逐步練習。', '', '## 來源與範圍', '', '核對日期：' + d['date'] + '。教學情境、資料契約與狀態處理是本教材設計。', '']
    md += [f"- [{s['title']}]({s['url']})：{s['note']}" for s in d['sources']]
    (root / 'lessons/02b-fetch.md').write_text('\n'.join(md) + '\n', encoding='utf-8')
    refs = ''.join(f'<li><a href="{escape(s["url"], quote=True)}">{escape(s["title"])}</a>：{escape(s["note"])}</li>' for s in d['sources'])
    html = f'''<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(d['title'])}</title><link rel="stylesheet" href="../assets/style.css"><style>main{{margin:0 auto;max-width:1000px}}pre{{white-space:pre-wrap;overflow-wrap:anywhere}}</style></head><body><a class="skip" href="#lesson">跳到課程內容</a><main id="lesson"><a href="../index.html#stage-2">← 回到主教材第 2 階段</a><header class="hero"><p class="eyebrow">GUIDED PRACTICE / 02 B</p><h1>等到資料，<br>也要等對那次資料。</h1><p>{escape(d['intro'])}</p><p class="muted">更新：{d['date']} · 八個步驟 · 三個驗證練習</p></header><section class="dashboard"><h2>準備與操作入口</h2>{ul(d['materials'])}<p><a href="../examples/fetch-lab/index.html">開啟 Fetch 練習頁 →</a> · <a href="02b-fetch.md">閱讀 Markdown →</a></p></section>{''.join(steps)}<section class="stage"><h2>自己動手驗證</h2>{''.join(exercises)}</section><section class="stage"><h2>完成檢核</h2>{ul(d['checks'])}<p>本課不自動勾選主教材進度。npm 與 TypeScript 尚待後續逐步練習。</p></section><section class="stage"><h2>來源與核對範圍</h2><p>核對日期：{d['date']}。教學情境、資料契約與狀態處理為本教材設計。</p><ul>{refs}</ul></section><footer><a href="02-json-storage.html">回顧 JSON 與保存</a> · <a href="../index.html#stage-2">回到主教材</a></footer></main></body></html>'''
    (root / 'lessons/02b-fetch.html').write_text(html, encoding='utf-8')
