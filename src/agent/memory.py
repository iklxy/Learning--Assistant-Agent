"""对话历史与记忆管理"""

from typing import List, Dict, Optional, Any
from datetime import datetime
import json


class Message:
    """消息类"""

    def __init__(self, role: str, content: str, timestamp: Optional[str] = None):
        """
        初始化消息

        Args:
            role: 消息角色 ("user", "assistant", "system")
            content: 消息内容
            timestamp: 时间戳（默认当前时间）
        """
        self.role = role
        self.content = content
        self.timestamp = timestamp or datetime.now().isoformat()

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp
        }

    def __len__(self) -> int:
        """估算token数（粗略计算：1个字约0.3个token）"""
        return max(1, len(self.content) // 3)


class ConversationMemory:
    """对话历史管理器"""

    def __init__(self, max_history: int = 20, max_tokens: int = 4000):
        """
        初始化对话记忆

        Args:
            max_history: 保留的最大消息数量
            max_tokens: 上下文窗口的最大token数（保守估计）
        """
        self.messages: List[Message] = []
        self.max_history = max_history
        self.max_tokens = max_tokens
        self.current_tokens = 0

    def add_message(self, role: str, content: str) -> None:
        """
        添加消息

        Args:
            role: 角色 ("user", "assistant")
            content: 内容
        """
        message = Message(role, content)
        self.messages.append(message)
        self.current_tokens += len(message)

        # 检查是否超过限制
        self._enforce_limits()

    def _enforce_limits(self) -> None:
        """强制执行大小限制"""
        # 1. 检查消息数量限制
        if len(self.messages) > self.max_history:
            # 保留最后的消息，删除最早的
            removed = self.messages.pop(0)
            self.current_tokens -= len(removed)

        # 2. 检查token限制
        while self.current_tokens > self.max_tokens and len(self.messages) > 1:
            # 删除最早的消息，但保留至少1条
            removed = self.messages.pop(0)
            self.current_tokens -= len(removed)

    def get_messages(self) -> List[Dict]:
        """
        获取消息历史（用于LLM调用）

        Returns:
            消息列表格式
        """
        return [msg.to_dict() for msg in self.messages]

    def get_recent_messages(self, num: int = 5) -> List[Dict]:
        """
        获取最近的N条消息

        Args:
            num: 消息数量

        Returns:
            最近的消息列表
        """
        return [msg.to_dict() for msg in self.messages[-num:]]

    def get_context_window(self) -> str:
        """
        获取完整的上下文窗口（用于LLM prompt）

        Returns:
            格式化的对话历史
        """
        context_lines = []
        for msg in self.messages:
            # 更新为英文前缀，规范化 LLM 的阅读语境
            role_display = "User" if msg.role == "user" else "Assistant"
            context_lines.append(f"{role_display}: {msg.content}")

        return "\n".join(context_lines)

    def get_last_user_query(self) -> Optional[str]:
        """获取最后一条用户消息"""
        for msg in reversed(self.messages):
            if msg.role == "user":
                return msg.content
        return None

    def get_last_assistant_response(self) -> Optional[str]:
        """获取最后一条助手消息"""
        for msg in reversed(self.messages):
            if msg.role == "assistant":
                return msg.content
        return None

    def clear(self) -> None:
        """清空所有消息"""
        self.messages.clear()
        self.current_tokens = 0

    def save_to_file(self, filepath: str) -> None:
        """
        保存对话历史到文件

        Args:
            filepath: 文件路径
        """
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                data = {
                    "messages": self.get_messages(),
                    "timestamp": datetime.now().isoformat()
                }
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存对话历史失败: {str(e)}")

    def load_from_file(self, filepath: str) -> None:
        """
        从文件加载对话历史

        Args:
            filepath: 文件路径
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.clear()
                for msg_dict in data.get("messages", []):
                    msg = Message(
                        role=msg_dict["role"],
                        content=msg_dict["content"],
                        timestamp=msg_dict.get("timestamp")
                    )
                    self.messages.append(msg)
                    self.current_tokens += len(msg)
        except Exception as e:
            print(f"加载对话历史失败: {str(e)}")

    def get_summary_stats(self) -> Dict:
        """获取对话统计信息"""
        user_messages = [m for m in self.messages if m.role == "user"]
        assistant_messages = [m for m in self.messages if m.role == "assistant"]

        return {
            "total_messages": len(self.messages),
            "user_messages": len(user_messages),
            "assistant_messages": len(assistant_messages),
            "total_tokens": self.current_tokens,
            "token_usage_percent": (self.current_tokens / self.max_tokens) * 100 if self.max_tokens > 0 else 0
        }


class SessionMemory:
    """会话级别的记忆管理（可选）"""

    def __init__(self, session_id: str):
        """
        初始化会话记忆

        Args:
            session_id: 会话ID
        """
        self.session_id = session_id
        self.conversation = ConversationMemory()
        self.user_profile: Dict[str, Any] = {}  # 用户偏好、学习风格等
        self.retrieved_docs: Dict[str, Dict] = {}  # 检索过的文档缓存
        self.created_at = datetime.now().isoformat()

    def add_retrieved_doc(self, doc_id: str, doc_content: Dict) -> None:
        """缓存检索过的文档，避免重复检索"""
        self.retrieved_docs[doc_id] = doc_content

    def get_retrieved_doc(self, doc_id: str) -> Optional[Dict]:
        """获取已缓存的文档"""
        return self.retrieved_docs.get(doc_id)

    def clear_doc_cache(self) -> None:
        """清空文档缓存"""
        self.retrieved_docs.clear()

    def update_user_profile(self, key: str, value: Any) -> None:
        """更新用户配置"""
        self.user_profile[key] = value

    def get_user_profile(self) -> Dict[str, Any]:
        """获取用户配置"""
        return self.user_profile

    def to_dict(self) -> Dict:
        """转换为字典（用于序列化）"""
        return {
            "session_id": self.session_id,
            "created_at": self.created_at,
            "messages": self.conversation.get_messages(),
            "user_profile": self.user_profile,
            "stats": self.conversation.get_summary_stats()
        }


class MemoryManager:
    """多会话记忆管理器"""

    def __init__(self):
        """初始化记忆管理器"""
        self.sessions: Dict[str, SessionMemory] = {}
        self.current_session_id: Optional[str] = None

    def create_session(self, session_id: str) -> SessionMemory:
        """创建新会话"""
        if session_id in self.sessions:
            return self.sessions[session_id]

        session = SessionMemory(session_id)
        self.sessions[session_id] = session
        self.current_session_id = session_id
        return session

    def get_session(self, session_id: str) -> Optional[SessionMemory]:
        """获取会话"""
        return self.sessions.get(session_id)

    def get_current_session(self) -> Optional[SessionMemory]:
        """获取当前会话"""
        if self.current_session_id:
            return self.sessions.get(self.current_session_id)
        return None

    def switch_session(self, session_id: str) -> Optional[SessionMemory]:
        """切换会话"""
        if session_id in self.sessions:
            self.current_session_id = session_id
            return self.sessions[session_id]
        return None

    def delete_session(self, session_id: str) -> None:
        """删除会话"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            if self.current_session_id == session_id:
                self.current_session_id = None

    def list_sessions(self) -> List[str]:
        """列出所有会话ID"""
        return list(self.sessions.keys())