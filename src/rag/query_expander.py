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

        self.system_prompt = """You are a query rewriting expert. Rewrite the user's question into 5 completely different query formulations from different perspectives.

Requirements:
1. Direct Query: Remove all question words, keep core concepts only
   Example: "What is const" → "const"

2. Full Terms: Use complete official terminology and technical names
   Example: "What is const" → "const qualifier C++ type system"

3. Use Cases: Emphasize use cases, features, and how it works
   Example: "What is const" → "const correctness and const propagation in C++"

4. Comparison: Compare with related concepts or mention applications
   Example: "What is const" → "const vs constexpr vs const_cast in C++"

5. Implementation Details: Dive into deeper theory and internal mechanisms
   Example: "What is const" → "const semantics compiler optimization and memory safety"

Return format: One query per line (no numbering, no other symbols)"""

    def expand_query(self, query: str) -> List[str]:
        """
        Use LLM to rewrite query and generate multiple query variants.

        Parameters:
          query - Original query text

        Returns:
          List of original query and rewritten query variants
        """
        print(f"Rewriting query: {query}")

        try:
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=f"Please rewrite this query: {query}")
            ]

            response = self.llm.invoke(messages)
            expanded_queries = response.content.strip().split('\n')

            expanded_queries = [q.strip() for q in expanded_queries if q.strip()]

            print(f"Query rewriting completed. Generated {len(expanded_queries)} query variants")
            for i, q in enumerate(expanded_queries, 1):
                print(f"  {i}. {q}")

            return expanded_queries

        except Exception as e:
            print(f"Query rewriting failed: {e}")
            return [query]
