# LXY Code CLI - 快速开始

## 🚀 一句话启动

```bash
cd /Users/lixinyang/Desktop/Learning\ AssistantAgent/cli && npm start
```

---

## ⚙️ 安装依赖（仅第一次）

### Python 依赖

```bash
cd /Users/lixinyang/Desktop/Learning\ AssistantAgent
pip install fastapi uvicorn
```

### Node 依赖

```bash
cd /Users/lixinyang/Desktop/Learning\ AssistantAgent/cli
npm install
```

---

## 📺 界面预览

启动后你会看到：

```
  ██╗      ██╗ ██╗   ██╗     ██████╗  ██████╗  ██████╗  ███████╗
  ██║      ╚██╗██╔╝  ╚██╗██╔╝    ██╔════╝ ██╔═══██╗ ██╔══██╗ ██╔════╝
  ██║       ╚███╔╝    ╚███╔╝     ██║      ██║   ██║ ██║  ██║ █████╗
  ██║       ██╔██╗     ╚██╔╝     ██║      ██║   ██║ ██║  ██║ ██╔══╝
  ███████╗ ██╔╝ ██╗     ██║      ╚██████╗ ╚██████╔╝ ██████╔╝ ███████╗
  ╚══════╝╚═╝   ╚═╝     ╚═╝       ╚═════╝  ╚═════╝  ╚═════╝  ╚══════╝

  Learning Assistant Agent  |  v1.0.0  |  Powered by RAG + GPT-4
  ─────────────────────────────────────────────────────────────────

  [1/2] Starting Python backend...
  [2/2] Loading RAG knowledge base (this may take ~2 minutes)...
  Ready. (initialized in 12.0s)

  ┌──────────────────────────────────────────────┐
  │  LXY Code  |  Type /help for commands        │
  └──────────────────────────────────────────────┘

  Commands:
  ─────────
    /reset      Reset conversation memory
    /history    Show conversation history
    /help       Show this help message
    /exit       Exit the program
```

---

## 💬 交互示例

```
You: Who developed this system?
Thinking...

Agent: The system was developed by Xinyang Li (李欣洋), a student at
       Tongji University majoring in Information Security. He created
       this Learning Assistant Agent system.

You: What are his hobbies?
Thinking...

Agent: According to the system information, his hobbies include playing
       League of Legends, a popular multiplayer online battle arena game.

You: /history
Conversation History:
─────────────────────
You: Who developed this system?
Agent: The system was developed by Xinyang Li...
You: What are his hobbies?
Agent: According to the system information, his hobbies...

You: /reset
Conversation cleared.

You: /exit
Goodbye.
```

---

## 🎮 命令列表

| 命令 | 说明 | 示例 |
|------|------|------|
| （任意文本） | 发送问题 | `What is RAG?` |
| `/help` | 显示帮助 | `/help` |
| `/history` | 查看对话历史 | `/history` |
| `/reset` | 重置对话 | `/reset` |
| `/exit` | 退出程序 | `/exit` |
| `Ctrl+C` | 强制退出 | 按 Ctrl+C |

---

## ❓ 常见问题

### Q: "Error: Python process exited with code 2"

**A:** Python 服务器启动失败。检查：
- 是否安装了依赖：`pip install fastapi uvicorn`
- Python 版本是否 ≥ 3.8：`python3 --version`
- 端口 8765 是否被占用：`lsof -i :8765`

### Q: "Could not connect to Agent API"

**A:** Python 后端没有启动或未就绪。等待 2-3 分钟，RAG 初始化很耗时。

### Q: "System is still initializing"

**A:** RAG 系统在加载知识库。第一次启动需要 ~2 分钟。

### Q: 如何修改模型或 API Key？

**A:** 编辑项目根目录的 `.env` 文件：
```env
OPENAI_API_KEY=sk-your-key
OPENAI_API_BASE=https://api.openai.com/v1
```

### Q: 支持其他 LLM 吗？

**A:** 目前只支持 OpenAI 兼容的 API。可修改 `src/agent/llm_interface.py` 添加其他 LLM。

---

## 🏗️ 架构一览

```
TypeScript CLI
    ↓ (child_process)
Python FastAPI Server (:8765)
    ↓ (HTTP)
Agent
    ↓
RAG + LLM
    ↓
Knowledge Base (394 docs, 5518 chunks)
```

---

## 📝 后端日志位置

如果 CLI 启动失败，查看 Python 日志：

```bash
# 查看最后一次启动日志
tail -f /tmp/server.log

# 或直接运行 Python 服务器查看实时日志
cd /Users/lixinyang/Desktop/Learning\ AssistantAgent
python3 src/api/server.py
```

---

## ✨ 特色

- 🎨 **美观界面**：ASCII art 启动横幅
- ⚡ **快速启动**：一个命令即可启动
- 🔄 **自动进程管理**：自动启动/停止 Python 后端
- 💾 **对话历史**：支持查看和重置对话
- 🛡️ **优雅退出**：Ctrl+C 正确清理资源
- 🎯 **知识库集成**：完整的 RAG + LLM 系统

---

## 🚨 故障排除

### Python 依赖问题

```bash
# 重装所有依赖
pip install --upgrade -r requirements.txt
pip install fastapi uvicorn
```

### Node 依赖问题

```bash
cd cli
rm -rf node_modules package-lock.json
npm install
```

### 端口被占用

```bash
# 查看占用 8765 的进程
lsof -i :8765

# 杀掉该进程
kill -9 <PID>
```

---

**现在就开始使用吧！** 🚀

```bash
cd /Users/lixinyang/Desktop/Learning\ AssistantAgent/cli && npm start
```
