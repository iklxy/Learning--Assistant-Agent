"""Agent核心逻辑 - 推理决策和工具调用"""

from typing import Optional, Dict, List, Any
import json
import re

from .memory import ConversationMemory
from .llm_interface import OpenAIInterface
from .tools import ToolRegistry
from .prompt import (
    SYSTEM_PROMPT,
    TOOL_INSTRUCTION,
    CONTEXT_INSTRUCTION,
    REASONING_INSTRUCTION,
    FOLLOW_UP_PROMPT
)


class Agent:
    """Learning Assistant Agent - 学习助手Agent核心类"""

    def __init__(
        self,
        tool_registry: ToolRegistry,
        llm_interface: Optional[OpenAIInterface] = None,
        memory: Optional[ConversationMemory] = None,
        max_iterations: int = 5
    ):
        """
        初始化Agent

        Args:
            tool_registry: 工具注册表
            llm_interface: LLM接口（默认创建OpenAI实例）
            memory: 对话记忆（默认创建新实例）
            max_iterations: 最大推理迭代次数，防止无限循环
        """
        self.tool_registry = tool_registry
        self.llm = llm_interface or OpenAIInterface()
        self.memory = memory or ConversationMemory()
        self.max_iterations = max_iterations

        # 配置参数
        self.enable_retrieval = True  # 是否启用文档检索
        self.enable_reasoning = True  # 是否启用链式推理
        self.enable_followup = True   # 是否启用后续建议

    def run(self, user_query: str, use_tools: bool = True) -> str:
        """
        运行Agent处理用户查询

        Args:
            user_query: 用户的问题或查询
            use_tools: 是否允许使用工具

        Returns:
            Agent的最终回应
        """
        print(f"[Agent] Processing query: {user_query}")

        # 1. 添加用户消息到记忆
        self.memory.add_message("user", user_query)

        # 2. 初始化Agent思路
        context = ""
        iteration = 0

        # 3. 主推理循环
        while iteration < self.max_iterations:
            iteration += 1
            print(f"[Agent] Iteration {iteration}/{self.max_iterations}")

            # 4. 构建提示词
            system_prompt = self._build_system_prompt(use_tools)
            user_message = self._build_user_message(user_query, context, iteration)

            # 5. 调用LLM
            try:
                response = self.llm.call(
                    system_prompt=system_prompt,
                    user_message=user_message,
                    temperature=0.7
                )
            except Exception as e:
                error_msg = f"LLM调用失败: {str(e)}"
                print(f"[Agent Error] {error_msg}")
                return error_msg

            print(f"[Agent] LLM Response: {response[:200]}...")

            # 6. 解析LLM响应，检查是否需要调用工具
            if use_tools:
                tool_calls = self._parse_tool_calls(response)

                if tool_calls:
                    print(f"[Agent] Detected {len(tool_calls)} tool call(s)")

                    # 7. 执行工具调用
                    tool_results = self._execute_tool_calls(tool_calls)

                    # 8. 将工具结果作为新的上下文
                    context = self._format_tool_results(tool_results)

                    # 继续迭代
                    continue

            # 9. 如果没有工具调用，或者到达最大迭代次数，返回最终答案
            final_response = self._extract_final_answer(response)

            # 10. 添加助手响应到记忆
            self.memory.add_message("assistant", final_response)

            # 11. 打印内存统计
            stats = self.memory.get_summary_stats()
            print(f"[Agent] Memory Stats: {stats['total_messages']} messages, "
                  f"{stats['total_tokens']} tokens used ({stats['token_usage_percent']:.1f}%)")

            return final_response

        # 12. 如果超过最大迭代，返回错误
        error_msg = f"Agent reached maximum iterations ({self.max_iterations})"
        print(f"[Agent Error] {error_msg}")
        return error_msg

    def _build_system_prompt(self, use_tools: bool) -> str:
        """
        构建系统提示词

        Args:
            use_tools: 是否允许使用工具

        Returns:
            完整的系统提示词
        """
        prompts = [SYSTEM_PROMPT]

        if self.enable_reasoning:
            prompts.append(REASONING_INSTRUCTION)

        if use_tools and self.tool_registry.list_tools():
            prompts.append(TOOL_INSTRUCTION)
            tools_desc = self.tool_registry.get_tools_description()
            prompts.append(f"Available tools:\n{tools_desc}")

        if self.enable_followup:
            prompts.append(FOLLOW_UP_PROMPT)

        return "\n\n".join(prompts)

    def _build_user_message(self, user_query: str, context: str, iteration: int) -> str:
        """
        构建用户消息

        Args:
            user_query: 原始用户查询
            context: 当前的RAG上下文
            iteration: 当前迭代次数

        Returns:
            格式化的用户消息
        """
        message_parts = []

        # 第一次迭代：原始查询
        if iteration == 1:
            message_parts.append(f"User query: {user_query}")

            # 如果启用检索，自动检索相关文档
            if self.enable_retrieval and self.tool_registry.get_tool("retrieve_documents"):
                message_parts.append("\nPlease first retrieve relevant documents, then provide your answer.")
        else:
            # 后续迭代：继续处理
            message_parts.append(f"Based on the previous context, continue answering: {user_query}")

        # 如果有RAG上下文，添加到消息中
        if context:
            message_parts.append(CONTEXT_INSTRUCTION.format(context=context))

        return "\n\n".join(message_parts)

    def _parse_tool_calls(self, response: str) -> List[Dict[str, Any]]:
        """
        从LLM响应中解析工具调用

        格式: <tool_call>
              <name>tool_name</name>
              <input>{"param1": "value1"}</input>
              </tool_call>

        Args:
            response: LLM的响应文本

        Returns:
            工具调用列表，每项包含 name 和 params
        """
        tool_calls = []

        # 正则表达式匹配工具调用块
        pattern = r'<tool_call>\s*<name>(.*?)</name>\s*<input>(.*?)</input>\s*</tool_call>'
        matches = re.finditer(pattern, response, re.DOTALL)

        for match in matches:
            tool_name = match.group(1).strip()
            input_str = match.group(2).strip()

            try:
                # 解析JSON参数
                params = json.loads(input_str)
                tool_calls.append({
                    "name": tool_name,
                    "params": params
                })
                print(f"[Tool Parser] Found tool call: {tool_name} with params: {params}")
            except json.JSONDecodeError as e:
                print(f"[Tool Parser Error] Failed to parse JSON for {tool_name}: {str(e)}")

        return tool_calls

    def _execute_tool_calls(self, tool_calls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        执行工具调用

        Args:
            tool_calls: 工具调用列表

        Returns:
            工具执行结果列表
        """
        results = []

        for tool_call in tool_calls:
            tool_name = tool_call["name"]
            params = tool_call["params"]

            print(f"[Tool Execution] Executing {tool_name} with {params}")

            try:
                # 调用工具
                result = self.tool_registry.execute_tool(tool_name, **params)
                results.append({
                    "tool": tool_name,
                    "success": result.get("success", False),
                    "result": result.get("result"),
                    "error": result.get("error")
                })

                if result.get("success"):
                    print(f"[Tool Result] {tool_name} executed successfully")
                else:
                    print(f"[Tool Result] {tool_name} failed: {result.get('error')}")
            except Exception as e:
                print(f"[Tool Exception] Error executing {tool_name}: {str(e)}")
                results.append({
                    "tool": tool_name,
                    "success": False,
                    "error": str(e)
                })

        return results

    def _format_tool_results(self, tool_results: List[Dict[str, Any]]) -> str:
        """
        格式化工具执行结果，用于后续LLM调用

        Args:
            tool_results: 工具执行结果列表

        Returns:
            格式化的结果文本
        """
        formatted_parts = []

        for result in tool_results:
            tool_name = result["tool"]

            if result["success"]:
                # 成功的工具调用
                formatted_parts.append(f"[{tool_name}] Successfully retrieved:")

                # 根据工具类型格式化结果
                if tool_name == "retrieve_documents":
                    docs = result["result"].get("documents", [])
                    for doc in docs:
                        formatted_parts.append(f"\n- Source: {doc.get('source', 'unknown')}")
                        formatted_parts.append(f"  Score: {doc.get('score', 0):.2f}")
                        formatted_parts.append(f"  Content: {doc.get('content', '')[:300]}...")

                elif tool_name == "summarize_content":
                    formatted_parts.append(result["result"].get("summary", ""))

                else:
                    # 通用格式
                    formatted_parts.append(json.dumps(result["result"], ensure_ascii=False, indent=2))
            else:
                # 失败的工具调用
                formatted_parts.append(f"[{tool_name}] Error: {result.get('error', 'Unknown error')}")

        return "\n".join(formatted_parts)

    def _extract_final_answer(self, response: str) -> str:
        """
        从LLM响应中提取最终答案（移除工具调用部分）

        Args:
            response: LLM的响应文本

        Returns:
            清理后的最终答案
        """
        # 移除工具调用标记
        clean_response = re.sub(
            r'<tool_call>.*?</tool_call>',
            '',
            response,
            flags=re.DOTALL
        )

        # 移除多余的空白
        clean_response = clean_response.strip()

        return clean_response if clean_response else response

    def reset_memory(self) -> None:
        """重置对话记忆"""
        self.memory.clear()
        print("[Agent] Memory cleared")

    def get_conversation_history(self) -> List[Dict]:
        """获取完整的对话历史"""
        return self.memory.get_messages()

    def get_memory_stats(self) -> Dict:
        """获取内存统计信息"""
        return self.memory.get_summary_stats()

    def save_conversation(self, filepath: str) -> None:
        """保存对话历史到文件"""
        self.memory.save_to_file(filepath)
        print(f"[Agent] Conversation saved to {filepath}")

    def load_conversation(self, filepath: str) -> None:
        """从文件加载对话历史"""
        self.memory.load_from_file(filepath)
        print(f"[Agent] Conversation loaded from {filepath}")
