# 定义嵌入模型类
from langchain_openai import OpenAIEmbeddings
import os
from dotenv import load_dotenv
import numpy as np
from langchain_core.documents import Document

# 加载环境变量
# 注意：请确保在项目根目录下有一个 .env 文件，其中包含 OPENAI_API_KEY 和 OPENAI_API_BASE 的值(本项目使用的中转站是closeAI，具体设置参考https://platform.closeai-asia.com)

load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv('OPENAI_API_KEY')
os.environ["OPENAI_API_BASE"] = os.getenv('OPENAI_API_BASE')

# 定义Embedder类
class Embedder:
    def __init__(self,model_name,dimensions):
        "参数："
        "model_name: Ollama模型名称,需要与Ollama中定义的模型名称一致"
        "dimensions:嵌入向量的维度"
        self.embedder = OpenAIEmbeddings(
            model=model_name,
            dimensions=dimensions
        )

    def embed_text(self,text)->list[float]:
        "参数："
        "text:需要生成嵌入的文本字符串"

        text = text.replace("\n", " ")  # 替换换行符，确保输入是单行文本
        if not text.strip():
            return np.zeros(self.embedder.dimensions)  # 返回全零向量
        
        vector = self.embedder.embed_query(text)
        return vector
    
    def embed_texts(self,texts)->list[list[float]]:
        "参数："
        "texts:需要生成嵌入的文本字符串列表"

        texts = [text.replace("\n", " ") for text in texts]  # 替换换行符，确保输入是单行文本
        if not any(text.strip() for text in texts):
            return np.zeros((len(texts), self.embedder.dimensions))  # 返回全零矩阵
        
        vector = self.embedder.embed_documents(texts)
        return vector
    
    def embed_chunks(self,chunks)->list[Document]:
        "参数："
        "chunks:需要生成嵌入的Chunk对象列表"
        "返回的是增强后的Chunk对象列表,每个Chunk对象包含原始内容和对应的嵌入向量"
        texts = [chunk.page_content for chunk in chunks]
        "调用embed_texts方法生成嵌入向量，并且将向量添加到每个Chunk的metadata中"

        vectors = self.embed_texts(texts)
        enhanced_chunks = []
        for chunk, vector in zip(chunks, vectors):
            enhanced_chunk = Document(
                page_content=chunk.page_content,
                metadata={
                    **chunk.metadata,
                    "embedding": vector
                }
            )
            enhanced_chunks.append(enhanced_chunk)
        return enhanced_chunks