"""LLM调用接口封装"""

from typing import Optional, List, Dict
import os
from dotenv import load_dotenv

# 从根目录 .env 文件加载环境变量
load_dotenv()

class LLMInterface:
    """LLM调用接口基类"""

    def __init__(self, api_key: Optional[str] = None, model: str = None, base_url: Optional[str] = None):
        self.api_key = api_key or os.getenv("LLM_API_KEY")
        self.base_url = base_url or os.getenv("LLM_BASE_URL")
        # 默认模型修改为 OpenAI 系列，保持逻辑一致
        self.model = model or os.getenv("LLM_MODEL", "gpt-3.5-turbo")
        self.max_tokens = 2048
        self.temperature = 0.7

    def call(
        self,
        system_prompt: str,
        user_message: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        调用LLM API

        Args:
            system_prompt: 系统提示词
            user_message: 用户消息
            temperature: 采样温度（0-1）
            max_tokens: 最大生成token数

        Returns:
            LLM生成的响应文本
        """
        raise NotImplementedError("子类需要实现此方法")

    def set_temperature(self, temperature: float):
        """设置采样温度"""
        self.temperature = max(0, min(1, temperature))

    def set_max_tokens(self, max_tokens: int):
        """设置最大token数"""
        self.max_tokens = max_tokens


class OpenAIInterface(LLMInterface):
    """OpenAI API调用实现"""

    def __init__(self):
        # 默认使用 gpt-4，自动从 .env 读取 OPENAI_API_KEY
        api_key = os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("OPENAI_API_BASE")
        if not api_key:
            raise ValueError("未找到 OPENAI_API_KEY 环境变量，请检查 .env 文件")
        super().__init__(api_key, model="gpt-4")
        self.base_url = base_url
        self._init_client()

    def _init_client(self):
        """初始化OpenAI客户端"""
        try:
            from openai import OpenAI
            # 使用新版本的 OpenAI 客户端
            if self.base_url:
                self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
            else:
                self.client = OpenAI(api_key=self.api_key)
        except ImportError:
            raise ImportError("请安装 openai SDK: pip install openai")

    def call(
        self,
        system_prompt: str,
        user_message: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """调用OpenAI API（兼容 openai >= 1.0.0）"""
        temp = temperature or self.temperature
        tokens = max_tokens or self.max_tokens

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                max_tokens=tokens,
                temperature=temp,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            raise RuntimeError(f"OpenAI API调用失败: {str(e)}")