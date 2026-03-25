from typing import List, Dict, Optional
from sentence_transformers import CrossEncoder


class CrossEncoderReranker:
    """交叉编码器重排序器 - 用于重新评估和重排检索结果"""

    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-12-v2"):
        """
        Initialize Cross-Encoder Reranker

        Parameters:
          model_name - Name of the cross-encoder model. Default uses cross-encoder/ms-marco-MiniLM-L-12-v2
                     Other recommended models:
                     - "BAAI/bge-reranker-base" (multilingual, good performance)
                     - "BAAI/bge-reranker-large" (better performance, slower)
                     - "cross-encoder/qnli-distilroberta-base" (optimized for QA)
        """
        print(f"Loading cross-encoder reranking model: {model_name}")
        self.model = CrossEncoder(model_name)
        print(f"Cross-encoder model loaded successfully")

    def rerank(self, query: str, results: List[Dict], top_k: Optional[int] = None) -> List[Dict]:
        """
        Rerank retrieval results using cross-encoder model.

        Parameters:
          query - Query text
          results - List of results from retriever, each containing 'content' and other fields
          top_k - Number of final results to return. If None, return all reranked results

        Returns:
          List of reranked results with 'reranker_score' field added
        """
        if not results:
            return results

        # Prepare input data: (query, content) pairs
        query_content_pairs = [
            [query, result['content']]
            for result in results
        ]

        # Calculate relevance scores using cross-encoder
        print(f"Reranking {len(results)} results using cross-encoder...")
        reranker_scores = self.model.predict(query_content_pairs)

        # Add reranker score to each result
        for i, result in enumerate(results):
            result['reranker_score'] = float(reranker_scores[i])

        # Sort by reranker score
        reranked_results = sorted(
            results,
            key=lambda x: x['reranker_score'],
            reverse=True
        )

        # Return top_k results
        if top_k is not None:
            reranked_results = reranked_results[:top_k]

        return reranked_results

    def batch_rerank(self, queries: List[str], results_list: List[List[Dict]],
                     top_k: Optional[int] = None) -> List[List[Dict]]:
        """
        Batch rerank (for multiple queries).

        Parameters:
          queries - List of query texts
          results_list - List of retrieval results for each query
          top_k - Number of final results to return for each query

        Returns:
          List of reranked results
        """
        reranked_results_list = []
        for query, results in zip(queries, results_list):
            reranked_results = self.rerank(query, results, top_k)
            reranked_results_list.append(reranked_results)
        return reranked_results_list
