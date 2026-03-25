#定义RAG类
from .data_loader import load_multi_format_data
from .chunker import split_pdf_to_chunks
from .embedder import Embedder
from .vector_store import VectorStore
from .retriever import BM25Retriever, SemanticRetriever, HybridRetriever
from .query_expander import LLMQueryExpander
from ..utils.config import load_config
from typing import List, Dict, Optional
from langchain_core.documents import Document
import os

class RAG:
    def __init__(self, config_path):
        """
        初始化 RAG 系统

        参数：config_path - 配置文件路径

        职责：
          1. 读取配置文件
          2. 加载和分块文档
          3. 初始化 Embedder
          4. 初始化 VectorStore
          5. 生成嵌入并存储
        """
        print("初始化 RAG 系统")

        # 步骤1：读取配置
        print("\n读取配置文件...")
        self.config = load_config(config_path)
        self.data_dir = self.config['data']['data_dir']
        self.cache_dir = self.config['cache']['cache_dir']
        self.chunk_size = int(self.config['chunk']['chunk_size'])
        self.chunk_overlap = int(self.config['chunk']['chunk_overlap'])
        print("配置读取完成")

        # 步骤2：加载文档
        print("\n加载文档")
        self.all_documents = load_multi_format_data(
            self.data_dir,
            self.cache_dir,
            use_cache=True
        )
        print(f"加载了 {len(self.all_documents)} 个文档")

        # 步骤3：分类和分块
        print("\n文档分类和分块")
        self.chunks = self._split_and_chunk_documents()
        print(f"分块完成：共 {len(self.chunks)} 个 chunks")

        # 步骤4：初始化 Embedder
        print("\n初始化嵌入模型")
        self.embedder = Embedder(model_name=self.config['embedder']['model_name'], dimensions=int(self.config['embedder']['model_dimensions']))
        print("嵌入模型初始化完成")

        # 步骤5：初始化 VectorStore
        print("\n初始化向量库")

        self.vector_store = VectorStore(
            embedder=self.embedder,
            persist_directory=self.config['vector_store']['persist_directory'],
            collection_name=self.config['vector_store']['collection_name'],
            distance_metric=self.config['vector_store']['distance_metric']
        )
        # 步骤6：检查向量库是否已存在
        if self._check_vector_store_exists():
            print("向量库已存在，使用现有的")
        else:
            print("创建新的向量库")

            # 生成嵌入
            print("生成嵌入向量并存储到向量库")
            enhanced_chunks = self.embedder.embed_chunks(self.chunks)

            # 存储到向量库
            self.vector_store.add_chunks(enhanced_chunks)
            print("向量库创建完成")

        # 步骤7：初始化检索器
        print("\n初始化检索器")
        self._initialize_retrievers()
        print("检索器初始化完成")

        # 步骤8：初始化查询改写器
        print("\n初始化查询改写器")
        self.query_expander = LLMQueryExpander()
        print("查询改写器初始化完成")

        print("\nRAG 系统初始化完成！\n")

    def _split_and_chunk_documents(self) -> List[Document]:
        """
        分类文档并进行分块

        职责：
          1. 按文件类型分类（仅处理PDF）
          2. 调用对应的分块器
          3. 返回分块结果

        返回：分块后的 Document 列表
        """
        # 分类文档（仅提取PDF）
        pdf_docs = self._classify_documents(self.all_documents)

        print(f"   分类结果：{len(pdf_docs)} 个 PDF 文件")

        # 分块
        pdf_chunks = split_pdf_to_chunks(
            pdf_docs,
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap
        ) if pdf_docs else []

        print(f"   分块结果：{len(pdf_chunks)} 个 PDF chunks")

        return pdf_chunks

    @staticmethod
    def _classify_documents(documents: List[Document]) -> List[Document]:
        """
        按文件类型分类文档

        参数：documents - 所有文档列表

        返回：PDF 文档列表
        """
        pdf_docs = []

        for doc in documents:
            source = doc.metadata.get("source", "")
            if source.endswith(".pdf"):
                pdf_docs.append(doc)

        return pdf_docs

    def _check_vector_store_exists(self) -> bool:
        """
        检查向量库是否已存在

        返回：True 如果向量库存在且非空，否则 False
        """
        persist_dir = self.config['vector_store']['persist_directory']

        if not os.path.exists(persist_dir):
            return False

        # 检查目录是否非空
        if len(os.listdir(persist_dir)) == 0:
            return False

        # 检查向量库中是否有数据
        try:
            stats = self.vector_store.get_stats()
            return stats['total_chunks'] > 0
        except:
            return False

    def _initialize_retrievers(self) -> None:
        """
        初始化所有检索器（BM25、语义、混合）

        职责：
          1. 创建BM25检索器
          2. 创建语义检索器
          3. 创建混合检索器
        """
        retriever_config = self.config.get('retriever', {})

        self.bm25_retriever = BM25Retriever(self.chunks)
        self.semantic_retriever = SemanticRetriever(self.vector_store, self.embedder)
        self.hybrid_retriever = HybridRetriever(self.bm25_retriever, self.semantic_retriever)

    def search(self, query: str, top_k: int = 5, strategy: str = None, use_expansion: bool = True) -> List[Dict]:
        """
        核心查询接口

        参数：
          query - 用户查询文本
          top_k - 返回结果数量(默认设置为5)
          strategy - 检索策略 ('bm25', 'semantic', 'hybrid')，默认使用config中的配置
          use_expansion - 是否使用查询改写，默认为True

        返回：
          相关 chunks 列表，每个结果包含：
            {
              "rank": 1,
              "content": "...",
              "source": "data/STL.pdf",
              "page": 12,
              "score": 0.85,
              "metadata": {...}
            }
        """
        print(f"\n查询: {query}")

        try:
            retriever_config = self.config.get('retriever', {})
            if strategy is None:
                strategy = retriever_config.get('strategy', 'hybrid')

            print(f"使用 {strategy} 检索策略")

            if use_expansion:
                expanded_queries = self.query_expander.expand_query(query)
            else:
                expanded_queries = [query]

            all_results = {}

            for expanded_query in expanded_queries:
                print(f"\n执行检索: {expanded_query}")

                if strategy == 'bm25':
                    results = self.bm25_retriever.search(expanded_query, top_k=top_k)
                elif strategy == 'semantic':
                    results = self.semantic_retriever.search(expanded_query, top_k=top_k)
                elif strategy == 'hybrid':
                    alpha = float(retriever_config.get('hybrid', {}).get('alpha', 0.3))
                    results = self.hybrid_retriever.search(expanded_query, top_k=top_k, alpha=alpha)
                else:
                    raise ValueError(f"不支持的检索策略: {strategy}")

                for result in results:
                    content_hash = hash(result['content']) % 10000000
                    if content_hash not in all_results:
                        all_results[content_hash] = {
                            'chunk_id': result['chunk_id'],
                            'content': result['content'],
                            'metadata': result['metadata'],
                            'score': float(result['score']),
                            'count': 1
                        }
                    else:
                        all_results[content_hash]['score'] += float(result['score'])
                        all_results[content_hash]['count'] += 1

            merged_results = list(all_results.values())

            for result in merged_results:
                base_score = result['score'] / result['count']
                frequency_boost = 1 + (result['count'] - 1) * 0.15
                result['score'] = base_score * frequency_boost

            merged_results = sorted(merged_results, key=lambda x: x['score'], reverse=True)[:top_k]

            formatted_results = []
            for rank, result in enumerate(merged_results, 1):
                formatted_results.append({
                    "rank": rank,
                    "chunk_id": result['chunk_id'],
                    "content": result['content'],
                    "source": result['metadata'].get('source', 'Unknown'),
                    "page": result['metadata'].get('page'),
                    "score": f"{result['score']:.4f}",
                    "metadata": result['metadata']
                })

            return formatted_results

        except Exception as e:
            print(f"查询失败: {e}")
            raise

    def display_search_results(self, results: List[Dict], show_full_content: bool = True) -> None:
        """
        打印搜索结果（显示完整内容）

        参数：
          results - search() 方法的返回结果
          show_full_content - 是否显示完整内容（默认为True）
        """
        print("\n" + "=" * 80)
        print(f"搜索结果（共 {len(results)} 个）")
        print("=" * 80)

        for result in results:
            print(f"\n【结果 {result['rank']}】")
            print(f"得分: {result['score']}")
            print(f"来源: {result['source']}")
            if result['page']:
                print(f"页码: {result['page']}")
            print(f"Chunk ID: {result['chunk_id']}")
            print("\n内容：")
            print("-" * 80)

            if show_full_content:
                print(result['content'])
            else:
                content_preview = result['content'][:500]
                if len(result['content']) > 500:
                    content_preview += "..."
                print(content_preview)

            print("-" * 80)

    def get_vector_store_stats(self) -> Dict:
        """获取向量库统计信息"""
        return self.vector_store.get_stats()

    def display_chunks(self, num_samples: int = 3) -> None:
        """
        显示 chunks 样本（用于调试）

        参数：num_samples - 显示的样本数量
        """
        print(f"\n=== 知识库统计 ===")
        print(f"总分块数: {len(self.chunks)}")
        print("-" * 50)

        for i, chunk in enumerate(self.chunks[:num_samples]):
            print(f"\n【Chunk {i+1}】")
            source = chunk.metadata.get('source', 'Unknown')

            print(f"源文件: {source}")
            print(f"内容摘要:\n{chunk.page_content[0:200]}...")
            print("-" * 50)

