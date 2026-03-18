# 项目目录结构

```
learning-assistant-agent/
│
├── README.md                           # 项目说明和快速开始
├── DEVELOPMENT.md                      # 开发文档（详见另一文件）
├── requirements.txt                    # Python依赖
├── .env.example                        # 环境变量模板
├── .gitignore                          # Git忽略文件
│
├── src/                                # 核心源代码
│   ├── __init__.py
│   │
│   ├── rag/                            # 第一阶段：RAG检索层
│   │   ├── __init__.py
│   │   ├── data_loader.py              # 文件加载器（PDF, Markdown, TXT, CPP/Go）
│   │   ├── chunker.py                  # 文本分块逻辑
│   │   ├── embedder.py                 # 向量化模块
│   │   ├── vector_store.py             # 向量数据库接口
│   │   ├── retriever.py                # 检索引擎（混合检索）
│   │   └── preprocessor.py             # 数据预处理工具
│   │
│   ├── agent/                          # 第二阶段：Agent推理层
│   │   ├── __init__.py
│   │   ├── agent.py                    # Agent核心逻辑
│   │   ├── tools.py                    # Agent工具集定义
│   │   ├── memory.py                   # 对话历史与记忆管理
│   │   ├── llm_interface.py            # LLM调用接口
│   │   └── prompts.py                  # 系统提示词集合
│   │
│   ├── interaction/                    # 第三阶段：个性化交互层
│   │   ├── __init__.py
│   │   ├── chat_interface.py           # 对话界面
│   │   ├── personalization.py          # 用户个性化引擎
│   │   ├── feedback_handler.py         # 反馈处理
│   │   └── session_manager.py          # 会话管理
│   │
│   └── utils/                          # 工具函数
│       ├── __init__.py
│       ├── config.py                   # 配置管理
│       ├── logging.py                  # 日志工具
│       ├── metrics.py                  # 性能评估工具
│       └── helpers.py                  # 通用辅助函数
│
├── config/                             # 配置文件目录
│   ├── config.yaml                     # 主配置文件
│   ├── rag_config.yaml                 # RAG系统配置
│   ├── agent_config.yaml               # Agent配置
│   ├── model_config.yaml               # LLM模型配置
│   └── vector_db_config.yaml           # 向量库配置
│
├── data/                               # 数据目录
│   ├── raw/                            # 原始学习资料
│   │   ├── pdfs/                       # PDF文件
│   │   ├── markdowns/                  # Markdown文件
│   │   └── texts/                      # 文本文件
│   │
│   ├── processed/                      # 处理后的数据
│   │   ├── chunks/                     # 分块后的文本
│   │   └── embeddings/                 # 向量化结果（可选）
│   │
│   ├── samples/                        # 测试样本
│   │   ├── sample1.pdf
│   │   └── sample2.md
│   │
│   ├── vector_db/                      # 向量数据库存储
│   │   └── chroma_db/                  # Chroma本地存储（如果使用）
│   │
│   └── test_queries.json               # 测试查询集合
│
├── tests/                              # 测试目录
│   ├── __init__.py
│   │
│   ├── unit/                           # 单元测试
│   │   ├── test_data_loader.py
│   │   ├── test_chunker.py
│   │   ├── test_embedder.py
│   │   ├── test_retriever.py
│   │   ├── test_agent.py
│   │   └── test_personalization.py
│   │
│   ├── integration/                    # 集成测试
│   │   ├── test_rag_pipeline.py
│   │   ├── test_agent_workflow.py
│   │   └── test_full_system.py
│   │
│   ├── performance/                    # 性能测试
│   │   ├── test_retrieval_speed.py
│   │   ├── test_indexing_speed.py
│   │   └── benchmark_results.json
│   │
│   └── fixtures/                       # 测试数据和工具
│       ├── sample_data.py
│       └── mock_llm.py
│
├── docs/                               # 文档
│   ├── ARCHITECTURE.md                 # 系统架构文档
│   ├── API.md                          # API文档
│   ├── USER_GUIDE.md                   # 用户使用指南
│   ├── DEPLOYMENT.md                   # 部署指南
│   ├── TROUBLESHOOTING.md              # 故障排查
│   └── diagrams/                       # 架构图
│       ├── system_architecture.png
│       ├── rag_pipeline.png
│       └── agent_workflow.png
│
├── scripts/                            # 脚本工具
│   ├── setup.sh                        # 初始化脚本
│   ├── build_index.py                  # 构建索引脚本
│   ├── evaluate.py                     # 评估脚本
│   ├── run_tests.sh                    # 运行测试脚本
│   └── format_code.sh                  # 代码格式化脚本
│
├── logs/                               # 日志目录（运行时生成）
│   ├── rag.log
│   ├── agent.log
│   └── system.log
│
├── notebooks/                          # Jupyter notebooks（可选）
│   ├── rag_exploration.ipynb
│   ├── agent_testing.ipynb
│   └── data_analysis.ipynb
│
└── docker/                             # Docker相关（可选）
    ├── Dockerfile
    └── docker-compose.yml

```

## 核心目录说明

### src/ 结构详解

```
src/
├── rag/                   # 第一阶段核心
│   ├── 职责：文档加载→分块→向量化→存储→检索
│   └── 关键文件：retriever.py（检索引擎核心）
│
├── agent/                 # 第二阶段核心
│   ├── 职责：推理决策→工具调用→结果整合
│   └── 关键文件：agent.py, tools.py
│
├── interaction/           # 第三阶段核心
│   ├── 职责：用户交互→个性化→反馈收集
│   └── 关键文件：chat_interface.py
│
└── utils/                 # 共享工具
    └── 职责：配置、日志、指标计算
```

### data/ 目录说明

```
data/
├── raw/                   # 存放用户的原始学习资料（手动维护）
├── processed/             # 分块和处理后的数据（自动生成）
├── vector_db/             # 向量库存储（自动生成）
├── samples/               # 用于测试的样本资料
└── test_queries.json      # 评估用的测试问题集
```

### tests/ 配置

```
tests/
├── unit/                  # 各模块单独测试
├── integration/           # 端到端流程测试
├── performance/           # 性能基准测试
└── fixtures/              # 共享的测试数据
```

## 文件命名约定

- **Python模块**：`snake_case.py`
- **配置文件**：`service_config.yaml`
- **测试文件**：`test_*.py`
- **文档文件**：`UPPERCASE.md`
- **数据文件**：按来源和类型分类

## 关键接口点

```
┌─────────────────────────────────────────────┐
│           Interaction Layer                 │
│  (chat_interface.py, personalization.py)    │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│            Agent Layer                      │
│  (agent.py → tools.py)                      │
└──────┬───────────────────────────────────┬──┘
       │                                   │
       └──────────────┬────────────────────┘
                      │
┌─────────────────────▼──────────────────────┐
│             RAG Layer                      │
│  (retriever.py ← vector_store.py)          │
└──────────────────────────────────────────┘
```

## 第一次运行流程

1. `scripts/setup.sh` - 环境初始化
2. 准备数据 - 将学习资料放入 `data/raw/`
3. `scripts/build_index.py` - 构建向量索引
4. `scripts/run_tests.sh` - 运行测试验证
5. 启动交互界面

## 扩展预留

- `notebooks/` - 数据探索和实验
- `docker/` - 容器化部署
- `logs/` - 系统运行日志
- `config/` - 支持多环境配置

