"""Agent核心模块单元测试"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.agent import (
    Agent,
    ToolRegistry,
    RetrievalTool,
    CodeAnalysisTool,
    ConversationMemory,
    OpenAIInterface
)


class TestAgentMemory:
    """测试Agent内存管理"""

    def test_conversation_memory_add_message(self):
        """测试添加消息"""
        memory = ConversationMemory()
        memory.add_message("user", "Hello")
        memory.add_message("assistant", "Hi there!")

        assert len(memory.messages) == 2
        assert memory.messages[0].role == "user"
        assert memory.messages[0].content == "Hello"
        print("✓ test_conversation_memory_add_message passed")

    def test_conversation_memory_get_messages(self):
        """测试获取消息"""
        memory = ConversationMemory()
        memory.add_message("user", "What is Python?")
        memory.add_message("assistant", "Python is a programming language")

        messages = memory.get_messages()
        assert len(messages) == 2
        assert messages[0]["role"] == "user"
        assert isinstance(messages, list)
        print("✓ test_conversation_memory_get_messages passed")

    def test_conversation_memory_token_limit(self):
        """测试Token限制"""
        memory = ConversationMemory(max_history=5, max_tokens=100)

        # 添加多条消息
        for i in range(10):
            memory.add_message("user", f"This is a long message number {i} with some extra content to increase token count")

        # 应该被限制在5条消息以内
        assert len(memory.messages) <= 5
        print("✓ test_conversation_memory_token_limit passed")

    def test_memory_clear(self):
        """测试清空内存"""
        memory = ConversationMemory()
        memory.add_message("user", "Hello")
        memory.clear()

        assert len(memory.messages) == 0
        assert memory.current_tokens == 0
        print("✓ test_memory_clear passed")


class TestToolRegistry:
    """测试工具注册表"""

    def test_tool_registry_register(self):
        """测试注册工具"""
        registry = ToolRegistry()
        tool = CodeAnalysisTool()
        registry.register(tool)

        assert len(registry.list_tools()) == 1
        assert registry.get_tool("analyze_code") is not None
        print("✓ test_tool_registry_register passed")

    def test_tool_registry_execute(self):
        """测试执行工具"""
        registry = ToolRegistry()
        tool = CodeAnalysisTool()
        registry.register(tool)

        result = registry.execute_tool("analyze_code", code="print('hello')", language="python")

        assert result["success"] is True
        assert "analysis" in result["result"]
        print("✓ test_tool_registry_execute passed")

    def test_tool_registry_nonexistent_tool(self):
        """测试执行不存在的工具"""
        registry = ToolRegistry()
        result = registry.execute_tool("nonexistent_tool")

        assert result["success"] is False
        assert "不存在" in result["error"] or "not exist" in result["error"]
        print("✓ test_tool_registry_nonexistent_tool passed")


class TestAgent:
    """测试Agent核心功能"""

    def setup_method(self):
        """测试方法前的设置"""
        self.memory = ConversationMemory()
        self.tool_registry = ToolRegistry()
        self.tool_registry.register(CodeAnalysisTool())

        try:
            self.llm = OpenAIInterface()
        except ValueError as e:
            print(f"Warning: LLM not available - {str(e)}")
            self.llm = None

    def test_agent_initialization(self):
        """测试Agent初始化"""
        if self.llm is None:
            print("⊘ test_agent_initialization skipped (no LLM)")
            return

        agent = Agent(
            tool_registry=self.tool_registry,
            llm_interface=self.llm,
            memory=self.memory
        )

        assert agent.tool_registry is not None
        assert agent.llm is not None
        assert agent.memory is not None
        print("✓ test_agent_initialization passed")

    def test_agent_parse_tool_calls(self):
        """测试解析工具调用"""
        if self.llm is None:
            print("⊘ test_agent_parse_tool_calls skipped (no LLM)")
            return

        agent = Agent(
            tool_registry=self.tool_registry,
            llm_interface=self.llm,
            memory=self.memory
        )

        # 模拟LLM响应
        response = """Here is my analysis:
<tool_call>
<name>analyze_code</name>
<input>{"code": "print('hello')", "language": "python"}</input>
</tool_call>

And here is my conclusion."""

        tool_calls = agent._parse_tool_calls(response)

        assert len(tool_calls) == 1
        assert tool_calls[0]["name"] == "analyze_code"
        assert tool_calls[0]["params"]["code"] == "print('hello')"
        print("✓ test_agent_parse_tool_calls passed")

    def test_agent_extract_final_answer(self):
        """测试提取最终答案"""
        if self.llm is None:
            print("⊘ test_agent_extract_final_answer skipped (no LLM)")
            return

        agent = Agent(
            tool_registry=self.tool_registry,
            llm_interface=self.llm,
            memory=self.memory
        )

        response = """<tool_call>
<name>analyze_code</name>
<input>{"code": "test"}</input>
</tool_call>

This is the final answer without tool calls."""

        clean_answer = agent._extract_final_answer(response)

        assert "<tool_call>" not in clean_answer
        assert "This is the final answer" in clean_answer
        print("✓ test_agent_extract_final_answer passed")

    def test_memory_reset(self):
        """测试重置内存"""
        if self.llm is None:
            print("⊘ test_memory_reset skipped (no LLM)")
            return

        agent = Agent(
            tool_registry=self.tool_registry,
            llm_interface=self.llm,
            memory=self.memory
        )

        agent.memory.add_message("user", "Hello")
        assert len(agent.memory.messages) == 1

        agent.reset_memory()
        assert len(agent.memory.messages) == 0
        print("✓ test_memory_reset passed")


def run_unit_tests():
    """运行所有单元测试"""
    print("\n" + "="*80)
    print("Running Unit Tests")
    print("="*80 + "\n")

    test_classes = [
        TestAgentMemory,
        TestToolRegistry,
        TestAgent
    ]

    total_tests = 0
    passed_tests = 0
    failed_tests = 0

    for test_class in test_classes:
        print(f"\n{test_class.__name__}:")
        print("-" * 40)

        instance = test_class()
        test_methods = [
            method for method in dir(instance)
            if method.startswith("test_")
        ]

        for method_name in test_methods:
            total_tests += 1
            try:
                # 如果有setup_method，先执行
                if hasattr(instance, "setup_method"):
                    instance.setup_method()

                # 执行测试
                method = getattr(instance, method_name)
                method()
                passed_tests += 1

            except AssertionError as e:
                print(f"✗ {method_name} failed: {str(e)}")
                failed_tests += 1
            except Exception as e:
                print(f"✗ {method_name} error: {str(e)}")
                failed_tests += 1

    # 输出总结
    print("\n" + "="*80)
    print(f"Test Summary: {passed_tests}/{total_tests} passed")
    if failed_tests > 0:
        print(f"⚠ {failed_tests} test(s) failed")
    print("="*80)

    return 0 if failed_tests == 0 else 1


if __name__ == "__main__":
    exit_code = run_unit_tests()
    sys.exit(exit_code)
