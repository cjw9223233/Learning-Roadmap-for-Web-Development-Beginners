"""Build the stage-1 reading lesson and progressive runnable examples."""
import json
from html import escape


def replace_once(text, old, new):
    if text.count(old) != 1:
        raise ValueError('Stage-1 source marker changed: ' + old[:60])
    return text.replace(old, new, 1)


def build_stage1(root):
    lesson = json.loads((root / 'lessons/01-form-dom.json').read_text(encoding='utf-8'))
    sources = root / 'lessons/snippets'
    template = (sources / '01-form.html').read_text(encoding='utf-8')
    css = (sources / '01-form.css').read_text(encoding='utf-8')
    js = (sources / '01-form.js').read_text(encoding='utf-8')
    out = root / 'examples/form-dom'
    out.mkdir(parents=True, exist_ok=True)
    (out / 'form.css').write_text(css, encoding='utf-8')
    (out / 'form.js').write_text(js, encoding='utf-8')
    (out / '03-interactive.html').write_text(template, encoding='utf-8')
    styled = replace_once(template, '03 JavaScript 互動：紀錄只在當頁記憶體，重新整理會清空。', '02 加入 CSS：比較版面與間距，這一版尚未接上新增與篩選邏輯。')
    styled = replace_once(styled, '巡檢表單｜03 JavaScript 互動', '巡檢表單｜02 加入 CSS')
    styled = replace_once(styled, 'type="submit"', 'type="button"')
    styled = replace_once(styled, '<select id="filter">', '<select id="filter" disabled>')
    styled = replace_once(styled, '  <script src="form.js"></script>\n', '')
    styled = replace_once(styled, '使用虛構設備練習。此頁沒有後端、登入或本機永久保存；不會傳送表單資料。', '此版只供觀察欄位與排版。新增按鈕尚未接程式；在欄位按 Enter 可能觸發瀏覽器預設送出並重新載入。請只使用虛構資料。')
    (out / '02-styled.html').write_text(styled, encoding='utf-8')
    static = replace_once(styled, '02 加入 CSS：比較版面與間距，這一版尚未接上新增與篩選邏輯。', '01 靜態 HTML：先辨認內容與欄位；新增與篩選尚未接上程式。')
    static = replace_once(static, '巡檢表單｜02 加入 CSS', '巡檢表單｜01 靜態 HTML')
    static = replace_once(static, '  <link rel="stylesheet" href="form.css">\n', '')
    (out / '01-static.html').write_text(static, encoding='utf-8')
    note_html = '        <label for="note">備註（可留白，最多 120 字元）</label>\n        <textarea id="note" name="note" maxlength="120" rows="3"></textarea>\n'
    notes = replace_once(template, '        <button type="submit">', note_html + '        <button type="submit">')
    notes = replace_once(notes, '03 JavaScript 互動：紀錄只在當頁記憶體，重新整理會清空。', '04 備註練習解答：同時連接欄位、資料與呈現，仍只保存於當頁記憶體。')
    notes = replace_once(notes, '巡檢表單｜03 JavaScript 互動', '巡檢表單｜04 備註練習解答')
    notes = replace_once(notes, 'src="form.js"', 'src="form-notes.js"')
    note_declaration = "const noteInput = document.getElementById('note');"
    note_validation = """  const note = noteInput.value.trim();
  if (note.length > 120) {
    message.textContent = '備註最多 120 字元。';
    noteInput.focus();
    return;
  }
  rows.push({ equipment, result, note });"""
    notes_js = replace_once(js, "const filter = document.getElementById('filter');", note_declaration + "\nconst filter = document.getElementById('filter');")
    notes_js = replace_once(notes_js, '  rows.push({ equipment, result });', note_validation)
    notes_render = "    const noteText = row.note ? ` · 備註：${row.note}` : '';\n    item.textContent = `${row.equipment} · ${row.result}${noteText}`;"
    notes_js = replace_once(notes_js, '    item.textContent = `${row.equipment} · ${row.result}`;', notes_render)
    (out / '04-notes.html').write_text(notes, encoding='utf-8')
    (out / 'form-notes.js').write_text(notes_js, encoding='utf-8')

    snippets = {
        'form-html': ('html', static[static.index('      <form'):static.index('      </form>') + len('      </form>')]),
        'box-model': ('css', '* { box-sizing: border-box; }\n.card { margin: 24px 0; padding: 24px; border: 1px solid #d5ddd3; }'),
        'event': ('javascript', "form.addEventListener('submit', event => {\n  event.preventDefault();\n  // 接著讀取輸入、驗證、更新陣列與 render。\n});"),
        'validation': ('javascript', js[js.index('  const equipment ='):js.index('  rows.push')].rstrip()),
        'render': ('javascript', js[js.index('function render()'):js.index("form.addEventListener")].rstrip()),
        'filter': ('javascript', "const visible = rows.filter(row =>\n  filter.value === 'all' || row.result === filter.value\n);\n// change 事件只要求重新呈現，不刪除 rows。\nfilter.addEventListener('change', render);"),
        'git': ('powershell', 'git init\ngit status\ngit add 01-static.html 02-styled.html 03-interactive.html form.css form.js\ngit diff --cached\ngit commit -m "建立巡檢表單練習原版"\n# 完成一次小修改後\ngit diff\ngit status'),
        'notes': ('text', note_html.strip() + '\n\n// 取得欄位\n' + note_declaration + '\n\n// 提交時，取代原本 rows.push 那一行\n' + note_validation + '\n\n// render 迴圈中，取代原本 item.textContent 那一行\n' + notes_render),
        'length': ('text', 'HTML：maxlength="20"，標籤顯示 1–20 字元\nJavaScript：equipment.length > 20\n錯誤訊息：設備名稱須為 1–20 字元，不能全是空白。')
    }
    versions = [('01-static.html', '01 · 靜態 HTML'), ('02-styled.html', '02 · 加入 CSS'), ('03-interactive.html', '03 · JavaScript 互動'), ('04-notes.html', '04 · 備註練習解答')]
    md = [f"# {lesson['title']}", '', '更新：' + lesson['date'], '', lesson['intro'], '', '## 準備', '']
    md += ['- ' + item for item in lesson['materials']]
    md += ['', '## 直接開啟版本對照', ''] + [f'- [{label}](../examples/form-dom/{filename})' for filename, label in versions]
    md += ['', '01／02 版尚未接互動；03／04 版只有當頁記憶體，重新整理會清空。所有程式碼可在對應檔案閱讀。下方片段需放回相應位置，並非每一段都可獨立執行。', '']

    def code(key):
        language, text = snippets[key]
        return f'<p class="muted">檔案中的重點片段，請配合完整範例閱讀。</p><pre><code>{escape(text)}</code></pre>'

    step_html = []
    for step in lesson['steps']:
        md += ['## ' + step['title'], '', step['text'], '', '**預期觀察：** ' + step['expected'], '']
        if step.get('code'):
            lang, text = snippets[step['code']]
            md += ['```' + lang, text, '```', '']
        step_html.append('<section class="stage"><h2>' + escape(step['title']) + '</h2><p>' + escape(step['text']) + '</p><aside class="note"><strong>預期觀察</strong><p>' + escape(step['expected']) + '</p></aside>' + (code(step['code']) if step.get('code') else '') + '</section>')
    exercise_html = []
    md += ['## 自己動手修改', '']
    for exercise in lesson['exercises']:
        md += ['### ' + exercise['title'], '', exercise['task'], '', '**參考解答：** ' + exercise['answer'], '']
        if exercise.get('code'):
            lang, text = snippets[exercise['code']]
            md += ['```' + lang, text, '```', '']
        exercise_html.append('<section><h3>' + escape(exercise['title']) + '</h3><p>' + escape(exercise['task']) + '</p><details><summary>完成修改後看解答</summary><p>' + escape(exercise['answer']) + '</p>' + (code(exercise['code']) if exercise.get('code') else '') + '</details></section>')
    md += ['## 完成檢核', ''] + ['- [ ] ' + c for c in lesson['checks']]
    md += ['', '本課不自動修改主教材進度；完成實作後再回主教材第 1 階段勾選原有驗收。', '', '## 排除卡點', '']
    for title, description in lesson['troubleshooting']:
        md += ['### ' + title, '', description, '']
    md += ['## 來源與範圍', '', '核對日期：' + lesson['date'] + '。版本安排、練習與解答是本教材的教學設計。', '']
    md += [f"- [{s['title']}]({s['url']})：{s['note']}" for s in lesson['sources']]
    (root / 'lessons/01-form-dom.md').write_text('\n'.join(md) + '\n', encoding='utf-8')
    ul = lambda items: '<ul>' + ''.join('<li>' + escape(s) + '</li>' for s in items) + '</ul>'
    links = ''.join(f'<a href="../examples/form-dom/{f}">{escape(label)} ↗</a>' for f, label in versions)
    trouble = ''.join('<h3>' + escape(t) + '</h3><p>' + escape(p) + '</p>' for t, p in lesson['troubleshooting'])
    refs = ''.join(f'<li><a href="{escape(s["url"], quote=True)}">{escape(s["title"])}</a>：{escape(s["note"])}</li>' for s in lesson['sources'])
    html = f'''<!doctype html>
<html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(lesson['title'])}</title><link rel="stylesheet" href="../assets/style.css"><style>main{{margin:0 auto;max-width:1000px}}.version-links{{display:flex;gap:12px 24px;flex-wrap:wrap}}.version-links a{{padding:8px 0}}pre{{white-space:pre-wrap;overflow-wrap:anywhere}}</style></head>
<body><a class="skip" href="#lesson">跳到課程內容</a><main id="lesson"><a href="../index.html#stage-1">← 回到主教材第 1 階段</a><header class="hero"><p class="eyebrow">GUIDED PRACTICE / 01</p><h1>先寫出表單，<br>再讓資料動起來。</h1><p>{escape(lesson['intro'])}</p><p class="muted">更新：{lesson['date']} · 三個進度版本與一個完整解答</p></header>
<section class="dashboard"><h2>準備與版本對照</h2>{ul(lesson['materials'])}<div class="version-links">{links}<a href="01-form-dom.md">Markdown 教材 ↗</a></div><p>01／02 版尚未接互動；03／04 版只有當頁記憶體，重新整理會清空。練習不會更動主教材進度或既有巡檢範例的保存資料。</p></section>
{''.join(step_html)}<section class="stage"><h2>自己動手修改</h2>{''.join(exercise_html)}</section><section class="stage"><h2>完成檢核</h2>{ul(lesson['checks'])}<p>完成操作後，再回到主教材第 1 階段勾選原有驗收。本課不會自動修改進度。</p></section><section class="stage"><h2>遇到卡點先檢查</h2>{trouble}</section><section class="stage"><h2>來源與核對範圍</h2><p>核對日期：{lesson['date']}。版本安排、練習與解答為本教材的教學設計。</p><ul>{refs}</ul></section><footer><a href="../index.html#stage-1">回到主教材 →</a> · <a href="00-first-web.html">複習第 0 階段</a></footer></main></body></html>'''
    (root / 'lessons/01-form-dom.html').write_text(html, encoding='utf-8')
