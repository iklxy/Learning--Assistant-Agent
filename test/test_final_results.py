import sys, os
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '..')))

from src.rag.rag import RAG


def test_query_with_expansion():
    """测试带查询改写的完整检索流程"""

    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'rag.yaml')
    rag = RAG(config_path=config_path)

    test_queries = [
        "什么是STL",
        "怎样使用vector",
        "如何实现二叉树"
    ]

    for query in test_queries:
        print("\n" + "=" * 90)
        print(f"原始查询: {query}")
        print("=" * 90)

        print("\n【查询改写结果】")
        expanded_queries = rag.query_expander.expand_query(query)
        for i, q in enumerate(expanded_queries, 1):
            print(f"  {i}. {q}")

        print("\n【检索结果 - 启用查询改写】")
        results = rag.search(query, strategy='hybrid', use_expansion=True, top_k=5)

        for result in results:
            print(f"\n  排名: {result['rank']}")
            print(f"  得分: {result['score']}")
            print(f"  来源: {result['source']}")
            if result['page']:
                print(f"  页码: {result['page']}")
            print(f"  内容摘要:")
            print(f"  {result['content'][:200]}...")
            print(f"  {'-' * 85}")


def test_without_expansion():
    """对比：不使用查询改写的结果"""

    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'rag.yaml')
    rag = RAG(config_path=config_path)

    query = "什么是STL"

    print("\n" + "=" * 90)
    print(f"对比测试: {query}")
    print("=" * 90)

    print("\n【不启用查询改写的结果】")
    results = rag.search(query, strategy='hybrid', use_expansion=False, top_k=5)

    for result in results:
        print(f"\n  排名: {result['rank']}")
        print(f"  得分: {result['score']}")
        print(f"  来源: {result['source']}")
        print(f"  内容摘要:")
        print(f"  {result['content'][:200]}...")
        print(f"  {'-' * 85}")

    print("\n" + "=" * 90)
    print(f"启用查询改写的结果")
    print("=" * 90)

    results = rag.search(query, strategy='hybrid', use_expansion=True, top_k=5)

    for result in results:
        print(f"\n  排名: {result['rank']}")
        print(f"  得分: {result['score']}")
        print(f"  来源: {result['source']}")
        print(f"  内容摘要:")
        print(f"  {result['content'][:200]}...")
        print(f"  {'-' * 85}")


if __name__ == "__main__":
    print("\n启动RAG系统查询测试...\n")

    try:
        test_query_with_expansion()
        test_without_expansion()

        print("\n" + "=" * 90)
        print("测试完成！")
        print("=" * 90)

    except Exception as e:
        print(f"\n测试失败: {e}")
        import traceback
        traceback.print_exc()
