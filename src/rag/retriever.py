from typing import List, Dict, Optional, Callable
from langchain_core.documents import Document
from rank_bm25 import BM25Okapi
import jieba
from .vector_store import VectorStore
from .embedder import Embedder


class BM25Retriever:
    """BM25关键词检索器"""

    def __init__(self, chunks: List[Document], tokenizer: Optional[Callable] = None):
        """
        初始化BM25检索器

        参数：
          chunks - 文档chunks列表
          tokenizer - 分词函数，默认使用jieba
        """
        self.chunks = chunks
        self.tokenizer = tokenizer or (lambda x: list(jieba.cut(x)))

        print("正在构建BM25索引...")
        tokenized_chunks = [self.tokenizer(chunk.page_content) for chunk in chunks]
        self.bm25_model = BM25Okapi(tokenized_chunks)
        print(f"BM25索引构建完成，共索引 {len(chunks)} 个chunks")

    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        BM25关键词搜索

        参数：
          query - 查询文本
          top_k - 返回结果数量

        返回：
          [{
            "chunk_id": str,
            "content": str,
            "metadata": dict,
            "score": float,
          }, ...]
        """
        tokenized_query = self.tokenizer(query)
        scores = self.bm25_model.get_scores(tokenized_query)

        top_indices = sorted(
            range(len(scores)),
            key=lambda i: scores[i],
            reverse=True
        )[:top_k]

        results = []
        for idx in top_indices:
            chunk = self.chunks[idx]
            source = chunk.metadata.get('source', 'unknown')

            chunk_id = f"chunk_{hash(source + str(idx)) % 10000:04d}_bm25"

            results.append({
                "chunk_id": chunk_id,
                "content": chunk.page_content,
                "metadata": chunk.metadata,
                "score": float(scores[idx]),
                "retriever_type": "bm25"
            })

        return results


class SemanticRetriever:
    """语义向量检索器"""

    def __init__(self, vector_store: VectorStore, embedder: Embedder):
        """
        初始化语义检索器

        参数：
          vector_store - VectorStore实例
          embedder - Embedder实例
        """
        self.vector_store = vector_store
        self.embedder = embedder

    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        语义相似度搜索

        参数：
          query - 查询文本
          top_k - 返回结果数量

        返回：
          [{
            "chunk_id": str,
            "content": str,
            "metadata": dict,
            "score": float,
          }, ...]
        """
        query_vector = self.embedder.embed_text(query)
        results = self.vector_store.search(query_vector, top_k=top_k)

        formatted_results = []
        for result in results:
            formatted_results.append({
                "chunk_id": result['chunk_id'],
                "content": result['content'],
                "metadata": result['metadata'],
                "score": float(result['similarity']),
                "retriever_type": "semantic"
            })

        return formatted_results


class HybridRetriever:
    """混合检索器（BM25 + 语义搜索）"""

    def __init__(self, bm25_retriever: BM25Retriever, semantic_retriever: SemanticRetriever):
        """
        初始化混合检索器

        参数：
          bm25_retriever - BM25检索器实例
          semantic_retriever - 语义检索器实例
        """
        self.bm25_retriever = bm25_retriever
        self.semantic_retriever = semantic_retriever

    def search(self, query: str, top_k: int = 5, alpha: float = 0.3) -> List[Dict]:
        """
        混合搜索（融合BM25和语义搜索）

        参数：
          query - 查询文本
          top_k - 返回最终结果数量
          alpha - BM25权重（0-1），语义权重为(1-alpha)

        返回：
          [{
            "chunk_id": str,
            "content": str,
            "metadata": dict,
            "score": float,
            "bm25_score": float,
            "semantic_score": float,
          }, ...]
        """
        bm25_results = self.bm25_retriever.search(query, top_k=top_k)
        semantic_results = self.semantic_retriever.search(query, top_k=top_k)

        fused_results = self._fuse_results(bm25_results, semantic_results, alpha)
        fused_results = sorted(fused_results, key=lambda x: x['score'], reverse=True)[:top_k]

        return fused_results

    def _fuse_results(self, bm25_results: List[Dict],
                      semantic_results: List[Dict],
                      alpha: float) -> List[Dict]:
        """
        融合两种检索结果

        参数：
          bm25_results - BM25检索结果
          semantic_results - 语义检索结果
          alpha - BM25权重

        返回：
          融合后的结果列表
        """
        fused_map = {}

        bm25_scores = [r['score'] for r in bm25_results]
        bm25_max = max(bm25_scores) if bm25_scores else 1.0
        bm25_min = min(bm25_scores) if bm25_scores else 0.0
        bm25_range = bm25_max - bm25_min if bm25_max > bm25_min else 1.0

        for result in bm25_results:
            normalized_bm25 = (result['score'] - bm25_min) / bm25_range
            content_hash = hash(result['content']) % 1000000

            fused_map[content_hash] = {
                "chunk_id": result['chunk_id'],
                "content": result['content'],
                "metadata": result['metadata'],
                "bm25_score": normalized_bm25,
                "semantic_score": 0.0,
            }

        for result in semantic_results:
            content_hash = hash(result['content']) % 1000000
            semantic_score = result['score']

            if content_hash in fused_map:
                fused_map[content_hash]['semantic_score'] = semantic_score
            else:
                fused_map[content_hash] = {
                    "chunk_id": result['chunk_id'],
                    "content": result['content'],
                    "metadata": result['metadata'],
                    "bm25_score": 0.0,
                    "semantic_score": semantic_score,
                }

        for item in fused_map.values():
            item['score'] = (alpha * item['bm25_score'] +
                           (1 - alpha) * item['semantic_score'])

        return list(fused_map.values())
