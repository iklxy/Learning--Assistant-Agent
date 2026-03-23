# 实现了向量存储功能类
import chromadb
import os
import hashlib
from typing import List, Dict, Optional
from langchain_core.documents import Document

class VectorStore:
    def __init__(self, embedder, persist_directory: str, collection_name: str, distance_metric: str = "cosine"):
        """
        初始化向量存储

        参数：
          embedder - 嵌入模型实例
          persist_directory - 向量数据库的持久化目录路径
          collection_name - 向量数据库中集合的名称
          distance_metric - 用于相似度计算的距离度量方法，默认为'cosine'
        """
        self.embedder = embedder
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self.distance_metric = distance_metric

        # 确保目录存在
        os.makedirs(self.persist_directory, exist_ok=True)

        self.client = chromadb.PersistentClient(path=self.persist_directory)

        # 创建或获取 collection
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": self.distance_metric}
        )

    @staticmethod
    def _generate_chunk_id(source: str, index: int) -> str:
        """
        为 chunk 生成唯一 ID
   
        格式：chunk_<source_hash>_<index>
        例如：chunk_a3f7b2c1_001
   
        原因：
        - 需要唯一标识每个 chunk
        - hash source 避免 ID 过长
        - index 保证同一源文件的 chunks 不冲突
        """
        # 对源文件路径进行 hash
        source_hash = hashlib.md5(source.encode()).hexdigest()[:8]

        # 生成最终 ID
        chunk_id = f"chunk_{source_hash}_{index:04d}"

        return chunk_id
    
    def add_chunks(self, chunks: list[Document]) -> None:
        """
        核心方法：将增强的 chunks 添加到向量库
   
        参数：chunks - 带有 embedding 的 Document 列表
   
        职责：
        1. 提取向量、文本、metadata
        2. 生成唯一 ID
        3. 存储到 Chroma
        4. 保存到磁盘
        """
        if not chunks:
            print("chunks 列表为空")
            return

        print(f"开始添加 {len(chunks)} 个 chunks 到向量库...")

        # 准备数据
        ids = []
        embeddings = []
        metadatas = []
        documents = []

        for idx, chunk in enumerate(chunks):
            # 步骤1：生成 ID
            source = chunk.metadata.get('source', 'unknown')
            chunk_id = self._generate_chunk_id(source, idx)
            ids.append(chunk_id)

            # 步骤2：提取向量
            embedding_data = chunk.metadata.get('embedding')
            if embedding_data is None:
                raise ValueError(f"Chunk {chunk_id} 没有 embedding 字段")

            embeddings.append(embedding_data)

            # 步骤3：提取 metadata
            metadata = {k: v for k, v in chunk.metadata.items() if k != 'embedding'}
            # 确保 metadata 中的值都是可序列化的
            metadata = self._sanitize_metadata(metadata)
            metadatas.append(metadata)

            # 步骤4：提取文本内容
            documents.append(chunk.page_content)

        # 步骤5：批量添加到 Chroma
        try:
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                metadatas=metadatas,
                documents=documents
            )
            print(f"成功添加 {len(chunks)} 个 chunks")
        except Exception as e:
            print(f"添加失败: {e}")
            raise

        # 注意：PersistentClient 会自动持久化数据，无需手动调用 persist()

    @staticmethod
    def _sanitize_metadata(metadata: dict) -> dict:
        """清理 metadata，确保所有值都可序列化"""
        sanitized = {}
        for k, v in metadata.items():
            if isinstance(v, (str, int, float, bool, type(None))):
                sanitized[k] = v
            elif isinstance(v, (list, tuple)):
                sanitized[k] = str(v)  # 转为字符串
            else:
                sanitized[k] = str(v)
        return sanitized

    def search(self, query_vector: List[float], top_k: int = 5,
               metadata_filter: Optional[Dict] = None) -> List[Dict]:
        """
        核心方法：向量相似度搜索

        参数：
          query_vector - 查询向量（float list）
          top_k - 返回结果数量
          metadata_filter - 可选的元数据过滤条件

        返回：
          结果列表，每个结果包含：
            {
              "chunk_id": "chunk_a3f7b2c1_001",
              "content": "...",
              "metadata": {...},
              "distance": 0.15  # 距离越小相似度越高
            }
        """
        print(f"搜索最相似的 {top_k} 个 chunks...")

        try:
            # 调用 Chroma 的查询接口
            results = self.collection.query(
                query_embeddings=[query_vector],  # 必须是列表
                n_results=top_k,
                where=metadata_filter if metadata_filter else None
            )

            # 解析结果
            # Chroma 返回的格式：
            # {
            #   'ids': [['chunk_001', 'chunk_002', ...]],
            #   'distances': [[0.15, 0.23, ...]],
            #   'metadatas': [[{...}, {...}, ...]],
            #   'documents': [['content1', 'content2', ...]]
            # }

            parsed_results = []
            if results['ids']:
                ids = results['ids'][0]
                distances = results['distances'][0]
                metadatas = results['metadatas'][0]
                documents = results['documents'][0]

                for chunk_id, distance, metadata, content in zip(
                    ids, distances, metadatas, documents
                ):
                    parsed_results.append({
                        "chunk_id": chunk_id,
                        "content": content,
                        "metadata": metadata,
                        "distance": float(distance),
                        "similarity": 1 - float(distance)  # 转为相似度（0-1）
                    })

            print(f"搜索完成，找到 {len(parsed_results)} 个结果")
            return parsed_results

        except Exception as e:
            print(f"搜索失败: {e}")
            raise

    def get_chunk_by_id(self, chunk_id: str) -> Optional[Dict]:
        """
        通过 ID 获取单个 chunk

        参数：chunk_id - chunk 的唯一标识

        返回：
          包含内容、metadata、embedding 的字典
          如果 chunk 不存在，返回 None
        """
        try:
            results = self.collection.get(
                ids=[chunk_id],
                include=['embeddings', 'metadatas', 'documents']
            )

            if not results['ids']:
                print(f"未找到 chunk: {chunk_id}")
                return None

            return {
                "chunk_id": results['ids'][0],
                "content": results['documents'][0],
                "metadata": results['metadatas'][0],
                "embedding": results['embeddings'][0]
            }
        except Exception as e:
            print(f"获取失败: {e}")
            raise

    def delete_chunks(self, chunk_ids: List[str]) -> None:
        """
        删除指定的 chunks

        参数：chunk_ids - 要删除的 chunk ID 列表
        """
        try:
            self.collection.delete(ids=chunk_ids)
            # PersistentClient 会自动持久化
            print(f"删除了 {len(chunk_ids)} 个 chunks")
        except Exception as e:
            print(f"删除失败: {e}")
            raise

    def get_stats(self) -> Dict:
        """
        获取向量库统计信息

        返回：
          包含向量库统计数据的字典
        """
        total_chunks = self.collection.count()

        return {
            "total_chunks": total_chunks,
            "collection_name": self.collection_name,
            "persist_dir": self.persist_directory,
            "distance_metric": self.distance_metric
        }

    def clear(self) -> None:
        """
        清空向量库

        删除当前 collection，然后重建一个新的空 collection
        """
        try:
            # 删除 collection 再重建
            self.client.delete_collection(name=self.collection_name)
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": self.distance_metric}
            )
            # PersistentClient 会自动持久化
            print("向量库已清空")
        except Exception as e:
            print(f"清空失败: {e}")
            raise
