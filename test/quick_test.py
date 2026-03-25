import sys, os
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '..')))

from src.rag.rag import RAG

config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'rag.yaml')
rag = RAG(config_path=config_path)

query = "什么是STL"

print("\n" + "=" * 90)
print(f"查询: {query}")
print("=" * 90)

print("\n【查询改写】")
expanded_queries = rag.query_expander.expand_query(query)
for i, q in enumerate(expanded_queries, 1):
    print(f"{i}. {q}")

print("\n【混合检索 + 查询改写结果】\n")
results = rag.search(query, strategy='hybrid', use_expansion=True, top_k=5)

for result in results:
    print(f"排名: {result['rank']} | 得分: {result['score']} | 来源: {result['source']}")
    print(f"内容: {result['content'][:150]}...")
    print("-" * 90)
