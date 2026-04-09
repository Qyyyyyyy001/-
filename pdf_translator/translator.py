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


def create_backend(backend_name: str, api_key: str | None = None) -> TranslatorBackend:
    """工厂方法：创建翻译后端

    Args:
        backend_name: "google", "deepl", "claude"
        api_key: API密钥（google不需要）
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
    else:
        raise ValueError(f"不支持的翻译后端: {backend_name}，可选: google, deepl, claude")


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
