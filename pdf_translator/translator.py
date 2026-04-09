"""翻译引擎模块 - 支持多种翻译后端，带重试和速率限制"""

import time
import re
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, as_completed


class TranslatorBackend(ABC):
    """翻译后端基类"""

    @abstractmethod
    def translate(self, text: str) -> str:
        """翻译单段文本"""
        ...

    @abstractmethod
    def name(self) -> str:
        ...


class GoogleTranslateBackend(TranslatorBackend):
    """Google翻译后端（免费，使用deep-translator库）"""

    def __init__(self):
        from deep_translator import GoogleTranslator
        self._translator = GoogleTranslator(source="en", target="zh-CN")

    def translate(self, text: str) -> str:
        if not text or not text.strip():
            return ""
        # deep-translator 单次最多5000字符，需要分段
        chunks = self._split_text(text, max_len=4900)
        results = []
        for chunk in chunks:
            result = self._translate_with_retry(chunk)
            results.append(result)
        return "".join(results)

    def _translate_with_retry(self, text: str, max_retries: int = 3) -> str:
        for attempt in range(max_retries):
            try:
                return self._translator.translate(text)
            except Exception as e:
                if attempt < max_retries - 1:
                    wait = 2 ** (attempt + 1)
                    time.sleep(wait)
                else:
                    raise RuntimeError(f"翻译失败（重试{max_retries}次后）: {e}") from e

    def _split_text(self, text: str, max_len: int) -> list[str]:
        """按句子边界分割长文本"""
        if len(text) <= max_len:
            return [text]

        chunks = []
        current = ""
        # 按段落分割
        paragraphs = text.split("\n")
        for para in paragraphs:
            if len(current) + len(para) + 1 <= max_len:
                current += para + "\n"
            else:
                if current:
                    chunks.append(current)
                # 如果单段落也超长，按句子分
                if len(para) > max_len:
                    sentences = re.split(r'(?<=[.!?])\s+', para)
                    current = ""
                    for sent in sentences:
                        if len(current) + len(sent) + 1 <= max_len:
                            current += sent + " "
                        else:
                            if current:
                                chunks.append(current)
                            current = sent + " "
                else:
                    current = para + "\n"
        if current.strip():
            chunks.append(current)
        return chunks

    def name(self) -> str:
        return "Google Translate"


class DeepLBackend(TranslatorBackend):
    """DeepL翻译后端（需要API密钥）"""

    def __init__(self, api_key: str):
        self._api_key = api_key

    def translate(self, text: str) -> str:
        if not text or not text.strip():
            return ""
        from deep_translator import DeeplTranslator
        translator = DeeplTranslator(
            api_key=self._api_key, source="en", target="zh"
        )
        return translator.translate(text)

    def name(self) -> str:
        return "DeepL"


class ClaudeBackend(TranslatorBackend):
    """Claude API翻译后端（高质量，需要API密钥）"""

    def __init__(self, api_key: str, model: str = "claude-sonnet-4-20250514"):
        import anthropic
        self._client = anthropic.Anthropic(api_key=api_key)
        self._model = model

    def translate(self, text: str) -> str:
        if not text or not text.strip():
            return ""
        response = self._client.messages.create(
            model=self._model,
            max_tokens=8192,
            messages=[
                {
                    "role": "user",
                    "content": (
                        "Please translate the following English text to Chinese "
                        "(Simplified). Only output the translation, no explanations.\n\n"
                        f"{text}"
                    ),
                }
            ],
        )
        return response.content[0].text

    def name(self) -> str:
        return f"Claude ({self._model})"


class MarianBackend(TranslatorBackend):
    """Helsinki-NLP MarianMT 本地翻译后端（完全离线，无需API）

    使用 Helsinki-NLP/opus-mt-en-zh 模型，首次运行自动下载（~300MB）。
    支持GPU加速，CPU上也有不错的速度。
    """

    def __init__(self, model_name: str = "Helsinki-NLP/opus-mt-en-zh", device: str | None = None):
        from transformers import MarianMTModel, MarianTokenizer
        import torch

        print(f"  加载本地翻译模型: {model_name} ...")
        self._tokenizer = MarianTokenizer.from_pretrained(model_name)
        self._model = MarianMTModel.from_pretrained(model_name)

        if device:
            self._device = device
        elif torch.cuda.is_available():
            self._device = "cuda"
        else:
            self._device = "cpu"

        self._model.to(self._device)
        self._model.eval()
        self._model_name = model_name
        print(f"  模型已加载，设备: {self._device}")

    def translate(self, text: str) -> str:
        if not text or not text.strip():
            return ""
        # MarianMT 对输入长度有限制（~512 tokens），需要分段翻译
        sentences = self._split_into_sentences(text)
        batches = self._make_batches(sentences, max_tokens=400)
        translated_parts = []
        for batch in batches:
            translated_parts.extend(self._translate_batch(batch))
        return "\n".join(translated_parts)

    def _translate_batch(self, sentences: list[str]) -> list[str]:
        """批量翻译多个句子（提升GPU利用率）"""
        import torch

        encoded = self._tokenizer(
            sentences, return_tensors="pt", padding=True, truncation=True, max_length=512
        ).to(self._device)
        with torch.no_grad():
            output_ids = self._model.generate(**encoded, max_length=512)
        return self._tokenizer.batch_decode(output_ids, skip_special_tokens=True)

    def _split_into_sentences(self, text: str) -> list[str]:
        """将文本分割为句子"""
        sentences = []
        for paragraph in text.split("\n"):
            paragraph = paragraph.strip()
            if not paragraph:
                continue
            # 按句号/问号/感叹号分句
            parts = re.split(r'(?<=[.!?])\s+', paragraph)
            for part in parts:
                part = part.strip()
                if part:
                    sentences.append(part)
        return sentences

    def _make_batches(self, sentences: list[str], max_tokens: int = 400) -> list[list[str]]:
        """将句子分组为批次，每批不超过max_tokens个token"""
        batches = []
        current_batch = []
        current_len = 0
        for sent in sentences:
            token_len = len(self._tokenizer.encode(sent))
            if current_len + token_len > max_tokens and current_batch:
                batches.append(current_batch)
                current_batch = []
                current_len = 0
            current_batch.append(sent)
            current_len += token_len
        if current_batch:
            batches.append(current_batch)
        return batches

    def name(self) -> str:
        return f"MarianMT 本地模型 ({self._device})"


