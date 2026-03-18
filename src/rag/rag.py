#定义RAG类
from .data_loader import load_multi_format_data
from .chunker import split_code_to_fine_grained_chunks,split_pdf_to_chunks
from ..utils.config import load_config
class RAG:
    def __init__(self,config_path):
        "参数"
        "config_path:配置文件保存路径"

        self.config = load_config(config_path)
        "初始化加载器"
        data_dir = self.config['data']['data_dir']
        self.all_documents = load_multi_format_data(data_dir)

        "按照文件类型进行分类"
        code_docs = []
        pdf_docs = []
        # 分类                                                                                                                                                               
        for doc in self.all_documents:                                                                                                                                       
            source = doc.metadata.get("source", "")                                                                                                                          
            if source.endswith((".cpp", ".h", ".c", ".go")):                                                                                                                 
                code_docs.append(doc)                                                                                                                                        
            elif source.endswith(".pdf"):                                                                                                                                    
                pdf_docs.append(doc)

        # 调用不同的分块逻辑进行分块
        code_chunks = split_code_to_fine_grained_chunks(code_docs)
        pdf_chunks = split_pdf_to_chunks(pdf_docs)
        self.chunks = code_chunks + pdf_chunks
        print(f"分块完成：代码块 {len(code_chunks)} 个,PDF块 {len(pdf_chunks)} 个,共 {len(self.chunks)} 个")   

    "辅助测试函数,方便调试,测试chunk表现是否正常"
    def display_chunks(self, num_samples=3):
        print(f"=== 知识库统计 ===")
        print(f"总分块数: {len(self.chunks)}")
        print("-" * 30)

        for i, chunk in enumerate(self.chunks[:num_samples]):
            print(f"【Chunk {i+1}】")
            source = chunk.metadata.get('source', 'Unknown')
            lang = chunk.metadata.get('language')
            
            print(f"源文件: {source}")
            print(f"类型/语言: {lang}")
            print(f"内容摘要:\n{chunk.page_content[0:200]}...") # 只取前200字
            print("-" * 30)
