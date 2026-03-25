from typing import List
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage


load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv('OPENAI_API_KEY')
os.environ["OPENAI_API_BASE"] = os.getenv('OPENAI_API_BASE')

class LLMQueryExpander:
    """基于LLM的查询改写器"""

    def __init__(self):
        """
        初始化LLM查询改写器

        """

        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.7
        )

        self.system_prompt = """你是一个查询改写专家。将用户的问题改写成5个**完全不同视角**的查询表述。

要求：
1. 直接查询：移除所有疑问词，保留核心概念
   例："什么是STL" → "STL"

2. 专业术语：使用完整的官方术语或英文表述
   例："什么是STL" → "Standard Template Library"

3. 功能特性：强调功能、特性、原理
   例："什么是STL" → "STL容器和算法库的功能特性"

4. 对比应用：与其他相关概念的对比或应用场景
   例："什么是STL" → "STL与数组链表的区别和应用"

5. 深度理解：更深层的理论或内部实现
   例："什么是STL" → "STL迭代器和模板元编程原理"

返回格式：每行一个查询（无编号，无其他符号）"""

    def expand_query(self, query: str) -> List[str]:
        """
        使用LLM改写查询，生成多个查询变体

        参数：
          query - 原始查询文本

        返回：
          包含原始查询和多个改写查询的列表
        """
        print(f"正在改写查询: {query}")

        try:
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=f"请改写这个查询：{query}")
            ]

            response = self.llm.invoke(messages)
            expanded_queries = response.content.strip().split('\n')

            expanded_queries = [q.strip() for q in expanded_queries if q.strip()]

            print(f"查询改写完成，生成 {len(expanded_queries)} 个查询变体")
            for i, q in enumerate(expanded_queries, 1):
                print(f"  {i}. {q}")

            return expanded_queries

        except Exception as e:
            print(f"查询改写失败: {e}")
            return [query]
