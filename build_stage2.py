"""Generate stage-2A reading formats; the runnable app is maintained directly."""
import json
from html import escape


def build_stage2(root):
    d = json.loads((root / 'lessons/02-json-storage.json').read_text(encoding='utf-8'))
    js = (root / 'examples/json-storage/app.js').read_text(encoding='utf-8')
    sample = (root / 'examples/json-storage/samples/valid.json').read_text(encoding='utf-8')
    codes = {
        'json': ('javascript', 'const text = JSON.stringify({ version: 1, rows: [] });\nconst value = JSON.parse(text);\nconsole.log(typeof text);  // string\nconsole.log(value.rows);   // []'),
        'storage': ('javascript', "// 以下是流程片段，須配合完整程式的 try/catch\nlocalStorage.setItem(storageKey, asJSON());\nconst raw = localStorage.getItem(storageKey);\nconst loaded = raw === null ? [] : parseBackup(raw);"),
        'file': ('javascript', 'const text = await file.text();\n// 讀取成功只填入文字區，不立刻取代 rows。\ndocument.getElementById(\'json-input\').value = text;'),
        'validate': ('javascript', js[js.index('function parseBackup'):js.index('function makeBackup')].strip()),
        'corrupt': ('javascript', "// 先匯出本練習備份；只在本練習頁操作。\nlocalStorage.setItem('web-storage-lab-v1', '{');\n// 再用瀏覽器重新整理，觀察保存鎖定與原值保留。"),
        'failure': ('javascript', "try {\n  localStorage.setItem(storageKey, asJSON());\n  // 只有成功後才將 dirty 設為 false。\n} catch (error) {\n  // 保留 rows，提示使用者改用 JSON 檔案備份。\n  console.error(error.name);\n}")
    }
    md = ['# ' + d['title'], '', '更新：' + d['date'], '', d['intro'], '', '## 準備', '']
    md += ['- ' + text for text in d['materials']]
    md += ['', '[開啟保存與備份練習](../examples/json-storage/index.html)', '', '## 本課的備份格式', '', '```json', sample.strip(), '```', '', '版本、最多 200 筆、128 KiB 與欄位規則是本課練習的資料契約，不是瀏覽器通用規範。', '']
    steps = []
    for step in d['steps']:
        md += ['## ' + step['title'], '', step['text'], '', '**預期觀察：** ' + step['expected'], '']
        code_html = ''
        if step.get('code'):
            lang, text = codes[step['code']]
            md += ['```' + lang, text, '```', '']
            code_html = '<p class="muted">重點片段，請配合完整範例與指定位置閱讀。</p><pre><code>' + escape(text) + '</code></pre>'
        steps.append('<section class="stage"><h2>' + escape(step['title']) + '</h2><p>' + escape(step['text']) + '</p><aside class="note"><strong>預期觀察</strong><p>' + escape(step['expected']) + '</p></aside>' + code_html + '</section>')
    exercises = []
    md += ['## 自己動手驗證', '']
    for e in d['exercises']:
        md += ['### ' + e['title'], '', e['task'], '', '**參考解答：** ' + e['answer'], '']
        exercises.append('<h3>' + escape(e['title']) + '</h3><p>' + escape(e['task']) + '</p><details><summary>完成操作後看解答</summary><p>' + escape(e['answer']) + '</p></details>')
    md += ['## 完成檢核', ''] + ['- [ ] ' + c for c in d['checks']]
    md += ['', '本課不自動勾選主教材驗收。Fetch 可接續[第 2 階段 B](02b-fetch.html)；npm 與 TypeScript 尚待後續練習。完成本課不代表整個第 2 階段已完成。', '', '## 來源與範圍', '', '核對日期：' + d['date'] + '。操作順序、範例與資料契約為本教材設計。', '']
    md += [f"- [{s['title']}]({s['url']})：{s['note']}" for s in d['sources']]
    (root / 'lessons/02-json-storage.md').write_text('\n'.join(md) + '\n', encoding='utf-8')
    ul = lambda items: '<ul>' + ''.join('<li>' + escape(s) + '</li>' for s in items) + '</ul>'
    refs = ''.join(f'<li><a href="{escape(s["url"], quote=True)}">{escape(s["title"])}</a>：{escape(s["note"])}</li>' for s in d['sources'])
    html = f'''<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(d['title'])}</title><link rel="stylesheet" href="../assets/style.css"><style>main{{margin:0 auto;max-width:1000px}}pre{{white-space:pre-wrap;overflow-wrap:anywhere}}.links{{display:flex;gap:20px;flex-wrap:wrap}}</style></head><body><a class="skip" href="#lesson">跳到課程內容</a><main id="lesson"><a href="../index.html#stage-2">← 回到主教材第 2 階段</a><header class="hero"><p class="eyebrow">GUIDED PRACTICE / 02 A</p><h1>讓資料留下來，<br>也讓備份還原得回來。</h1><p>{escape(d['intro'])}</p><p class="muted">更新：{d['date']} · 八個步驟 · 三個驗證練習</p></header><section class="dashboard"><h2>準備與練習入口</h2>{ul(d['materials'])}<div class="links"><a href="../examples/json-storage/index.html">開啟保存與備份練習 →</a><a href="02-json-storage.md">閱讀 Markdown →</a></div></section><section class="stage"><h2>本課的備份格式</h2><pre><code>{escape(sample.strip())}</code></pre><p>版本、最多 200 筆、128 KiB 與欄位規則是本課的資料契約，不是瀏覽器通用規範。</p></section>{''.join(steps)}<section class="stage"><h2>自己動手驗證</h2>{''.join(exercises)}</section><section class="stage"><h2>完成檢核</h2>{ul(d['checks'])}<p>本課不自動勾選主教材驗收。Fetch 可接續<a href="02b-fetch.html">第 2 階段 B</a>；npm 與 TypeScript 尚待後續練習。完成本課不代表整個第 2 階段已完成。</p></section><section class="stage"><h2>來源與核對範圍</h2><p>核對日期：{d['date']}。操作順序、範例及資料契約為本教材設計。</p><ul>{refs}</ul></section><footer><a href="01-form-dom.html">複習第 1 階段</a> · <a href="../index.html#stage-2">回到主教材</a></footer></main></body></html>'''
    (root / 'lessons/02-json-storage.html').write_text(html, encoding='utf-8')
