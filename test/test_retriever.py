import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '..')))

from src.rag.rag import RAG


def test_bm25_retriever():
    """测试BM25关键词检索"""
    print("\n" + "="*80)
    print("测试 BM25 关键词检索")
    print("="*80)

    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'rag.yaml')
    rag = RAG(config_path=config_path)

    query = "什么是STL"
    print(f"\n查询: {query}")

    results = rag.search(query, top_k=5, strategy='bm25')
    rag.display_search_results(results, show_full_content=False)

    return results


def test_semantic_retriever():
    """测试语义向量检索"""
    print("\n" + "="*80)
    print("测试 语义向量检索")
    print("="*80)

    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'rag.yaml')
    rag = RAG(config_path=config_path)

    query = "什么是STL"
    print(f"\n查询: {query}")

    results = rag.search(query, top_k=5, strategy='semantic')
    rag.display_search_results(results, show_full_content=False)

    return results


def test_hybrid_retriever():
    """测试混合检索（BM25 + 语义）"""
    print("\n" + "="*80)
    print("测试 混合检索 (BM25 + 语义搜索)")
    print("="*80)

    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'rag.yaml')
    rag = RAG(config_path=config_path)

    query = "什么是STL"
    print(f"\n查询: {query}")

    results = rag.search(query, top_k=5, strategy='hybrid')
    rag.display_search_results(results, show_full_content=False)

    return results


def test_comparison():
    """对比三种检索策略"""
    print("\n" + "="*80)
    print("三种检索策略对比测试")
    print("="*80)

    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'rag.yaml')
    rag = RAG(config_path=config_path)

    queries = [
        "什么是STL",
        "vector的用法",
        "如何使用链表"
    ]

    for query in queries:
        print(f"\n\n查询: {query}")
        print("-" * 80)

        bm25_results = rag.search(query, top_k=3, strategy='bm25')
        semantic_results = rag.search(query, top_k=3, strategy='semantic')
        hybrid_results = rag.search(query, top_k=3, strategy='hybrid')

        print("\n【BM25检索结果】")
        for result in bm25_results:
            print(f"  rank: {result['rank']}, score: {result['score']}, "
                  f"source: {result['source']}")

        print("\n【语义检索结果】")
        for result in semantic_results:
            print(f"  rank: {result['rank']}, score: {result['score']}, "
                  f"source: {result['source']}")

        print("\n【混合检索结果】")
        for result in hybrid_results:
            print(f"  rank: {result['rank']}, score: {result['score']}, "
                  f"source: {result['source']}")


def test_alpha_parameter():
    """测试不同的alpha参数对混合检索结果的影响"""
    print("\n" + "="*80)
    print("不同alpha参数的混合检索对比")
    print("="*80)

    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'rag.yaml')
    rag = RAG(config_path=config_path)

    query = "什么是STL"
    alpha_values = [0.1, 0.3, 0.5, 0.7, 0.9]

    print(f"\n查询: {query}")
    print("-" * 80)

    for alpha in alpha_values:
        print(f"\nalpha = {alpha} (BM25权重{alpha*100:.0f}%, 语义权重{(1-alpha)*100:.0f}%)")
        results = rag.hybrid_retriever.search(query, top_k=3, alpha=alpha)

        for result in results:
            bm25_score = float(result.get('bm25_score', 0))
            semantic_score = float(result.get('semantic_score', 0))
            final_score = float(result['score'])

            print(f"  score: {final_score:.4f} "
                  f"(BM25: {bm25_score:.4f}, semantic: {semantic_score:.4f}) "
                  f"source: {result['source']}")


if __name__ == "__main__":
    print("\n开始测试混合检索系统...")

    try:
        test_bm25_retriever()
        test_semantic_retriever()
        test_hybrid_retriever()
        test_comparison()
        test_alpha_parameter()

        print("\n" + "="*80)
        print("所有测试完成")
        print("="*80)

    except Exception as e:
        print(f"\n测试失败: {e}")
        import traceback
        traceback.print_exc()
