"""断点续传模块 - 保存和恢复翻译进度"""

import json
import os


class Checkpoint:
    """管理翻译进度的检查点

    将已翻译的页面保存到JSON文件，支持中断后恢复翻译。
    """

    def __init__(self, checkpoint_path: str):
        self.path = checkpoint_path
        self._data = self._load()

    def _load(self) -> dict:
        if os.path.isfile(self.path):
            with open(self.path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"completed_pages": {}, "metadata": {}}

    def save(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, ensure_ascii=False, indent=2)

    def set_metadata(self, pdf_path: str, total_pages: int, backend: str):
        self._data["metadata"] = {
            "pdf_path": os.path.abspath(pdf_path),
            "total_pages": total_pages,
            "backend": backend,
        }

    def get_completed_pages(self) -> set[int]:
        """获取已完成翻译的页码集合"""
        return set(int(k) for k in self._data["completed_pages"].keys())

    def save_page(self, page_num: int, original: str, translated: str):
        """保存单页翻译结果"""
        self._data["completed_pages"][str(page_num)] = {
            "original": original,
            "translated": translated,
        }

    def get_all_pages(self) -> dict[int, dict]:
        """获取所有已翻译的页面数据"""
        return {
            int(k): v for k, v in self._data["completed_pages"].items()
        }

    def get_progress(self) -> tuple[int, int]:
        """返回 (已完成页数, 总页数)"""
        total = self._data["metadata"].get("total_pages", 0)
        done = len(self._data["completed_pages"])
        return done, total

    def clear(self):
        """清除检查点"""
        self._data = {"completed_pages": {}, "metadata": {}}
        if os.path.isfile(self.path):
            os.remove(self.path)
