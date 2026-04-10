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
<title>PDF 翻译工具 - 英译中</title>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
       background: #f0f2f5; color: #333; min-height: 100vh; }
.container { max-width: 900px; margin: 0 auto; padding: 20px; }
h1 { text-align: center; margin: 20px 0; color: #1a1a2e; font-size: 28px; }
.subtitle { text-align: center; color: #666; margin-bottom: 30px; }
.card { background: white; border-radius: 12px; padding: 24px; margin-bottom: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08); }
.card h2 { font-size: 18px; margin-bottom: 16px; color: #1a1a2e;
           border-bottom: 2px solid #4361ee; padding-bottom: 8px; display: inline-block; }
.form-group { margin-bottom: 16px; }
.form-group label { display: block; font-weight: 600; margin-bottom: 6px; color: #444; }
.form-group select, .form-group input[type="text"], .form-group input[type="number"],
.form-group input[type="password"] {
    width: 100%; padding: 10px 12px; border: 1px solid #ddd; border-radius: 8px;
    font-size: 14px; transition: border-color 0.2s; }
.form-group select:focus, .form-group input:focus { border-color: #4361ee; outline: none; }
.row { display: flex; gap: 16px; }
.row .form-group { flex: 1; }
.upload-area { border: 2px dashed #ccc; border-radius: 12px; padding: 40px; text-align: center;
               cursor: pointer; transition: all 0.3s; background: #fafbfc; }
.upload-area:hover { border-color: #4361ee; background: #f0f4ff; }
.upload-area.has-file { border-color: #2ecc71; background: #f0fff4; }
.upload-area input { display: none; }
.upload-icon { font-size: 48px; margin-bottom: 12px; }
.file-info { color: #2ecc71; font-weight: 600; margin-top: 8px; }
.checkbox-group { display: flex; align-items: center; gap: 8px; }
.checkbox-group input { width: 18px; height: 18px; }
.btn { display: inline-block; padding: 12px 32px; border: none; border-radius: 8px;
       font-size: 16px; font-weight: 600; cursor: pointer; transition: all 0.2s; }
.btn-primary { background: #4361ee; color: white; width: 100%; }
.btn-primary:hover { background: #3651d4; }
.btn-primary:disabled { background: #aaa; cursor: not-allowed; }
.btn-download { background: #2ecc71; color: white; margin-top: 12px; text-decoration: none;
                display: inline-block; padding: 10px 24px; border-radius: 8px; font-weight: 600; }
.btn-download:hover { background: #27ae60; }
.progress-container { margin: 16px 0; }
.progress-bar-bg { background: #e9ecef; border-radius: 10px; height: 24px; overflow: hidden; }
.progress-bar { background: linear-gradient(90deg, #4361ee, #3a86ff); height: 100%;
                border-radius: 10px; transition: width 0.3s; display: flex; align-items: center;
                justify-content: center; color: white; font-size: 12px; font-weight: 600;
                min-width: 40px; }
.status { margin-top: 8px; color: #666; font-size: 14px; }
.preview { background: #f8f9fa; border: 1px solid #e9ecef; border-radius: 8px; padding: 16px;
           margin-top: 12px; white-space: pre-wrap; font-size: 13px; line-height: 1.6;
           max-height: 400px; overflow-y: auto; font-family: "SF Mono", Monaco, monospace; }
.hidden { display: none; }
.api-key-group { display: none; }
.api-key-group.show { display: block; }
</style>
</head>
<body>
<div class="container">
    <h1>PDF 翻译工具</h1>
    <p class="subtitle">支持大型PDF (800+页) 英文翻译为中文</p>

    <div class="card">
        <h2>上传PDF</h2>
        <div class="upload-area" id="uploadArea" onclick="document.getElementById('fileInput').click()">
            <div class="upload-icon">📄</div>
            <div>点击或拖拽上传PDF文件</div>
            <div class="file-info hidden" id="fileInfo"></div>
            <input type="file" id="fileInput" accept=".pdf" onchange="handleFileSelect(this)">
        </div>
    </div>

    <div class="card">
        <h2>翻译设置</h2>
        <div class="form-group">
            <label>翻译引擎</label>
            <select id="backend" onchange="toggleApiKey()">
                <option value="google">Google翻译 (免费，需联网)</option>
                <option value="builtin">内置词典 (离线演示)</option>
                <option value="marian">MarianMT (本地离线，需安装transformers)</option>
                <option value="argos">Argos Translate (本地轻量)</option>
                <option value="deepl">DeepL (需API密钥)</option>
                <option value="claude">Claude (需API密钥，质量最高)</option>
            </select>
        </div>
        <div class="form-group api-key-group" id="apiKeyGroup">
            <label>API密钥</label>
            <input type="password" id="apiKey" placeholder="输入API密钥">
        </div>
        <div class="row">
            <div class="form-group">
                <label>起始页</label>
                <input type="number" id="startPage" value="1" min="1">
            </div>
            <div class="form-group">
                <label>结束页</label>
                <input type="number" id="endPage" value="1" min="1">
            </div>
        </div>
        <div class="row">
            <div class="form-group">
                <label>输出格式</label>
                <select id="outputFormat">
                    <option value="txt">TXT 文本文件</option>
                    <option value="pdf">PDF 文件</option>
                </select>
            </div>
            <div class="form-group">
                <label>并发线程</label>
                <input type="number" id="workers" value="2" min="1" max="8">
            </div>
        </div>
        <div class="form-group">
            <div class="checkbox-group">
                <input type="checkbox" id="bilingual">
                <label for="bilingual" style="font-weight:normal">双语对照 (原文 + 译文)</label>
            </div>
        </div>
    </div>

    <button class="btn btn-primary" id="translateBtn" onclick="startTranslation()">
        开始翻译
    </button>

    <div class="card hidden" id="resultCard">
        <h2>翻译结果</h2>
        <div class="progress-container">
            <div class="progress-bar-bg">
                <div class="progress-bar" id="progressBar" style="width: 0%">0%</div>
            </div>
        </div>
        <div class="status" id="statusText">准备中...</div>
        <div id="downloadArea" class="hidden">
            <a class="btn-download" id="downloadLink" href="#" download>下载翻译文件</a>
        </div>
        <div id="previewArea" class="hidden">
            <h3 style="margin: 16px 0 8px; font-size: 15px;">译文预览</h3>
            <div class="preview" id="previewText"></div>
        </div>
    </div>
</div>

<script>
let uploadedFile = null;
let pollTimer = null;

function handleFileSelect(input) {
    const file = input.files[0];
    if (!file) return;
    uploadedFile = file;
    const area = document.getElementById('uploadArea');
    const info = document.getElementById('fileInfo');
    area.classList.add('has-file');
    info.classList.remove('hidden');
    info.textContent = file.name + ' (' + (file.size/1024/1024).toFixed(1) + ' MB)';

    // 上传获取页数
    const fd = new FormData();
    fd.append('file', file);
    fetch('/upload', {method:'POST', body:fd})
        .then(r => r.json())
        .then(d => {
            if (d.total_pages) {
                info.textContent = file.name + ' (' + (file.size/1024/1024).toFixed(1) + ' MB, ' + d.total_pages + ' 页)';
                document.getElementById('endPage').value = d.total_pages;
                document.getElementById('endPage').max = d.total_pages;
                document.getElementById('startPage').max = d.total_pages;
            }
        });
}

function toggleApiKey() {
    const v = document.getElementById('backend').value;
    const g = document.getElementById('apiKeyGroup');
    g.classList.toggle('show', v === 'deepl' || v === 'claude');
}

function startTranslation() {
    if (!uploadedFile) { alert('请先上传PDF文件'); return; }

    const btn = document.getElementById('translateBtn');
    btn.disabled = true;
    btn.textContent = '翻译中...';

    document.getElementById('resultCard').classList.remove('hidden');
    document.getElementById('downloadArea').classList.add('hidden');
    document.getElementById('previewArea').classList.add('hidden');

    const fd = new FormData();
    fd.append('file', uploadedFile);
    fd.append('backend', document.getElementById('backend').value);
    fd.append('api_key', document.getElementById('apiKey').value);
    fd.append('start_page', document.getElementById('startPage').value);
    fd.append('end_page', document.getElementById('endPage').value);
    fd.append('output_format', document.getElementById('outputFormat').value);
    fd.append('bilingual', document.getElementById('bilingual').checked ? '1' : '0');
    fd.append('workers', document.getElementById('workers').value);

    fetch('/translate', {method:'POST', body:fd})
        .then(r => r.json())
        .then(d => { if (d.error) alert(d.error); });

    // 轮询进度
    pollTimer = setInterval(pollProgress, 500);
}

function pollProgress() {
    fetch('/progress').then(r => r.json()).then(d => {
        const pct = d.total > 0 ? Math.round(d.progress / d.total * 100) : 0;
        const bar = document.getElementById('progressBar');
        bar.style.width = pct + '%';
        bar.textContent = pct + '%';
        document.getElementById('statusText').textContent = d.status;

        if (!d.running && d.progress > 0) {
            clearInterval(pollTimer);
            const btn = document.getElementById('translateBtn');
            btn.disabled = false;
            btn.textContent = '开始翻译';

            if (d.result_file) {
                document.getElementById('downloadArea').classList.remove('hidden');
                document.getElementById('downloadLink').href = '/download?f=' + encodeURIComponent(d.result_file);
            }
            if (d.preview) {
                document.getElementById('previewArea').classList.remove('hidden');
                document.getElementById('previewText').textContent = d.preview;
            }
        }
    });
}

// 拖拽上传
const area = document.getElementById('uploadArea');
area.addEventListener('dragover', e => { e.preventDefault(); area.style.borderColor = '#4361ee'; });
area.addEventListener('dragleave', e => { area.style.borderColor = ''; });
area.addEventListener('drop', e => {
    e.preventDefault(); area.style.borderColor = '';
    const f = e.dataTransfer.files[0];
    if (f && f.name.endsWith('.pdf')) {
        document.getElementById('fileInput').files = e.dataTransfer.files;
        handleFileSelect(document.getElementById('fileInput'));
    }
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
        self.send_response(200)
        self.send_header("Content-Type", "application/octet-stream")
        self.send_header("Content-Disposition", f'attachment; filename="{filename}"')
        self.send_header("Content-Length", str(os.path.getsize(filepath)))
        self.end_headers()
        with open(filepath, "rb") as f:
            self.wfile.write(f.read())

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
