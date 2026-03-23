import sys
import os
import json
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '..')))

from src.rag.rag import RAG

def simple_retrieval_test(chunks,query,top_k=3):
    "简单的基于关键词的检索测试函数"
    print(f"=== 简单检索测试 ===")
    print(f"查询: {query}")
    print("-" * 30)

    # 基于关键词的简单检索逻辑
    query_keywords = set(query.split())
    scored_chunks = []
    for chunk in chunks:
        content = chunk.page_content
        content_words = set(content.split())
        score = len(query_keywords.intersection(content_words))
        scored_chunks.append((score, chunk))

    # 按照得分排序并返回前top_k个结果
    scored_chunks.sort(key=lambda x: x[0], reverse=True)
    top_chunks = scored_chunks[:top_k]

    for i, (score, chunk) in enumerate(top_chunks):
        source = chunk.metadata.get('source', 'Unknown')
        print(f"Result {i+1}】")
        print(f"源文件: {source}")
        print(f"匹配度得分: {score}")
        print(f"内容摘要:\n{chunk.page_content[0:200]}...") # 只取前200字
        print("-" * 30)

def batch_retrieval_from_json(chunks, json_file_path, top_k=5):
    """
    从 JSON 文件读取查询并进行批量检索
    """
    # 1. 加载 JSON 数据
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            queries_data = json.load(f)
    except FileNotFoundError:
        return "错误：找不到指定的 JSON 文件。"
    except json.JSONDecodeError:
        return "错误：JSON 文件格式不正确。"
    
    # 2. 遍历执行检索
    for item in queries_data:
        q_text = item.get("query_text")
        
        # 容错处理：确保必须有 id 和 text 才能检索
        if  not q_text:
            continue
            
        # 调用核心引擎，传入当前的查询文本
        simple_retrieval_test(chunks, q_text, top_k)

def main():
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'rag.yaml')
    real_RAG = RAG(config_path= config_path)
    # real_RAG.display_chunks(num_samples=100)
    # 正确处理路径（从项目根目录开始）                                                                                                                                       
    test_queries_path = os.path.join(os.path.dirname(__file__), '..', real_RAG.config['data']['test_queries_path'].lstrip("./"))                                             
                                                                                                                                                                               
    batch_retrieval_from_json(real_RAG.chunks, test_queries_path, top_k=5)


if __name__ == "__main__":
    main()