"""
大模型服务模块 — 封装 Ollama API 调用

提供三种调用方式：
1. generate() — 一次性生成完整回答（等待全部生成完再返回）
2. generate_stream() — 流式生成（边生成边返回，打字机效果）
3. chat() — 多轮对话（传入历史消息列表）

底层使用 ollama Python SDK 与本地 Ollama 服务通信。
Ollama 是一个本地运行大模型的工具，支持 Llama、Qwen 等开源模型。
"""
from typing import Dict, Generator, List

from ollama import Client

from app.core.config import OLLAMA_BASE_URL, DEFAULT_MODEL


class LLMService:
    """大模型服务，封装与 Ollama 的通信"""

    def __init__(self, model_name: str = None, base_url: str = None):
        """初始化 Ollama 客户端，默认读取环境变量中的地址和模型名"""
        self.client = Client(host=base_url or OLLAMA_BASE_URL)
        self.model_name = model_name or DEFAULT_MODEL

    def generate(self, prompt: str) -> str:
        """一次性生成：等模型全部生成完再返回完整文本"""
        try:
            response = self.client.generate(model=self.model_name, prompt=prompt, stream=False)
            return response["response"]
        except Exception as exc:
            raise RuntimeError(f"LLM 生成失败: {exc}") from exc

    def generate_stream(self, prompt: str) -> Generator[str, None, None]:
        """流式生成：每生成一个字就yield一个字，实现打字机效果"""
        try:
            for chunk in self.client.generate(model=self.model_name, prompt=prompt, stream=True):
                text = chunk.get("response", "")
                if text:
                    yield text
        except Exception as exc:
            raise RuntimeError(f"LLM 流式生成失败: {exc}") from exc

    def chat(self, messages: List[Dict[str, str]]) -> str:
        """多轮对话：传入消息列表 [{"role":"user","content":"..."}]，返回模型回复"""
        try:
            response = self.client.chat(model=self.model_name, messages=messages, stream=False)
            return response["message"]["content"]
        except Exception as exc:
            raise RuntimeError(f"LLM 聊天失败: {exc}") from exc