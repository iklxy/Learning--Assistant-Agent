"""Agent工具集定义"""

from typing import Optional, List, Dict, Callable, Any
from abc import ABC, abstractmethod
import json


class Tool(ABC):
    """工具基类"""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        """执行工具"""
        pass

    def to_dict(self) -> Dict:
        """将工具转换为字典格式（用于LLM调用）"""
        return {
            "name": self.name,
            "description": self.description
        }


class RetrievalTool(Tool):
    """知识库检索工具 - 与RAG系统集成"""

    def __init__(self, hybrid_retriever):
        super().__init__(
            name="retrieve_documents",
            # 更新为英文，让 Agent 更准确地理解工具用途
            description="Retrieve relevant document content from the knowledge base using hybrid search (BM25 + Semantic search)."
        )
        self.retriever = hybrid_retriever

    def execute(self, query: str, top_k: int = 5, alpha: float = 0.3) -> Dict:
        """执行文档检索"""
        try:
            results = self.retriever.search(query, top_k=top_k, alpha=alpha)

            documents = []
            for result in results:
                documents.append({
                    "chunk_id": result["chunk_id"],
                    "content": result["content"],
                    "metadata": result["metadata"],
                    "score": result["score"],
                    "source": result["metadata"].get("source", "unknown")
                })

            return {
                "success": True,
                "result": {
                    "query": query,
                    "documents": documents,
                    "total_count": len(documents)
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"检索失败: {str(e)}"  # 报错留给人类开发者看，保持中文
            }


class CodeAnalysisTool(Tool):
    """代码分析工具"""

    def __init__(self):
        super().__init__(
            name="analyze_code",
            description="Analyze and explain code snippets, providing functional descriptions and optimization suggestions."
        )

    def execute(self, code: str, language: str = "python") -> Dict:
        """分析代码"""
        try:
            analysis = self._analyze_code(code, language)
            return {
                "success": True,
                "result": {
                    "language": language,
                    "analysis": analysis,
                    "code_lines": len(code.split('\n'))
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"代码分析失败: {str(e)}"
            }

    def _analyze_code(self, code: str, language: str) -> str:
        """简单的代码分析（可扩展为更复杂的逻辑）"""
        lines = code.strip().split('\n')
        # 如果这个结果会直接传给 LLM 进行下一步思考，建议设为英文
        return f"The code snippet contains {len(lines)} lines, written in {language}. Key elements require further analysis."


class SummarizationTool(Tool):
    """内容总结工具"""

    def __init__(self, llm_interface):
        super().__init__(
            name="summarize_content",
            description="Summarize multiple document contents and generate a concise summary."
        )
        self.llm = llm_interface

    def execute(self, contents: List[str], max_length: int = 200) -> Dict:
        """总结内容"""
        try:
            if not contents:
                return {"success": False, "error": "没有可以总结的内容"}

            combined_content = "\n---\n".join(contents)

            # 更新给 LLM 的指令为英文
            prompt = f"Please summarize the following content, keeping it under {max_length} words:\n\n{combined_content}"
            summary = self.llm.call(
                system_prompt="You are an expert content summarization assistant, skilled at extracting key information.",
                user_message=prompt
            )

            return {
                "success": True,
                "result": {
                    "summary": summary,
                    "original_count": len(contents),
                    "summary_length": len(summary)
                }
            }
        except Exception as e:
            return {"success": False, "error": f"总结失败: {str(e)}"}


class QuestionDecompositionTool(Tool):
    """问题分解工具"""

    def __init__(self, llm_interface):
        super().__init__(
            name="decompose_question",
            description="Decompose a complex question into multiple manageable sub-questions."
        )
        self.llm = llm_interface

    def execute(self, question: str) -> Dict:
        """分解问题"""
        try:
            # 强化 JSON 输出的英文指令结构
            prompt = f"""Please break down the following question into 3-5 independent sub-questions:
Question: {question}

Please return strictly in JSON format:
{{"sub_questions": ["sub_question_1", "sub_question_2", ...]}}"""

            response = self.llm.call(
                system_prompt="You are a question analysis expert, skilled at breaking down complex questions into sub-questions.",
                user_message=prompt
            )

            try:
                result = json.loads(response)
                sub_questions = result.get("sub_questions", [])
            except json.JSONDecodeError:
                sub_questions = [q.strip() for q in response.split('\n') if q.strip()]

            return {
                "success": True,
                "result": {
                    "original_question": question,
                    "sub_questions": sub_questions[:5]
                }
            }
        except Exception as e:
            return {"success": False, "error": f"问题分解失败: {str(e)}"}


class ToolRegistry:
    """工具注册表 - 管理所有可用工具"""

    def __init__(self):
        self.tools: Dict[str, Tool] = {}

    def register(self, tool: Tool):
        self.tools[tool.name] = tool

    def get_tool(self, name: str) -> Optional[Tool]:
        return self.tools.get(name)

    def execute_tool(self, name: str, **kwargs) -> Dict:
        tool = self.get_tool(name)
        if not tool:
            return {"success": False, "error": f"工具 '{name}' 不存在"}
        return tool.execute(**kwargs)

    def list_tools(self) -> List[Dict]:
        return [tool.to_dict() for tool in self.tools.values()]

    def get_tools_description(self) -> str:
        """获取工具描述（交给 Agent 的清单）"""
        descriptions = []
        for tool in self.tools.values():
            descriptions.append(f"- {tool.name}: {tool.description}")
        return "\n".join(descriptions)