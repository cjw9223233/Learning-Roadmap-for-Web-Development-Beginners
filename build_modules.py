"""Generate the modules/npm reading lesson from its data and runnable files."""
import json
from html import escape


def build_modules(root):
    d = json.loads((root / 'lessons/02c-modules-npm.json').read_text(encoding='utf-8'))
    project = root / 'examples/modules-npm'
    rules = (project / 'inspection.js').read_text(encoding='utf-8')
    codes = {
        'exports': ('javascript', rules[rules.index('export function summarize'):].strip()),
        'imports': ('javascript', (project / 'cli.js').read_text(encoding='utf-8').strip()),
        'browser': ('html', '<script type="module" src="app.js"></script>'),
        'package': ('json', (project / 'package.json').read_text(encoding='utf-8').strip()),
        'tests': ('powershell', 'npm test\n# Windows PowerShell 如擋住 npm.ps1，可改用\nnpm.cmd test'),
        'ci': ('powershell', '# 只在自己的範例副本執行，先確認目前資料夾\nnode --version\nnpm --version\nnpm ci --ignore-scripts --offline --audit=false --fund=false\n# 本命令略過安裝生命週期 scripts；npm test 是之後明確執行的另一個命令。')
    }
    ul = lambda items: '<ul>' + ''.join('<li>' + escape(x) + '</li>' for x in items) + '</ul>'
    md = ['# ' + d['title'], '', '更新：' + d['date'], '', d['intro'], '', '## 準備', ''] + ['- ' + m for m in d['materials']]
    md += ['', '[範例頁面](../examples/modules-npm/index.html)；模組互動需先在範例副本執行 npm run serve。', '']
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
        exercises.append('<h3>' + escape(e['title']) + '</h3><p>' + escape(e['task']) + '</p><details><summary>完成操作後看解答</summary><p>' + escape(e['answer']) + '</p></details>')
    md += ['## 完成檢核', ''] + ['- [ ] ' + c for c in d['checks']]
    md += ['', '本課不自動修改主教材進度。TypeScript、外部套件評估與完整建置流程仍需後續練習。', '', '## 來源與核對範圍', '', '核對日期：' + d['date'] + '。專案、資料規則與練習安排為本教材設計。', '']
    md += [f"- [{s['title']}]({s['url']})：{s['note']}" for s in d['sources']]
    (root / 'lessons/02c-modules-npm.md').write_text('\n'.join(md) + '\n', encoding='utf-8')
    refs = ''.join(f'<li><a href="{escape(s["url"], quote=True)}">{escape(s["title"])}</a>：{escape(s["note"])}</li>' for s in d['sources'])
    html = f'''<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(d['title'])}</title><link rel="stylesheet" href="../assets/style.css"><style>main{{margin:0 auto;max-width:1000px}}pre{{white-space:pre-wrap;overflow-wrap:anywhere}}</style></head><body><a class="skip" href="#lesson">跳到課程內容</a><main id="lesson"><a href="../index.html#stage-2">← 回到主教材第 2 階段</a><header class="hero"><p class="eyebrow">GUIDED PRACTICE / 02 C</p><h1>把規則拆開，<br>讓不同入口共用。</h1><p>{escape(d['intro'])}</p><p class="muted">更新：{d['date']} · 八個步驟 · 三個修改練習</p></header><section class="dashboard"><h2>準備與範例入口</h2>{ul(d['materials'])}<p><a href="../examples/modules-npm/index.html">查看模組範例頁 →</a> · <a href="02c-modules-npm.md">閱讀 Markdown →</a></p><p>先在自己的範例副本執行 npm run serve，從印出的 HTTP 網址操作；命令列 demo 與測試則直接在終端機執行。</p></section>{''.join(steps)}<section class="stage"><h2>自己動手修改</h2>{''.join(exercises)}</section><section class="stage"><h2>完成檢核</h2>{ul(d['checks'])}<p>本課不自動修改主教材進度。TypeScript、外部套件評估與完整建置流程仍需後續練習。</p></section><section class="stage"><h2>來源與核對範圍</h2><p>核對日期：{d['date']}。專案、資料規則與練習安排是本教材設計。</p><ul>{refs}</ul></section><footer><a href="02b-fetch.html">複習 Fetch</a> · <a href="../index.html#stage-2">回到主教材</a></footer></main></body></html>'''
    (root / 'lessons/02c-modules-npm.html').write_text(html, encoding='utf-8')
