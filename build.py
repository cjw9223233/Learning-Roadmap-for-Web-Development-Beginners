"""Build the offline HTML and Markdown from the same course source."""
import json
from pathlib import Path
from html import escape
from build_lessons import build_lessons

ROOT = Path(__file__).resolve().parent
data = json.loads((ROOT / 'course.json').read_text(encoding='utf-8'))

def ul(items):
    return '<ul>' + ''.join('<li>' + escape(x) + '</li>' for x in items) + '</ul>'

sections, md = [], [f"# {data['title']}（2026 年版）", '', f"版本：{data['version']}｜自學教材", '', data['intro'], '',
    '## 使用方式', '', '每次挑選一個小任務，依序閱讀概念、動手修改、觀察失敗、完成驗收，再用自己的話解釋。建議一次約 45–60 分鐘，可依進度調整；沒有保證完成時數。', '',
    '互動版：開啟同目錄 index.html。可篩選學習路線、勾選驗收及回答小測驗。巡檢實作：examples/inspection.html。', '',
    '這是九階段入門教材與實作導航；後端、框架及部署仍需搭配所選技術的官方文件完成環境建置。所有練習使用虛構資料。', '', '## 選擇學習目標', '']
for key, track in data['tracks'].items():
    md += [f"### {key}｜{track['name']}", '', track['description'], '', '主要階段：' + ' → '.join(map(str, track['stages'])), '']
md += ['## 貫穿全程的能力', '', '- Git：每次小改動都先看差異，再提交。', '- 測試：從輸入、預期結果與失敗案例開始。', '- 資安：使用虛構資料、保護機密、驗證權限。', '- AI：先理解再接受，並以獨立驗收證據確認。', '']
for stage in data['stages']:
    n = stage['id']
    heading = f"第 {n} 階段｜{stage['title']}"
    check_html = ''.join(f'<label class="check"><input type="checkbox" data-check="{n}-{i}"><span>{escape(c)}</span></label>' for i,c in enumerate(stage['checks']))
    options = ''.join(f'<label class="option"><input type="radio" name="q{n}" value="{i}"><span>{escape(o)}</span></label>' for i,o in enumerate(stage['quiz']['options']))
    resource_html = ''.join(f'<li><a href="{escape(data["sources"][i]["url"], quote=True)}">{escape(data["sources"][i]["title"])}</a></li>' for i in stage['resources'])
    lessons_html = ''.join(f'<aside class="note"><strong>逐步實作</strong><p><a href="{escape(item["html"], quote=True)}">{escape(item["title"])}</a></p><p>{escape(item["description"])}</p><a href="{escape(item["markdown"], quote=True)}">閱讀此練習的 Markdown</a></aside>' for item in stage.get('lessons', []))
    sections.append(f'''<article class="stage" id="stage-{n}" data-stage="{n}">
<header><span class="eyebrow">STAGE {n:02d}</span><h2>{escape(heading)}</h2><p class="subtitle">{escape(stage['subtitle'])}</p></header>
<p class="prerequisite"><strong>開始前</strong>　{escape(stage['prerequisite'])}</p>
{lessons_html}
<h3>學完能做什麼</h3>{ul(stage['goals'])}
<h3>先理解</h3>{''.join('<h4>'+escape(t)+'</h4><p>'+escape(p)+'</p>' for t,p in stage['concepts'])}
<h3>動手做</h3><ol>{''.join('<li>'+escape(s)+'</li>' for s in stage['steps'])}</ol>
<div class="code-head"><span>{escape(stage['code']['language'])}</span><button type="button" class="copy">複製範例</button></div><pre><code>{escape(stage['code']['text'])}</code></pre>
<aside class="note"><strong>常見卡點</strong><p>{escape(stage['pitfall'])}</p></aside>
<h3>實作驗收</h3><p class="muted">完成實際操作後再勾選；小測驗答對不會自動算作完成。</p>{check_html}
<form class="quiz" data-quiz="{n}"><h3>理解小測驗</h3><fieldset><legend>{escape(stage['quiz']['question'])}</legend>{options}</fieldset><button type="submit">檢查答案</button><p class="feedback" role="status" aria-live="polite"></p></form>
<details><summary>延伸閱讀</summary><ul>{resource_html}</ul></details></article>''')
    md += [f'## {heading}', '', stage['subtitle'], '', '**開始前：** ' + stage['prerequisite'], '']
    for item in stage.get('lessons', []):
        md += [f"逐步實作：[{item['title']}]({item['html']})｜[Markdown 版]({item['markdown']})", '', item['description'], '']
    md += ['### 學完能做什麼', '']
    md += ['- ' + g for g in stage['goals']] + ['', '### 先理解', '']
    for title, paragraph in stage['concepts']:
        md += [f'#### {title}', '', paragraph, '']
    md += ['### 動手做', ''] + [f'{i+1}. {s}' for i,s in enumerate(stage['steps'])] + ['', '```'+stage['code']['language'], stage['code']['text'], '```', '', '**常見卡點：** '+stage['pitfall'], '', '### 實作驗收', '']
    md += ['- [ ] ' + c for c in stage['checks']] + ['', '### 理解小測驗', '', stage['quiz']['question'], '']
    md += [f'{i+1}. {o}' for i,o in enumerate(stage['quiz']['options'])] + ['', f"答案：{stage['quiz']['answer']+1}。{stage['quiz']['explanation']}", '', '### 延伸閱讀', '']
    md += [f"- [{data['sources'][i]['title']}]({data['sources'][i]['url']})" for i in stage['resources']] + ['']

