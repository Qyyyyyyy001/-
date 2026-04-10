"""翻译引擎模块 - 支持多种翻译后端，带重试和速率限制"""
from __future__ import annotations

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


class BuiltinDictBackend(TranslatorBackend):
    """内置词典翻译后端（无需联网、无需下载，开箱即用）

    基于高频英语词汇词典 + 短语模式匹配。
    翻译质量有限，仅用于演示和测试整个翻译流程。
    生产环境建议使用 marian/google/claude 等后端。
    """

    def __init__(self):
        # 高频词汇词典（覆盖常见学术/技术用语）
        self._dict = {
            # 常用词
            "the": "", "a": "一个", "an": "一个",
            "is": "是", "are": "是", "was": "是", "were": "是",
            "be": "是", "been": "已经", "being": "正在",
            "have": "有", "has": "有", "had": "有",
            "do": "做", "does": "做", "did": "做",
            "will": "将", "would": "会", "shall": "将",
            "should": "应该", "can": "能", "could": "能够",
            "may": "可能", "might": "可能", "must": "必须",
            "and": "和", "or": "或", "but": "但是",
            "not": "不", "no": "没有", "nor": "也不",
            "if": "如果", "then": "那么", "else": "否则",
            "when": "当", "where": "哪里", "while": "当...时",
            "that": "那个", "this": "这个", "these": "这些", "those": "那些",
            "it": "它", "its": "它的", "they": "他们", "their": "他们的",
            "them": "他们", "we": "我们", "our": "我们的",
            "he": "他", "his": "他的", "she": "她", "her": "她的",
            "i": "我", "my": "我的", "me": "我", "you": "你", "your": "你的",
            "in": "在...中", "on": "在...上", "at": "在",
            "to": "到", "for": "为了", "with": "与",
            "from": "从", "by": "由", "of": "的",
            "as": "作为", "into": "进入", "about": "关于",
            "between": "之间", "through": "通过", "during": "在...期间",
            "before": "之前", "after": "之后", "above": "之上",
            "below": "之下", "under": "在...下", "over": "超过",
            "up": "上", "down": "下", "out": "外",
            "new": "新的", "old": "旧的", "first": "第一",
            "last": "最后", "long": "长的", "great": "伟大的",
            "little": "小的", "own": "自己的", "other": "其他的",
            "right": "正确的", "big": "大的", "high": "高的",
            "small": "小的", "large": "大的", "good": "好的",
            "bad": "坏的", "important": "重要的", "different": "不同的",
            "same": "相同的", "early": "早期的", "possible": "可能的",
            "able": "能够的", "many": "许多", "much": "很多",
            "more": "更多", "most": "最", "very": "非常",
            "also": "也", "even": "甚至", "just": "只是",
            "only": "仅仅", "now": "现在", "still": "仍然",
            "already": "已经", "well": "好", "too": "也",
            "how": "如何", "what": "什么", "which": "哪个",
            "who": "谁", "why": "为什么",
            "all": "所有", "each": "每个", "every": "每个",
            "both": "两者", "few": "少数", "some": "一些",
            "any": "任何", "such": "如此", "than": "比",
            "so": "所以", "because": "因为", "however": "然而",
            "although": "虽然", "since": "自从", "therefore": "因此",
            "today": "今天", "world": "世界", "life": "生活",
            "way": "方式", "day": "天", "time": "时间",
            "year": "年", "people": "人们", "man": "人",
            "woman": "女人", "child": "孩子", "children": "孩子们",
            "thing": "事物", "place": "地方", "work": "工作",
            "part": "部分", "case": "情况", "number": "数字",
            "point": "点", "fact": "事实", "hand": "手",
            "system": "系统", "program": "程序", "question": "问题",
            "government": "政府", "company": "公司", "group": "团体",
            "problem": "问题", "example": "例子", "country": "国家",
            "end": "结束", "head": "头", "house": "房子",
            "word": "词", "money": "钱", "story": "故事",
            "information": "信息", "power": "力量", "water": "水",
            "history": "历史", "change": "变化", "interest": "兴趣",
            "development": "发展", "experience": "经验", "result": "结果",
            "idea": "想法", "research": "研究", "study": "学习",
            "book": "书", "eye": "眼睛", "state": "状态",
            "family": "家庭", "student": "学生", "school": "学校",
            "business": "商业", "market": "市场", "industry": "行业",
            "side": "方面", "service": "服务", "area": "领域",
            "society": "社会", "line": "线", "name": "名字",
            "use": "使用", "make": "制造", "find": "发现",
            "give": "给", "tell": "告诉", "take": "拿",
            "come": "来", "go": "去", "see": "看",
            "know": "知道", "get": "获得", "think": "认为",
            "say": "说", "look": "看", "want": "想要",
            "need": "需要", "become": "成为", "leave": "离开",
            "put": "放", "mean": "意味着", "keep": "保持",
            "let": "让", "begin": "开始", "seem": "似乎",
            "help": "帮助", "show": "展示", "turn": "转变",
            "play": "播放", "run": "运行", "move": "移动",
            "try": "尝试", "ask": "询问", "start": "开始",
            "learn": "学习", "create": "创建", "provide": "提供",
            "include": "包括", "continue": "继续", "set": "设置",
            "follow": "跟随", "call": "调用", "read": "阅读",
            "allow": "允许", "lead": "引导", "live": "生活",
            "stand": "站立", "happen": "发生", "carry": "携带",
            "talk": "说话", "produce": "生产", "hold": "持有",
            "grow": "增长", "open": "打开", "write": "写",
            "offer": "提供", "remember": "记住", "consider": "考虑",
            "appear": "出现", "buy": "购买", "wait": "等待",
            "serve": "服务", "remain": "保持", "suggest": "建议",
            "raise": "提高", "pass": "通过", "reach": "到达",
            "kill": "杀死", "require": "需要", "report": "报告",
            "decide": "决定", "build": "建造", "stay": "留下",
            "fall": "下降", "cut": "削减", "describe": "描述",
            "agree": "同意", "develop": "开发", "understand": "理解",
            "support": "支持", "recognize": "识别",
            # 技术/学术词汇
            "technology": "技术", "computer": "计算机", "data": "数据",
            "software": "软件", "hardware": "硬件", "network": "网络",
            "internet": "互联网", "algorithm": "算法", "model": "模型",
            "intelligence": "智能", "artificial": "人工的",
            "machine": "机器", "learning": "学习", "deep": "深度",
            "neural": "神经", "science": "科学", "analysis": "分析",
            "process": "过程", "method": "方法", "approach": "方法",
            "theory": "理论", "design": "设计", "performance": "性能",
            "application": "应用", "applications": "应用",
            "function": "函数", "language": "语言", "natural": "自然的",
            "image": "图像", "images": "图像", "video": "视频",
            "recognition": "识别", "generation": "生成", "training": "训练",
            "processing": "处理", "understanding": "理解",
            "optimization": "优化", "classification": "分类",
            "detection": "检测", "prediction": "预测",
            "accuracy": "准确率", "error": "错误", "loss": "损失",
            "feature": "特征", "features": "特征",
            "input": "输入", "output": "输出", "layer": "层",
            "parameter": "参数", "parameters": "参数",
            "dataset": "数据集", "database": "数据库",
            "framework": "框架", "architecture": "架构",
            "transformer": "变换器", "transforming": "变革",
            "attention": "注意力", "memory": "内存",
            "healthcare": "医疗保健", "diagnosis": "诊断",
            "finance": "金融", "fraud": "欺诈",
            "transportation": "交通运输", "education": "教育",
            "personalized": "个性化的",
            "chatbots": "聊天机器人", "virtual": "虚拟的",
            "assistants": "助手", "superhuman": "超人的",
            "identify": "识别", "objects": "对象",
            "faces": "人脸", "revolution": "革命",
            "breakthrough": "突破", "investment": "投资",
            "reignited": "重新点燃", "optimistic": "乐观的",
            "researchers": "研究人员", "conference": "会议",
            "founded": "创立", "college": "学院",
            "creative": "创造性的", "content": "内容",
            "impact": "影响", "aspect": "方面",
            "human": "人类", "across": "跨越",
            "recent": "最近的", "recently": "最近",
            "field": "领域", "progress": "进展",
            "slower": "较慢", "expected": "预期的",
            "periods": "时期", "known": "已知的",
            "winters": "寒冬", "self-driving": "自动驾驶",
            "cars": "汽车", "millions": "数百万",
            "every": "每个", "vision": "视觉",
            "algorithms": "算法", "recognize": "识别",
            "generate": "生成", "beginning": "开始",
            "felt": "感受到", "match": "匹配",
            "soon": "很快", "leading": "导致",
            "enables": "使能", "used": "使用",
        }

    def translate(self, text: str) -> str:
        if not text or not text.strip():
            return ""
        paragraphs = text.split("\n")
        translated_paragraphs = []
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            translated_paragraphs.append(self._translate_paragraph(para))
        return "\n".join(translated_paragraphs)

    def _translate_paragraph(self, text: str) -> str:
        # 按句子分割
        sentences = re.split(r'(?<=[.!?])\s+', text)
        translated = []
        for sent in sentences:
            translated.append(self._translate_sentence(sent))
        return "".join(translated)

    def _translate_sentence(self, sentence: str) -> str:
        # 简单的词级翻译
        words = re.findall(r"[a-zA-Z'-]+|[^a-zA-Z\s]+|\s+", sentence)
        result = []
        for word in words:
            lower = word.lower().strip(".,;:!?\"'()-")
            if lower in self._dict:
                translated = self._dict[lower]
                if translated:  # 跳过空翻译（如 "the"）
                    result.append(translated)
            elif word.strip():
                result.append(word)
        return "".join(result) + "。"

    def name(self) -> str:
        return "内置词典 (演示用，建议正式使用时换 marian/google)"


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
    elif backend_name == "builtin":
        return BuiltinDictBackend()
    else:
        raise ValueError(
            f"不支持的翻译后端: {backend_name}\n"
            f"可选: google, deepl, claude, marian（本地）, argos（本地）, builtin（内置演示）"
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
