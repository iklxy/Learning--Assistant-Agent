# 定义数据的分块逻辑
import tree_sitter_cpp as tcpp
from tree_sitter import Parser,Language
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter                                                                                                      
from langchain_core.documents import Document
# 定义CPP的解析器
parser = Parser(Language(tcpp.language()))

def split_pdf_to_chunks(pdf_documents, chunk_size=512, chunk_overlap=100):                                                                                                   
    """                                                                                                                                                                      
      PDF 文本分块（使用 LangChain 的递归字符分割器）
      参数：                                                                                                                                                                   
        pdf_documents: 来自 PDF 的文档列表                                                                                                                                     
        chunk_size: 分块大小（字符数）                                                                                                                                         
        chunk_overlap: 块之间的重叠字符数                                                                                                                                      
      返回：分块后的文档列表                                                                                                                                                   
    """                                                                                                                                                                                                                                                                                                  
                                                                                                                                                                               
    # 创建递归字符分割器                                                                                                                                      
    splitter = RecursiveCharacterTextSplitter(                                                                                                                               
        chunk_size=chunk_size,                                                                                                                                               
        chunk_overlap=chunk_overlap,                                                                                                                                         
        separators=["\n\n", "\n", "。", "！", "？", " ", ""]  # 优先按这些分隔符分                                                                                           
    )                                                                                                                                                                        
                  
    chunked_docs = []                                                                                                                                                        
                  
    for doc in pdf_documents:                                                                                                                                                
        # 分割文本
        chunks = splitter.split_text(doc.page_content)                                                                                                                       
                                                                                                                                                                               
        # 为每个 chunk 创建新的 Document 对象                                                                                                                                
        for chunk_idx, chunk in enumerate(chunks):                                                                                                                           
            new_doc = Document(                                                                                                                                              
                page_content=chunk,                                                                                                                                          
                metadata={                                                                                                                                                   
                    "source": doc.metadata.get("source"),                                                                                                                    
                    "page": doc.metadata.get("page"),                                                                                                                        
                    "chunk_in": chunk_idx,                                                                                                                                
                    "type": "pdf"                                                                                                                   
                }                                                                                                                                                            
            )                                                                                                                                                                
            chunked_docs.append(new_doc)  

    return chunked_docs       
