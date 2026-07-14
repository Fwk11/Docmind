from typing import Dict, Generator, List

from ollama import Client

from app.core.config import OLLAMA_BASE_URL, DEFAULT_MODEL


class LLMService:

    def __init__(self, model_name: str = None, base_url: str = None):
        self.client = Client(host=base_url or OLLAMA_BASE_URL)
        self.model_name = model_name or DEFAULT_MODEL

    def generate(self, prompt: str) -> str:
        try:
            response = self.client.generate(model=self.model_name, prompt=prompt, stream=False)
            return response["response"]
        except Exception as exc:
            raise RuntimeError(f"LLM 生成失败: {exc}") from exc

    def generate_stream(self, prompt: str) -> Generator[str, None, None]:
        try:
            for chunk in self.client.generate(model=self.model_name, prompt=prompt, stream=True):
                text = chunk.get("response", "")
                if text:
                    yield text
        except Exception as exc:
            raise RuntimeError(f"LLM 流式生成失败: {exc}") from exc

    def chat(self, messages: List[Dict[str, str]]) -> str:
        try:
            response = self.client.chat(model=self.model_name, messages=messages, stream=False)
            return response["message"]["content"]
        except Exception as exc:
            raise RuntimeError(f"LLM 聊天失败: {exc}") from exc