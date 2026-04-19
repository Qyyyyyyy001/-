#!/usr/bin/env python3
"""
PDF翻译工具 - 轻量Web界面（零额外依赖，用Python自带http.server）
启动: python3 web_ui_lite.py
浏览器打开: http://localhost:7860
"""

import http.server
import json
import os
import shutil
import sys
import tempfile
import threading
import time
import cgi
import urllib.parse

import base64
import io

from pdf_translator.extractor import get_page_count
from pdf_translator.translator import create_backend
from pdf_translator.overlay import translate_pdf_inplace


class CancelledError(Exception):
    """Raised from the progress callback to abort translation."""


# 全局翻译状态
translation_state = {
    "running": False,
    "progress": 0,
    "total": 0,
    "status": "就绪",
    "result_file": None,
    "preview": "",
    "error": None,
    "cancel_requested": False,
}


def _generate_thumbnail(pdf_path: str) -> str:
    """Render first page as a small PNG thumbnail, return base64 string."""
    try:
        import fitz
        doc = fitz.open(pdf_path)
        try:
            pix = doc[0].get_pixmap(matrix=fitz.Matrix(0.3, 0.3))
            png_bytes = pix.tobytes("png")
            return base64.b64encode(png_bytes).decode("ascii")
        finally:
            doc.close()
    except Exception:
        return ""

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

@media (prefers-color-scheme: dark) {
    :root {
        --bg-primary: #000000;
        --bg-secondary: #1c1c1e;
        --bg-tertiary: #2c2c2e;
        --text-primary: #f5f5f7;
        --text-secondary: #98989d;
        --text-tertiary: #636366;
        --accent: #0a84ff;
        --accent-hover: #2b96ff;
        --accent-active: #0073e6;
        --green: #30d158;
        --green-bg: rgba(48,209,88,0.12);
        --separator: rgba(84,84,88,0.35);
        --shadow-sm: 0 1px 3px rgba(0,0,0,0.3);
        --shadow-md: 0 4px 14px rgba(0,0,0,0.4);
        --shadow-lg: 0 8px 28px rgba(0,0,0,0.5);
    }
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: var(--font); background: var(--bg-primary); color: var(--text-primary);
       min-height: 100vh; -webkit-font-smoothing: antialiased; }

/* === Layout === */
.app-header { text-align: center; padding: 48px 20px 32px; }
.app-header h1 { font-size: 34px; font-weight: 700; letter-spacing: -0.5px;
                  color: var(--text-primary); }
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
.form-row input:focus, .form-row select:focus { background: var(--separator); }
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
.upload-area:hover { border-color: var(--accent); background: var(--bg-secondary); }
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

.btn-cancel { display: inline-flex; align-items: center; gap: 8px; padding: 10px 20px;
              border: 1px solid var(--separator); border-radius: var(--radius-md);
              font-family: var(--font); font-size: 14px; font-weight: 500;
              color: var(--text-secondary); background: transparent; cursor: pointer;
              transition: all 0.2s; margin-top: 12px; }
.btn-cancel:hover { color: #ff3b30; border-color: #ff3b30; }

/* Smooth entry animation for result card */
@keyframes slideUp {
    from { opacity: 0; transform: translateY(12px); }
    to { opacity: 1; transform: translateY(0); }
}
#resultCard:not(.hidden) { animation: slideUp 0.35s cubic-bezier(0.25, 0.8, 0.25, 1); }
#downloadArea:not(.hidden), #previewArea:not(.hidden) {
    animation: slideUp 0.35s cubic-bezier(0.25, 0.8, 0.25, 1);
}

/* PDF thumbnail preview */
.pdf-thumb { max-width: 120px; max-height: 160px; border-radius: 6px;
             box-shadow: var(--shadow-md); margin: 12px auto 0; display: block; }

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
            <label>Language</label>
            <div class="input-wrap">
                <select id="targetLang">
                    <option value="zh-CN">Chinese (Simplified)</option>
                    <option value="zh-TW">Chinese (Traditional)</option>
                    <option value="ja">Japanese</option>
                    <option value="ko">Korean</option>
                    <option value="fr">French</option>
                    <option value="de">German</option>
                    <option value="es">Spanish</option>
                    <option value="pt">Portuguese</option>
                    <option value="ru">Russian</option>
                    <option value="ar">Arabic</option>
                    <option value="th">Thai</option>
                    <option value="vi">Vietnamese</option>
                </select>
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
            <button class="btn-cancel hidden" id="cancelBtn" onclick="cancelTranslation()">Cancel</button>
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
        if (d.thumbnail) {
            let img = document.getElementById('pdfThumb');
            if (!img) {
                img = document.createElement('img');
                img.id = 'pdfThumb';
                img.className = 'pdf-thumb';
                document.getElementById('uploadArea').appendChild(img);
            }
            img.src = 'data:image/png;base64,' + d.thumbnail;
        }
    });
}

