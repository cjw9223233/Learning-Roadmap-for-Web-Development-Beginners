from build_sfc import build_sfc
from build_vue import build_vue
from build_typescript import build_typescript
"""Generate the guided lesson in Markdown and HTML from one source."""
import json
from html import escape
from build_stage1 import build_stage1
from build_stage2 import build_stage2
from build_fetch import build_fetch
from build_modules import build_modules


def build_lessons(root):
    lesson = json.loads((root / 'lessons/00-first-web.json').read_text(encoding='utf-8'))
    md = [f"# {lesson['title']}", '', f"更新：{lesson['version']}", '', lesson['intro'], '', '## 準備', '']
    md += ['- ' + item for item in lesson['materials']]
    md += ['', '起始頁：[first-page.html](../examples/first-page.html)｜離線模擬器：[http-lab.html](../examples/http-lab.html)', '', '## 逐步操作', '']
    steps_html = []
    for i, step in enumerate(lesson['steps']):
        md += [f"### {step['title']}", '', step['text'], '', '**預期觀察：** ' + step['expected'], '']
        code_html = ''
        if i == 0:
            md += ['```html', lesson['starter'], '```', '']
            code_html = '<pre><code>' + escape(lesson['starter']) + '</code></pre>'
        steps_html.append('<section class="stage"><h2>' + escape(step['title']) + '</h2><p>' + escape(step['text']) + '</p>' + code_html + '<aside class="note"><strong>預期觀察</strong><p>' + escape(step['expected']) + '</p></aside></section>')
    md += ['## HTTP 模擬器的七個任務', '', '先預測再送出。模型狀態只保存在當頁記憶體；重新整理會回到一筆起始資料。真實服務的狀態碼及驗證契約可能不同。', '']
    missions_html = []
    for i, mission in enumerate(lesson['missions'], 1):
        md += [f"### 任務 {i}｜{mission['title']}", '', mission['action'], '', '**參考解答：** ' + mission['answer'], '']
        missions_html.append('<section><h3>任務 ' + str(i) + '｜' + escape(mission['title']) + '</h3><p>' + escape(mission['action']) + '</p><details><summary>完成操作後看解答</summary><p>' + escape(mission['answer']) + '</p></details></section>')
    md += ['## 排除卡點', '', '| 現象 | 檢查方式 |', '| --- | --- |']
    md += ['| ' + title + ' | ' + description + ' |' for title, description in lesson['troubleshooting']]
    md += ['', '## 完成檢核', ''] + ['- [ ] ' + c for c in lesson['checks']]
    md += ['', '完成實作後，可回到主教材第 0 階段勾選原有驗收。此延伸課程不會自動修改主教材進度。', '', '## 實作紀錄', ''] + ['- ' + r for r in lesson['reflection']]
    md += ['', '## 來源與範圍', '', '核對日期：2026-11-18。操作步驟、七個任務及模擬 API 契約為本教材設計。', '']
    md += [f"- [{s['title']}]({s['url']})：{s['note']}" for s in lesson['sources']]
    (root / 'lessons/00-first-web.md').write_text('\n'.join(md) + '\n', encoding='utf-8')
    ul = lambda items: '<ul>' + ''.join('<li>' + escape(s) + '</li>' for s in items) + '</ul>'
    troubleshooting = ''.join('<h3>' + escape(t) + '</h3><p>' + escape(p) + '</p>' for t, p in lesson['troubleshooting'])
    sources = ''.join(f'<li><a href="{escape(s["url"], quote=True)}">{escape(s["title"])}</a>：{escape(s["note"])}</li>' for s in lesson['sources'])
    html = f'''<!doctype html>
<html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(lesson['title'])}</title><link rel="stylesheet" href="../assets/style.css"><style>main{{margin:0 auto;max-width:980px}}.lesson-actions{{display:flex;gap:20px;flex-wrap:wrap}}.lesson-actions a{{padding:10px 0}}</style></head>
<body><a class="skip" href="#lesson">跳到練習內容</a><main id="lesson"><a href="../index.html#stage-0">← 回到主教材第 0 階段</a><header class="hero"><p class="eyebrow">GUIDED PRACTICE / 00</p><h1>從本機檔案，<br>看懂一次 HTTP 往返。</h1><p>{escape(lesson['intro'])}</p><p class="muted">更新：{lesson['version']} · 離線可讀 · 依操作與理解調整進度</p></header>
<section class="dashboard"><h2>準備好就開始</h2>{ul(lesson['materials'])}<div class="lesson-actions"><a href="../examples/first-page.html">開啟起始頁 ↗</a><a href="../examples/first-page.html" download="index.html">下載起始 HTML</a><a href="../examples/http-lab.html">開啟 HTTP 模擬器 ↗</a><a href="00-first-web.md">閱讀 Markdown</a></div></section>
{''.join(steps_html)}<section class="stage"><h2>HTTP 模擬器的七個任務</h2><p>先預測，再送出。模型資料只保存在當頁記憶體，重新整理回到一筆起始資料。真實服務的狀態碼與驗證契約可能不同。</p><a href="../examples/http-lab.html">開始操作模擬器 →</a>{''.join(missions_html)}</section>
<section class="stage"><h2>遇到卡點先檢查</h2>{troubleshooting}</section><section class="stage"><h2>完成檢核</h2>{ul(lesson['checks'])}<p>完成實作後，再回到主教材第 0 階段勾選原有驗收。本頁不會自動修改進度。</p><h3>留下自己的實作紀錄</h3>{ul(lesson['reflection'])}</section>
<section class="stage"><h2>來源與核對範圍</h2><p>核對日期：2026-11-18。操作步驟、七個任務與模擬 API 契約為本教材的教學設計。</p><ul>{sources}</ul></section><footer><a href="../index.html#stage-0">回到主教材 →</a></footer></main></body></html>'''
    (root / 'lessons/00-first-web.html').write_text(html, encoding='utf-8')
    (root / 'examples/first-page.html').write_text(lesson['starter'] + '\n', encoding='utf-8')
    build_stage1(root)
    build_stage2(root)
    build_fetch(root)
    build_modules(root)
    build_typescript(root)
    build_vue(root)
    build_sfc(root)