class ArgosBackend(TranslatorBackend):
    """Argos Translate 本地翻译后端（完全离线，轻量级）

    使用 argostranslate 库，首次运行自动下载语言包。
    轻量级，适合CPU环境。
    """

    def __init__(self):
        import argostranslate.package
        import argostranslate.translate

        # 检查并安装英→中语言包
        argostranslate.package.update_package_index()
        available = argostranslate.package.get_available_packages()
        en_zh = next(
            (p for p in available if p.from_code == "en" and p.to_code == "zh"),
            None,
        )
        if en_zh is None:
            raise RuntimeError("找不到 Argos en→zh 语言包，请检查 argostranslate 安装")

        installed_codes = {
            (p.from_code, p.to_code)
            for p in argostranslate.package.get_installed_packages()
        }
        if ("en", "zh") not in installed_codes:
            print("  首次使用，正在下载 Argos en→zh 语言包...")
            argostranslate.package.install_from_path(en_zh.download())
            print("  语言包安装完成")

        self._translate_fn = argostranslate.translate.translate

    def translate(self, text: str) -> str:
        if not text or not text.strip():
            return ""
        return self._translate_fn(text, "en", "zh")

    def name(self) -> str:
        return "Argos Translate 本地模型"


def create_backend(
    backend_name: str,
    api_key: str | None = None,
    device: str | None = None,
) -> TranslatorBackend:
    """工厂方法：创建翻译后端

    Args:
        backend_name: "google", "deepl", "claude", "marian", "argos"
        api_key: API密钥（google/marian/argos不需要）
        device: 本地模型运行设备（仅marian有效）
    """
    if backend_name == "google":
        return GoogleTranslateBackend()
    elif backend_name == "deepl":
        if not api_key:
            raise ValueError("DeepL翻译需要提供API密钥 (--api-key)")
        return DeepLBackend(api_key)
    elif backend_name == "claude":
        if not api_key:
            raise ValueError("Claude翻译需要提供API密钥 (--api-key)")
        return ClaudeBackend(api_key)
    elif backend_name == "marian":
        return MarianBackend(device=device)
    elif backend_name == "argos":
        return ArgosBackend()
    else:
        raise ValueError(
            f"不支持的翻译后端: {backend_name}\n"
            f"可选: google, deepl, claude, marian（本地）, argos（本地）"
        )


class BatchTranslator:
    """批量翻译器 - 支持并发翻译和速率控制"""

    def __init__(
        self,
        backend: TranslatorBackend,
        workers: int = 4,
        delay: float = 0.5,
    ):
        """
        Args:
            backend: 翻译后端
            workers: 并发工作线程数
            delay: 每次翻译请求之间的延迟（秒）
        """
        self.backend = backend
        self.workers = workers
        self.delay = delay

    def translate_batch(
        self, pages: list[tuple[int, str]]
    ) -> dict[int, str]:
        """并发翻译多页文本

        Args:
            pages: [(页码, 原文), ...] 的列表

        Returns:
            {页码: 译文} 的字典
        """
        results = {}

        if self.workers <= 1:
            # 单线程顺序翻译
            for page_num, text in pages:
                translated = self.backend.translate(text)
                results[page_num] = translated
                if self.delay > 0:
                    time.sleep(self.delay)
            return results

        # 多线程并发翻译
        with ThreadPoolExecutor(max_workers=self.workers) as executor:
            future_to_page = {}
            for i, (page_num, text) in enumerate(pages):
                future = executor.submit(self._translate_one, text, i)
                future_to_page[future] = page_num

            for future in as_completed(future_to_page):
                page_num = future_to_page[future]
                results[page_num] = future.result()

        return results

    def _translate_one(self, text: str, index: int) -> str:
        """翻译单段文本，带延迟控制"""
        if self.delay > 0:
            time.sleep(self.delay * index * 0.1)  # 错开请求时间
        return self.backend.translate(text)
