# 定义数据的分块逻辑
import tree_sitter_cpp as tcpp
from tree_sitter import Parser,Language
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter                                                                                                      
from langchain_core.documents import Document
# 定义CPP的解析器
parser = Parser(Language(tcpp.language()))

def split_code_to_fine_grained_chunks(code_documents):
    "参数:"
    "code_documents:数据加载器加载得到的所有文件"
    chunked_docs = []
    
    for doc in code_documents:
        code_bytes = doc.page_content.encode('utf-8')
        file_path = doc.metadata.get("source", "unknown")
        tree = parser.parse(code_bytes)

        # 内部递归函数
        def walk(node, current_class=None):
            # 1. 识别类或结构体名称
            new_class_context = current_class
            if node.type in ['class_specifier', 'struct_specifier']:
                # 尝试寻找类名节点
                name_node = node.child_by_field_name('name')
                if name_node:
                    new_class_context = code_bytes[name_node.start_byte:name_node.end_byte].decode('utf-8')

            # 2. 识别函数定义
            if node.type == 'function_definition':
                content = code_bytes[node.start_byte:node.end_byte].decode('utf-8')
                
                # 构造层级描述，例如 "MyClass::myMethod"
                func_identity = content.split('{')[0].strip() # 简单提取函数签名
                full_name = f"{current_class}::{func_identity}" if current_class else func_identity
                
                "添加metadata"
                "source:该代码文件所在的绝对路径"
                "class_context:函数所属的类"
                "signature:函数签名"
                "start_line:开始行"

                new_doc = Document(
                    page_content=content,
                    metadata={
                        "source": file_path,
                        "class_context": current_class,
                        "signature": full_name,
                        "start_line": node.start_point[0] + 1,
                        "type":"cpp"
                    }
                )
                chunked_docs.append(new_doc)
                return 

            # 3. 继续遍历子节点，并将当前类上下文向下传递
            for child in node.children:
                walk(child, new_class_context)

        walk(tree.root_node)
        
    return chunked_docs

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
                    "chunk_index": chunk_idx,                                                                                                                                
                    "type": "pdf"                                                                                                                   
                }                                                                                                                                                            
            )                                                                                                                                                                
            chunked_docs.append(new_doc)  

    return chunked_docs       