sources_html = ''.join(f'<li><a href="{escape(s["url"], quote=True)}">{escape(s["title"])}</a><p>{escape(s["note"])}</p></li>' for s in data['sources'])
md += ['## 資料來源與核對範圍', '', '核對日期：2026-11-17。來源說明列出本次核對範圍；其餘連結為延伸閱讀，沒有宣稱逐頁驗證。', '']
md += [f"- [{s['title']}]({s['url']})：{s['note']}" for s in data['sources']]
md += ['', '## 學習紀錄', '', '| 日期 | 階段／任務 | 實際操作與驗收證據 | 卡點與下一步 |', '| --- | --- | --- | --- |', '| | | | |', '', '## 版本紀錄', '']
md += ['- ' + entry for entry in data['history']] + ['']
(ROOT/'教材.md').write_text('\n'.join(md), encoding='utf-8')
nav = ''.join(f'<a href="#stage-{s["id"]}" data-nav="{s["id"]}"><span>{s["id"]:02d}</span>{escape(s["title"])}</a>' for s in data['stages'])
html = f'''<!doctype html>
<html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{data['title']}｜互動教材</title><link rel="stylesheet" href="assets/style.css"></head>
<body><a class="skip" href="#content">跳到教材內容</a>
<aside class="sidebar"><a class="brand" href="#top">WEB / 學習手冊<span>2026 EDITION</span></a><p class="muted">以實作累積理解</p><nav aria-label="教材階段">{nav}<a href="#sources">資料來源</a></nav><a class="example-link" href="examples/inspection.html">開啟巡檢練習 ↗</a><a href="教材.md">閱讀 Markdown 教材 ↗</a></aside>
<main id="content"><header id="top" class="hero"><p class="eyebrow">從零開始 · 以成果前進</p><h1>寫出第一個網頁，<br>再把它變成系統。</h1><p>{escape(data['intro'])}</p><div class="hero-meta"><span>09 學習階段</span><span>03 目標路線</span><span>離線閱讀與練習</span></div></header>
<section class="dashboard" aria-labelledby="path-title"><h2 id="path-title">選擇你的目標</h2><label for="track">學習路線</label><select id="track"><option value="B">B · Web 全端系統（全部九階段）</option><option value="A">A · 工作工具開發</option><option value="C">C · AI 應用開發</option></select><p id="track-description"></p><p>先讀概念 → 動手修改 → 觀察失敗 → 通過驗收。Git、測試、資安與 AI 協作隨專案逐步加深。</p><div class="progress-label"><strong id="progress-text">0 / 0 項驗收</strong><span id="stage-text"></span></div><progress id="progress" max="1" value="0">0%</progress><p class="muted">勾選記錄儲存在此瀏覽器；更換瀏覽器、檔案位置或清除資料可能影響保存。可匯出備份。小測驗與巡檢練習不計入驗收進度。</p><div class="actions"><button id="export" type="button">匯出學習進度</button><label class="file-button" for="import">匯入進度<input id="import" type="file" accept="application/json,.json"></label><button id="reset" class="secondary" type="button">重設驗收</button></div><p id="storage-status" role="status" aria-live="polite"></p></section>
<section class="start"><h2>今天先完成一件小事</h2><p><a href="lessons/00-first-web.html">從第 0 階段逐步練習開始 →</a> 建立自己的 HTML，再用離線模擬器觀察一次 HTTP 往返。每次練習後，用自己的話寫下「輸入是什麼、程式做了什麼、如何證明結果正確」。</p><p>這是入門教材與實作導航；框架、後端與部署需搭配所選技術的官方文件。沒有固定完成期限，通過實作驗收再往下走。</p></section>
<div id="stages">{''.join(sections)}</div><section id="sources" class="stage"><p class="eyebrow">REFERENCES</p><h2>資料來源與核對範圍</h2><p>核對日期：2026-11-17。九階段、三條路線與練習題為本教材的教學設計。外部閱讀連結需要網路。</p><ol class="sources">{sources_html}</ol></section>
<footer>版本 {data['version']} · 所有實作使用虛構資料 · 持續以可驗收的小成果前進</footer></main>
<script id="course-data" type="application/json">{json.dumps(data, ensure_ascii=False).replace('<', chr(92)+'u003c')}</script><script src="assets/app.js"></script></body></html>'''
(ROOT/'index.html').write_text(html, encoding='utf-8')
build_lessons(ROOT)
print('Built main course and guided stage-0/1/2A/2B/2C/2D/3A/3B lessons in HTML and Markdown')
