#!/usr/bin/env python3
"""
PDF翻译工具 - 轻量Web界面（零额外依赖，用Python自带http.server）
启动: python3 web_ui_lite.py
浏览器打开: http://localhost:7860
"""

import http.server
import json
import os
import sys
import tempfile
import threading
import time
import cgi
import urllib.parse

from pdf_translator.extractor import get_page_count, extract_pages_batch
from pdf_translator.translator import create_backend, BatchTranslator
from pdf_translator.writer import create_writer
from pdf_translator.checkpoint import Checkpoint

# 全局翻译状态
translation_state = {
    "running": False,
    "progress": 0,
    "total": 0,
    "status": "就绪",
    "result_file": None,
    "preview": "",
    "error": None,
}

HTML_PAGE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>PDF Translator</title>
<style>
/* === Apple HIG: System Font Stack, Spacing, Radius === */
:root {
    --bg-primary: #f5f5f7;
    --bg-secondary: #ffffff;
    --bg-tertiary: #f2f2f7;
    --text-primary: #1d1d1f;
    --text-secondary: #86868b;
    --text-tertiary: #aeaeb2;
    --accent: #0071e3;
    --accent-hover: #0077ed;
    --accent-active: #006edb;
    --green: #34c759;
    --green-bg: #f0faf3;
    --separator: rgba(60,60,67,0.12);
    --shadow-sm: 0 1px 3px rgba(0,0,0,0.04), 0 1px 2px rgba(0,0,0,0.06);
    --shadow-md: 0 4px 14px rgba(0,0,0,0.06), 0 2px 6px rgba(0,0,0,0.04);
    --shadow-lg: 0 8px 28px rgba(0,0,0,0.08), 0 2px 8px rgba(0,0,0,0.04);
    --radius-sm: 8px;
    --radius-md: 12px;
    --radius-lg: 16px;
    --radius-xl: 20px;
    --font: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text",
             "Helvetica Neue", "PingFang SC", "Microsoft YaHei", sans-serif;
    --font-mono: "SF Mono", SFMono-Regular, ui-monospace, Menlo, Monaco, monospace;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: var(--font); background: var(--bg-primary); color: var(--text-primary);
       min-height: 100vh; -webkit-font-smoothing: antialiased; }

