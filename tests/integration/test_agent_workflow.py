"""集成测试：Agent + RAG 工作流测试"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.agent import (
    Agent,
    ToolRegistry,
    RetrievalTool,
    CodeAnalysisTool,
    SummarizationTool,
    QuestionDecompositionTool,
    OpenAIInterface,
    ConversationMemory
)
from src.rag.rag import RAG


class TestAgentWorkflow:
    """Agent工作流集成测试"""

    @classmethod
    def setup_class(cls):
        """测试类初始化"""
        print("\n" + "="*80)
        print("Setting up Agent Workflow Test")
        print("="*80)

        # 初始化RAG系统
        print("\n[Setup] Initializing RAG system...")
        try:
            config_path = project_root / "config" / "rag.yaml"
            cls.rag = RAG(str(config_path))
            print(f"✓ RAG system initialized")
        except Exception as e:
            print(f"✗ Failed to initialize RAG: {str(e)}")
            print(f"   (This is expected if knowledge base hasn't been built yet)")
            cls.rag = None

        # 初始化LLM接口
        print("\n[Setup] Initializing LLM interface...")
        try:
            cls.llm = OpenAIInterface()
            print(f"✓ LLM interface initialized (Model: {cls.llm.model})")
        except Exception as e:
            print(f"✗ Failed to initialize LLM: {str(e)}")
            raise

        # 初始化对话内存
        print("\n[Setup] Initializing memory...")
        cls.memory = ConversationMemory(max_history=20, max_tokens=4000)
        print(f"✓ Memory initialized")

        # 初始化工具注册表
        print("\n[Setup] Initializing tool registry...")
        cls.tool_registry = ToolRegistry()

        # 注册检索工具（如果RAG可用）
        if cls.rag:
            retrieval_tool = RetrievalTool(cls.rag.hybrid_retriever)
            cls.tool_registry.register(retrieval_tool)
            print(f"✓ Retrieval tool registered")

        # 注册代码分析工具
        code_tool = CodeAnalysisTool()
        cls.tool_registry.register(code_tool)
        print(f"✓ Code analysis tool registered")

        # 注册总结工具
        summary_tool = SummarizationTool(cls.llm)
        cls.tool_registry.register(summary_tool)
        print(f"✓ Summarization tool registered")

        # 注册问题分解工具
        decompose_tool = QuestionDecompositionTool(cls.llm)
        cls.tool_registry.register(decompose_tool)
        print(f"✓ Question decomposition tool registered")

        # 初始化Agent
        print("\n[Setup] Initializing Agent...")
        cls.agent = Agent(
            tool_registry=cls.tool_registry,
            llm_interface=cls.llm,
            memory=cls.memory,
            max_iterations=3
        )
        print(f"✓ Agent initialized with {len(cls.tool_registry.list_tools())} tools")

        print("\n" + "="*80)
        print("Setup Complete!")
        print("="*80)

    def test_cpp_bool_question(self):
        

        query = "Who is Xinyang Li?"

        print(f"\n[Test] User Query: {query}")
        print("-" * 80)

        try:
            # 运行Agent
            print("\n[Test] Running Agent...")
            response = self.agent.run(query, use_tools=True)

            print("\n" + "-" * 80)
            print("[Test] Agent Response:")
            print("-" * 80)
            print(response)
            print("-" * 80)

            # 验证响应
            print("\n[Test] Validation:")
            validation_results = self._validate_response(response, query)

            print(f"\nValidation Results:")
            for check, passed in validation_results.items():
                status = "✓ PASS" if passed else "✗ FAIL"
                print(f"  {status}: {check}")

            # 获取内存统计
            stats = self.agent.get_memory_stats()
            print(f"\nMemory Statistics:")
            print(f"  Total messages: {stats['total_messages']}")
            print(f"  User messages: {stats['user_messages']}")
            print(f"  Assistant messages: {stats['assistant_messages']}")
            print(f"  Total tokens: {stats['total_tokens']}")
            print(f"  Token usage: {stats['token_usage_percent']:.1f}%")

            # 获取对话历史
            history = self.agent.get_conversation_history()
            print(f"\nConversation History ({len(history)} messages):")
            for i, msg in enumerate(history, 1):
                role = msg['role'].upper()
                content_preview = msg['content'][:100] + "..." if len(msg['content']) > 100 else msg['content']
                print(f"  [{i}] {role}: {content_preview}")

            print("\n" + "="*80)
            print("Test Complete!")
            print("="*80)

            # 返回测试结果
            return all(validation_results.values()), response

        except Exception as e:
            print(f"\n✗ Test Failed with Exception:")
            print(f"  {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            return False, str(e)

    def _validate_response(self, response: str, query: str) -> dict:
        """
        验证Agent响应的质量

        Args:
            response: Agent的响应
            query: 原始查询

        Returns:
            验证结果字典
        """
        validation = {}

        # 检查1：响应是否为空
        validation["Response is not empty"] = len(response.strip()) > 0

        # 检查2：响应长度合理
        validation["Response length is reasonable"] = 50 < len(response) < 2000

        # 检查3：响应包含关键词（true/false 或 bool）
        response_lower = response.lower()
        validation["Response mentions bool/true/false"] = (
            "bool" in response_lower or
            "true" in response_lower or
            "false" in response_lower or
            "true 和 false" in response_lower
        )

        # 检查4：响应不包含明显的错误信息
        validation["No error messages in response"] = not any(
            error_keyword in response_lower
            for error_keyword in ["error", "failed", "exception", "not found"]
            if "error" in response_lower or "failed" in response_lower
        )

        # 检查5：响应包含两个值的提及
        has_two_values = (
            (response.count("true") + response.count("false")) >= 2 or
            "two" in response_lower or
            "both" in response_lower or
            "①" in response or
            "②" in response or
            "1." in response and "2." in response
        )
        validation["Response mentions two values"] = has_two_values

        return validation


def run_tests():
    """运行测试"""
    print("\n\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*20 + "AGENT WORKFLOW INTEGRATION TEST" + " "*28 + "║")
    print("╚" + "="*78 + "╝")

    # 类级别的设置
    test_instance = TestAgentWorkflow()
    TestAgentWorkflow.setup_class()

    # 运行测试
    success, response = test_instance.test_cpp_bool_question()


    # 保存对话历史
    try:
        log_file = project_root / "tests" / "integration" / "test_agent_conversation.json"
        test_instance.agent.save_conversation(str(log_file))
        print(f"\n✓ Conversation saved to: {log_file}")
    except Exception as e:
        print(f"\n✗ Failed to save conversation: {str(e)}")

    return 0 if success else 1


if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code)
