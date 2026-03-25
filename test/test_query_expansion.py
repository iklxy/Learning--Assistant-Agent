import sys, os
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '..')))
from src.rag.rag import RAG

config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'rag.yaml')
rag = RAG(config_path=config_path)
stats = rag.get_vector_store_stats()
print(f"知识库大小: {stats}")

  # 测试一个查询
query = "什么是STL"
print(f"\n===== BM25 =====")
r1 = rag.search(query, strategy='bm25', use_expansion=False)
for r in r1[:3]:
    print(f"{r['score']}: {r['source']}")

print(f"\n===== Semantic =====")
r2 = rag.search(query, strategy='semantic', use_expansion=False)
for r in r2[:3]:
    print(f"{r['score']}: {r['source']}")

print(f"\n===== Hybrid =====")
r3 = rag.search(query, strategy='hybrid', use_expansion=False)
for r in r3[:3]:
    print(f"{r['score']}: {r['source']}")

print(f"\n===== 改写查询 =====")
expanded = rag.query_expander.expand_query(query)
for q in expanded:
    print(f"- {q}")