function validatePages() {
    const s = parseInt(document.getElementById('startPage').value) || 1;
    const e = parseInt(document.getElementById('endPage').value) || 1;
    if (s > e) {
        alert('Start page (' + s + ') cannot be greater than end page (' + e + ').');
        return false;
    }
    return true;
}

function startTranslation() {
    if (!uploadedFile) { alert('Please upload a PDF first.'); return; }
    if (!validatePages()) return;
    const btn = document.getElementById('translateBtn');
    btn.disabled = true; btn.textContent = 'Translating...';
    document.getElementById('resultCard').classList.remove('hidden');
    document.getElementById('downloadArea').classList.add('hidden');
    document.getElementById('previewArea').classList.add('hidden');
    document.getElementById('cancelBtn').classList.remove('hidden');
    // Smooth scroll to result
    setTimeout(() => document.getElementById('resultCard').scrollIntoView({behavior:'smooth', block:'start'}), 100);

    const fd = new FormData();
    fd.append('target_lang', document.getElementById('targetLang').value);
    fd.append('start_page', document.getElementById('startPage').value);
    fd.append('end_page', document.getElementById('endPage').value);
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
            document.getElementById('cancelBtn').classList.add('hidden');
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

function cancelTranslation() {
    fetch('/cancel', {method:'POST'}).then(() => {
        clearInterval(pollTimer);
        const btn = document.getElementById('translateBtn');
        btn.disabled = false; btn.textContent = 'Translate';
        document.getElementById('cancelBtn').classList.add('hidden');
        document.getElementById('statusText').textContent = 'Cancelled';
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
        elif self.path == "/cancel":
            translation_state["cancel_requested"] = True
            self._send_json({"status": "cancelled"})
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
                thumbnail = _generate_thumbnail(uploaded_pdf_path)
                self._send_json({
                    "total_pages": total,
                    "path": uploaded_pdf_path,
                    "thumbnail": thumbnail,
                })
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

        if not uploaded_pdf_path or not os.path.isfile(uploaded_pdf_path):
            self._send_json({"error": "请先上传PDF文件"})
            return

        def get_field(name, default=""):
            """Reliably read a field from cgi.FieldStorage."""
            if name not in form:
                return default
            item = form[name]
            if isinstance(item, list):
                return item[0].value if item else default
            return item.value if hasattr(item, "value") else str(item)

        params = {
            "target_lang": get_field("target_lang", "zh-CN"),
            "start_page": int(get_field("start_page", "1")),
            "end_page": int(get_field("end_page", "0")),
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
        "status": "初始化翻译引擎...", "result_file": None, "preview": "",
        "error": None, "cancel_requested": False,
    }

    try:
        total_pages = get_page_count(pdf_path)
        start = max(0, params["start_page"] - 1)
        end = min(total_pages, params["end_page"]) if params["end_page"] > 0 else total_pages
        translation_state["total"] = end - start

        target_lang = params.get("target_lang", "zh-CN")
        engine = create_backend("google", target_lang=target_lang)
        translation_state["status"] = f"翻译引擎: {engine.name()}"

        tmp_dir = tempfile.mkdtemp()
        output_path = os.path.join(tmp_dir, "translated.pdf")
        start_time = time.time()

        def progress_cb(current, total):
            if translation_state.get("cancel_requested"):
                raise CancelledError("User cancelled")
            translation_state["progress"] = current
            elapsed = time.time() - start_time
            speed = current / elapsed if elapsed > 0 else 0
            eta = (total - current) / speed if speed > 0 else 0
            translation_state["status"] = (
                f"翻译中... {current}/{total} 页 "
                f"| {speed:.1f} 页/秒 | 剩余 {eta:.0f} 秒"
            )

        # 使用overlay模式：保留图片和布局，原位替换文字
        result = translate_pdf_inplace(
            input_path=pdf_path,
            output_path=output_path,
            translator_fn=engine.translate,
            start_page=start,
            end_page=end,
            remove_empty=True,
            progress_callback=progress_cb,
        )

        elapsed = time.time() - start_time
        translated = result.get("translated", 0)
        failed = result.get("failed", 0)
        skipped = result.get("skipped", 0)
        removed = result.get("pages_removed", 0)

        parts = [f"翻译完成! {end - start} 页, {elapsed:.1f} 秒"]
        parts.append(f"成功 {translated} 块")
        if failed:
            parts.append(f"失败 {failed} 块")
        if removed:
            parts.append(f"删除 {removed} 空白页")
        status = ", ".join(parts)

        if translated == 0 and failed > 0:
            status = f"翻译失败: 全部 {failed} 个文字块翻译出错，请检查网络"

        translation_state.update({
            "running": False,
            "status": status,
            "result_file": output_path if translated > 0 else None,
            "preview": f"翻译: {translated} 成功, {failed} 失败, {skipped} 跳过" if translated > 0 else "",
        })

    except CancelledError:
        translation_state.update({
            "running": False,
            "status": "已取消",
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