/* === Layout === */
.app-header { text-align: center; padding: 48px 20px 32px; }
.app-header h1 { font-size: 34px; font-weight: 700; letter-spacing: -0.5px;
                  background: linear-gradient(135deg, var(--text-primary) 0%, #424245 100%);
                  -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.app-header p { font-size: 17px; color: var(--text-secondary); margin-top: 8px;
                font-weight: 400; letter-spacing: -0.2px; }
.container { max-width: 680px; margin: 0 auto; padding: 0 20px 60px; }

/* === Card (Apple grouped-style) === */
.card { background: var(--bg-secondary); border-radius: var(--radius-lg);
        padding: 20px; margin-bottom: 16px; box-shadow: var(--shadow-sm); }
.card-title { font-size: 13px; font-weight: 600; color: var(--text-secondary);
              text-transform: uppercase; letter-spacing: 0.5px; padding: 0 4px;
              margin-bottom: 12px; }

/* === Form Elements (Apple native feel) === */
.form-row { display: flex; align-items: center; padding: 11px 0;
            border-bottom: 0.5px solid var(--separator); }
.form-row:last-child { border-bottom: none; }
.form-row label { flex: 0 0 90px; font-size: 15px; color: var(--text-primary); font-weight: 400; }
.form-row .input-wrap { flex: 1; display: flex; justify-content: flex-end; }
.form-row select, .form-row input[type="number"], .form-row input[type="password"] {
    font-family: var(--font); font-size: 15px; color: var(--text-primary);
    background: var(--bg-tertiary); border: none; border-radius: var(--radius-sm);
    padding: 8px 12px; outline: none; text-align: right; width: 100%;
    transition: background 0.2s; -webkit-appearance: none; }
.form-row select { padding-right: 28px; background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath d='M3 4.5L6 7.5L9 4.5' stroke='%2386868b' stroke-width='1.5' fill='none' stroke-linecap='round'/%3E%3C/svg%3E");
    background-repeat: no-repeat; background-position: right 10px center; text-align: left; }
.form-row input:focus, .form-row select:focus { background: #e8e8ed; }
.form-row input[type="number"] { width: 80px; text-align: center; }

/* === Toggle Switch (Apple style) === */
.toggle { position: relative; width: 51px; height: 31px; flex-shrink: 0; }
.toggle input { opacity: 0; width: 0; height: 0; }
.toggle .slider { position: absolute; inset: 0; background: #e9e9eb; border-radius: 31px;
                  cursor: pointer; transition: background 0.25s; }
.toggle .slider::before { content: ""; position: absolute; width: 27px; height: 27px;
    left: 2px; top: 2px; background: white; border-radius: 50%; transition: transform 0.25s;
    box-shadow: 0 2px 4px rgba(0,0,0,0.15); }
.toggle input:checked + .slider { background: var(--green); }
.toggle input:checked + .slider::before { transform: translateX(20px); }

/* === Upload Area === */
.upload-area { border: 2px dashed var(--separator); border-radius: var(--radius-md);
               padding: 36px 20px; text-align: center; cursor: pointer;
               transition: all 0.3s ease; background: var(--bg-tertiary); }
.upload-area:hover { border-color: var(--accent); background: #f0f5ff; }
.upload-area.has-file { border-color: var(--green); background: var(--green-bg);
                        border-style: solid; }
.upload-area input { display: none; }
.upload-icon { width: 48px; height: 48px; margin: 0 auto 12px; border-radius: 12px;
               background: linear-gradient(135deg, #007aff, #5856d6);
               display: flex; align-items: center; justify-content: center;
               font-size: 24px; color: white; box-shadow: 0 4px 12px rgba(0,122,255,0.3); }
.upload-area.has-file .upload-icon { background: linear-gradient(135deg, #34c759, #30d158);
               box-shadow: 0 4px 12px rgba(52,199,89,0.3); }
.upload-label { font-size: 15px; color: var(--text-secondary); margin-top: 4px; }
.file-info { color: var(--green); font-weight: 500; margin-top: 8px; font-size: 14px; }

/* === Primary Button === */
.btn-primary { display: block; width: 100%; padding: 16px; border: none;
               border-radius: var(--radius-md); font-family: var(--font);
               font-size: 17px; font-weight: 600; letter-spacing: -0.2px;
               color: white; background: var(--accent); cursor: pointer;
               transition: all 0.2s; margin-bottom: 16px; box-shadow: var(--shadow-sm); }
.btn-primary:hover { background: var(--accent-hover); box-shadow: var(--shadow-md);
                     transform: translateY(-1px); }
.btn-primary:active { background: var(--accent-active); transform: translateY(0);
                      box-shadow: var(--shadow-sm); }
.btn-primary:disabled { background: var(--text-tertiary); cursor: not-allowed;
                        transform: none; box-shadow: none; }

/* === Download Button === */
.btn-download { display: inline-flex; align-items: center; gap: 8px; padding: 12px 24px;
                border: none; border-radius: var(--radius-md); font-family: var(--font);
                font-size: 15px; font-weight: 600; color: white; background: var(--green);
                cursor: pointer; transition: all 0.2s; text-decoration: none;
                box-shadow: var(--shadow-sm); margin-top: 12px; }
.btn-download:hover { background: #2db84e; box-shadow: var(--shadow-md); }
.btn-download svg { width: 16px; height: 16px; }

/* === Progress Bar === */
.progress-wrap { margin: 16px 0; }
.progress-track { background: var(--bg-tertiary); border-radius: 6px; height: 8px;
                  overflow: hidden; }
.progress-fill { height: 100%; border-radius: 6px;
                 background: linear-gradient(90deg, #007aff, #5ac8fa);
                 transition: width 0.4s ease; min-width: 4px; }
.progress-info { display: flex; justify-content: space-between; margin-top: 8px; }
.progress-pct { font-size: 26px; font-weight: 700; color: var(--text-primary);
                letter-spacing: -1px; font-variant-numeric: tabular-nums; }
.progress-status { font-size: 13px; color: var(--text-secondary); margin-top: 4px;
                   line-height: 1.4; }

/* === Preview === */
.preview-box { background: var(--bg-tertiary); border-radius: var(--radius-md);
               padding: 16px; margin-top: 16px; white-space: pre-wrap;
               font-family: var(--font-mono); font-size: 12px; line-height: 1.7;
               color: var(--text-primary); max-height: 360px; overflow-y: auto;
               border: 0.5px solid var(--separator); }
.preview-title { font-size: 13px; font-weight: 600; color: var(--text-secondary);
                 text-transform: uppercase; letter-spacing: 0.5px; margin-top: 20px;
                 margin-bottom: 8px; }

.hidden { display: none; }
.api-key-row { display: none; }
.api-key-row.show { display: flex; }

/* === Responsive === */
@media (max-width: 500px) {
    .app-header h1 { font-size: 28px; }
    .form-row label { flex: 0 0 72px; font-size: 14px; }
}
</style>
</head>
<body>
<div class="app-header">
    <h1>PDF Translator</h1>
    <p>Large PDF (800+ pages) English to Chinese</p>
</div>
<div class="container">

    <!-- Upload -->
    <div class="card">
        <div class="upload-area" id="uploadArea" onclick="document.getElementById('fileInput').click()">
            <div class="upload-icon">
                <svg width="24" height="24" fill="none" viewBox="0 0 24 24"><path d="M12 3v12m0-12L8 7m4-4l4 4" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M4 17v2a2 2 0 002 2h12a2 2 0 002-2v-2" stroke="white" stroke-width="2" stroke-linecap="round"/></svg>
            </div>
            <div class="upload-label">Click or drag PDF file here</div>
            <div class="file-info hidden" id="fileInfo"></div>
            <input type="file" id="fileInput" accept=".pdf" onchange="handleFileSelect(this)">
        </div>
    </div>

    <!-- Settings -->
    <div class="card-title">Settings</div>
    <div class="card">
        <div class="form-row">
            <label>Engine</label>
            <div class="input-wrap">
                <select id="backend" onchange="toggleApiKey()">
                    <option value="google">Google Translate</option>
                    <option value="builtin">Built-in Dictionary</option>
                    <option value="marian">MarianMT (Local)</option>
                    <option value="argos">Argos (Local)</option>
                    <option value="deepl">DeepL</option>
                    <option value="claude">Claude</option>
                </select>
            </div>
        </div>
        <div class="form-row api-key-row" id="apiKeyGroup">
            <label>API Key</label>
            <div class="input-wrap">
                <input type="password" id="apiKey" placeholder="Required">
            </div>
        </div>
        <div class="form-row">
            <label>Pages</label>
            <div class="input-wrap" style="gap:8px;">
                <input type="number" id="startPage" value="1" min="1">
                <span style="color:var(--text-tertiary);padding:0 4px;">-</span>
                <input type="number" id="endPage" value="1" min="1">
            </div>
        </div>
        <div class="form-row">
            <label>Format</label>
            <div class="input-wrap">
                <select id="outputFormat">
                    <option value="txt">TXT</option>
                    <option value="pdf">PDF</option>
                </select>
            </div>
        </div>
        <div class="form-row">
            <label>Workers</label>
            <div class="input-wrap">
                <input type="number" id="workers" value="2" min="1" max="8">
            </div>
        </div>
        <div class="form-row">
            <label>Bilingual</label>
            <div class="input-wrap">
                <label class="toggle"><input type="checkbox" id="bilingual"><span class="slider"></span></label>
            </div>
        </div>
    </div>

    <!-- Translate Button -->
    <button class="btn-primary" id="translateBtn" onclick="startTranslation()">Translate</button>

    <!-- Result -->
    <div class="hidden" id="resultCard">
        <div class="card">
            <div class="progress-wrap">
                <div class="progress-info">
                    <div>
                        <div class="progress-pct" id="progressPct">0%</div>
                        <div class="progress-status" id="statusText">Preparing...</div>
                    </div>
                </div>
                <div class="progress-track">
                    <div class="progress-fill" id="progressBar" style="width:0%"></div>
                </div>
            </div>
            <div id="downloadArea" class="hidden">
                <a class="btn-download" id="downloadLink" href="#" download>
                    <svg viewBox="0 0 16 16" fill="none"><path d="M8 2v8m0 0l-3-3m3 3l3-3M3 12h10" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
                    Download
                </a>
            </div>
        </div>
        <div id="previewArea" class="hidden">
            <div class="preview-title">Preview</div>
            <div class="preview-box" id="previewText"></div>
        </div>
    </div>
</div>

<script>
let uploadedFile = null, pollTimer = null;

function handleFileSelect(input) {
    const file = input.files[0];
    if (!file) return;
    uploadedFile = file;
    document.getElementById('uploadArea').classList.add('has-file');
    const info = document.getElementById('fileInfo');
    info.classList.remove('hidden');
    info.textContent = file.name + ' (' + (file.size/1024/1024).toFixed(1) + ' MB)';

    const fd = new FormData(); fd.append('file', file);
    fetch('/upload', {method:'POST', body:fd}).then(r=>r.json()).then(d=>{
        if (d.total_pages) {
            info.textContent = file.name + '  |  ' + (file.size/1024/1024).toFixed(1) + ' MB  |  ' + d.total_pages + ' pages';
            document.getElementById('endPage').value = d.total_pages;
            document.getElementById('endPage').max = d.total_pages;
            document.getElementById('startPage').max = d.total_pages;
        }
    });
}

function toggleApiKey() {
    const v = document.getElementById('backend').value;
    document.getElementById('apiKeyGroup').classList.toggle('show', v==='deepl'||v==='claude');
}

function startTranslation() {
    if (!uploadedFile) { alert('Please upload a PDF first.'); return; }
    const btn = document.getElementById('translateBtn');
    btn.disabled = true; btn.textContent = 'Translating...';
    document.getElementById('resultCard').classList.remove('hidden');
    document.getElementById('downloadArea').classList.add('hidden');
    document.getElementById('previewArea').classList.add('hidden');

    const fd = new FormData();
    fd.append('file', uploadedFile);
    ['backend','apiKey','startPage','endPage','outputFormat','workers'].forEach(id=>{
        const el = document.getElementById(id);
        const key = id==='apiKey'?'api_key':id==='startPage'?'start_page':
                    id==='endPage'?'end_page':id==='outputFormat'?'output_format':id;
        fd.append(key, el.value);
    });
    fd.append('bilingual', document.getElementById('bilingual').checked?'1':'0');
    fetch('/translate',{method:'POST',body:fd}).then(r=>r.json()).then(d=>{ if(d.error) alert(d.error); });
    pollTimer = setInterval(pollProgress, 500);
}

function pollProgress() {
    fetch('/progress').then(r=>r.json()).then(d=>{
        const pct = d.total>0 ? Math.round(d.progress/d.total*100) : 0;
        document.getElementById('progressBar').style.width = pct+'%';
        document.getElementById('progressPct').textContent = pct+'%';
        document.getElementById('statusText').textContent = d.status;
        if (!d.running && d.progress>0) {
            clearInterval(pollTimer);
            const btn = document.getElementById('translateBtn');
            btn.disabled = false; btn.textContent = 'Translate';
            if (d.result_file) {
                document.getElementById('downloadArea').classList.remove('hidden');
                document.getElementById('downloadLink').href = '/download?f='+encodeURIComponent(d.result_file);
            }
            if (d.preview) {
                document.getElementById('previewArea').classList.remove('hidden');
                document.getElementById('previewText').textContent = d.preview;
            }
        }
    });
}

const area = document.getElementById('uploadArea');
area.addEventListener('dragover', e=>{e.preventDefault();area.style.borderColor='var(--accent)';});
area.addEventListener('dragleave', ()=>{area.style.borderColor='';});
area.addEventListener('drop', e=>{
    e.preventDefault(); area.style.borderColor='';
    const f=e.dataTransfer.files[0];
    if(f&&f.name.endsWith('.pdf')){document.getElementById('fileInput').files=e.dataTransfer.files;handleFileSelect(document.getElementById('fileInput'));}
});
</script>
</body>
</html>"""

# 临时存储上传的PDF路径
uploaded_pdf_path = None


class TranslationHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # 静默日志

    def do_GET(self):
        if self.path == "/":
            self._send_html(HTML_PAGE)
        elif self.path == "/progress":
            self._send_json(translation_state)
        elif self.path.startswith("/download"):
            self._handle_download()
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path == "/upload":
            self._handle_upload()
        elif self.path == "/translate":
            self._handle_translate()
        else:
            self.send_error(404)

    def _handle_upload(self):
        global uploaded_pdf_path
        content_type = self.headers.get("Content-Type", "")
        if "multipart/form-data" not in content_type:
            self._send_json({"error": "invalid content type"})
            return

        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={"REQUEST_METHOD": "POST", "CONTENT_TYPE": content_type},
        )
        file_item = form["file"]
        if file_item.filename:
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
            tmp.write(file_item.file.read())
            tmp.close()
            uploaded_pdf_path = tmp.name
            try:
                total = get_page_count(uploaded_pdf_path)
                self._send_json({"total_pages": total, "path": uploaded_pdf_path})
            except Exception as e:
                self._send_json({"error": str(e)})
        else:
            self._send_json({"error": "no file"})

    def _handle_translate(self):
        global uploaded_pdf_path, translation_state

        if translation_state["running"]:
            self._send_json({"error": "翻译正在进行中，请等待完成"})
            return

        content_type = self.headers.get("Content-Type", "")
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={"REQUEST_METHOD": "POST", "CONTENT_TYPE": content_type},
        )

        # 如果表单里有文件，保存它
        if "file" in form and form["file"].filename:
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
            tmp.write(form["file"].file.read())
            tmp.close()
            uploaded_pdf_path = tmp.name

        if not uploaded_pdf_path or not os.path.isfile(uploaded_pdf_path):
            self._send_json({"error": "请先上传PDF文件"})
            return

        params = {
            "backend": form.getvalue("backend", "google"),
            "api_key": form.getvalue("api_key", ""),
            "start_page": int(form.getvalue("start_page", "1")),
            "end_page": int(form.getvalue("end_page", "0")),
            "output_format": form.getvalue("output_format", "txt"),
            "bilingual": form.getvalue("bilingual", "0") == "1",
            "workers": int(form.getvalue("workers", "2")),
        }

        thread = threading.Thread(target=run_translation, args=(uploaded_pdf_path, params))
        thread.daemon = True
        thread.start()

        self._send_json({"status": "started"})

    def _handle_download(self):
        query = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query)
        filepath = params.get("f", [None])[0]

        if not filepath or not os.path.isfile(filepath):
            self.send_error(404, "File not found")
            return

        filename = os.path.basename(filepath)
        import shutil
        self.send_response(200)
        self.send_header("Content-Type", "application/octet-stream")
        self.send_header("Content-Disposition", f'attachment; filename="{filename}"')
        self.send_header("Content-Length", str(os.path.getsize(filepath)))
        self.end_headers()
        with open(filepath, "rb") as f:
            shutil.copyfileobj(f, self.wfile)

    def _send_html(self, html):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))

    def _send_json(self, data):
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))


def run_translation(pdf_path, params):
    global translation_state

    translation_state = {
        "running": True, "progress": 0, "total": 0,
        "status": "初始化翻译引擎...", "result_file": None, "preview": "", "error": None,
    }

    try:
        total_pages = get_page_count(pdf_path)
        start = max(0, params["start_page"] - 1)
        end = min(total_pages, params["end_page"]) if params["end_page"] > 0 else total_pages
        page_range = list(range(start, end))
        translation_state["total"] = len(page_range)

        engine = create_backend(params["backend"], api_key=params["api_key"] or None)
        translation_state["status"] = f"翻译引擎: {engine.name()}"

        translator = BatchTranslator(
            backend=engine,
            workers=params["workers"],
            delay=0.3 if params["backend"] == "google" else 0.0,
        )

        tmp_dir = tempfile.mkdtemp()
        ckpt_path = os.path.join(tmp_dir, "progress.json")
        checkpoint = Checkpoint(ckpt_path)
        checkpoint.set_metadata(pdf_path, total_pages, params["backend"])

        batch_size = 10
        batches = [page_range[i:i + batch_size] for i in range(0, len(page_range), batch_size)]
        start_time = time.time()

        for batch_pages in batches:
            page_texts = extract_pages_batch(pdf_path, batch_pages[0], batch_pages[-1] + 1)
            translatable = [(pn, text) for pn, text in page_texts if len(text.strip()) >= 5]
            for pn, text in page_texts:
                if len(text.strip()) < 5:
                    checkpoint.save_page(pn, text, "")

            if translatable:
                try:
                    results = translator.translate_batch(translatable)
                    for pn, text in translatable:
                        checkpoint.save_page(pn, text, results.get(pn, ""))
                except Exception as e:
                    for pn, text in translatable:
                        checkpoint.save_page(pn, text, f"[翻译失败: {e}]")

            checkpoint.save()
            translation_state["progress"] += len(batch_pages)
            elapsed = time.time() - start_time
            speed = translation_state["progress"] / elapsed if elapsed > 0 else 0
            eta = (len(page_range) - translation_state["progress"]) / speed if speed > 0 else 0
            translation_state["status"] = (
                f"翻译中... {translation_state['progress']}/{len(page_range)} 页 "
                f"| {speed:.1f} 页/秒 | 剩余 {eta:.0f} 秒"
            )

        # 生成输出
        translation_state["status"] = "生成输出文件..."
        ext = ".pdf" if params["output_format"] == "pdf" else ".txt"
        output_path = os.path.join(tmp_dir, f"translated{ext}")
        writer = create_writer(params["output_format"])
        pages_data = checkpoint.get_all_pages()
        writer.write(pages_data, output_path, bilingual=params["bilingual"])

        # 预览
        preview_lines = []
        for pn in sorted(pages_data.keys())[:3]:
            t = pages_data[pn].get("translated", "")
            snippet = t[:300] + "..." if len(t) > 300 else t
            preview_lines.append(f"--- 第 {pn+1} 页 ---\n{snippet}")

        elapsed = time.time() - start_time
        translation_state.update({
            "running": False,
            "status": f"翻译完成! 共 {len(page_range)} 页, 耗时 {elapsed:.1f} 秒",
            "result_file": output_path,
            "preview": "\n\n".join(preview_lines),
        })

    except Exception as e:
        translation_state.update({
            "running": False,
            "status": f"翻译失败: {e}",
            "error": str(e),
        })


def main():
    port = 7860
    server = http.server.HTTPServer(("0.0.0.0", port), TranslationHandler)
    print(f"PDF 翻译工具 Web 界面已启动!")
    print(f"请在浏览器打开: http://localhost:{port}")
    print(f"按 Ctrl+C 停止服务")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n已停止")
        server.server_close()


if __name__ == "__main__":
    main()
