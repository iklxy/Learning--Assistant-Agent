# 定义数据的分块逻辑
import tree_sitter_cpp as tcpp
from tree_sitter import Parser,Language
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
import re
# 定义CPP的解析器
parser = Parser(Language(tcpp.language()))

def split_pdf_to_chunks(pdf_documents, chunk_size=512, chunk_overlap=100):
    """
    PDF text chunking using LangChain's recursive character text splitter.

    Parameters:
      pdf_documents: List of documents from PDF
      chunk_size: Maximum characters per chunk
      chunk_overlap: Character overlap between chunks

    Returns: List of chunked documents
    """

    # Create recursive character text splitter optimized for English
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""]  # Split by paragraph, line, sentence, word, char
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


def split_markdown_to_chunks(markdown_documents, chunk_size=512, chunk_overlap=100):
    """
    Markdown text chunking based on Markdown structure.

    Splits content by secondary headers (##) to preserve logical sections.

    Parameters:
      markdown_documents: List of documents from Markdown files
      chunk_size: Maximum characters per chunk (content exceeding this will be further split)
      chunk_overlap: Character overlap between chunks

    Returns: List of chunked documents
    """
    chunked_docs = []

    for doc in markdown_documents:
        content = doc.page_content
        source = doc.metadata.get('source', 'unknown')

        # Step 1: Extract main title (first level header)
        main_title_match = re.search(r'^#\s+(.+?)$', content, re.MULTILINE)
        main_title = main_title_match.group(1).strip() if main_title_match else "Untitled"

        # Step 2: Split content by secondary headers (##)
        sections = re.split(r'(^##\s+.+?$)', content, flags=re.MULTILINE)

        current_chunk = f"# {main_title}\n"  # 初始化为一级标题
        section_idx = 0

        for i, section in enumerate(sections):
            if not section.strip():
                continue

            # Check if this is a secondary header
            if section.startswith("##"):
                # If current chunk is not empty and not just the title, save it
                if len(current_chunk.strip()) > len(f"# {main_title}\n"):
                    # If content exceeds chunk_size, split further
                    if len(current_chunk) > chunk_size:
                        sub_chunks = _split_long_section(
                            current_chunk, chunk_size, chunk_overlap, source, section_idx
                        )
                        chunked_docs.extend(sub_chunks)
                    else:
                        chunk_doc = Document(
                            page_content=current_chunk.strip(),
                            metadata={
                                'source': source,
                                'type': 'markdown',
                                'section_idx': section_idx,
                                'section_title': section.strip(),
                            }
                        )
                        chunked_docs.append(chunk_doc)

                # Start new chunk with this header
                current_chunk = f"# {main_title}\n\n{section}\n"
                section_idx += 1
            else:
                # Content portion
                current_chunk += section + "\n"

        # Save last chunk
        if len(current_chunk.strip()) > len(f"# {main_title}\n"):
            if len(current_chunk) > chunk_size:
                sub_chunks = _split_long_section(
                    current_chunk, chunk_size, chunk_overlap, source, section_idx
                )
                chunked_docs.extend(sub_chunks)
            else:
                chunk_doc = Document(
                    page_content=current_chunk.strip(),
                    metadata={
                        'source': source,
                        'type': 'markdown',
                        'section_idx': section_idx,
                    }
                )
                chunked_docs.append(chunk_doc)

    return chunked_docs


def _split_long_section(text, chunk_size, chunk_overlap, source, section_idx):
    """
    Further split long secondary header content that exceeds chunk_size.

    Parameters:
      text - Text to split
      chunk_size - Chunk size limit
      chunk_overlap - Character overlap between chunks
      source - Document source
      section_idx - Index of the secondary header section

    Returns: List of split Document objects
    """
    # Use recursive character text splitter optimized for English
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""]
    )

    chunks = splitter.split_text(text)
    docs = []

    for chunk_idx, chunk in enumerate(chunks):
        chunk_doc = Document(
            page_content=chunk,
            metadata={
                'source': source,
                'type': 'markdown',
                'section_idx': section_idx,
                'sub_chunk_idx': chunk_idx,
            }
        )
        docs.append(chunk_doc)

    return docs
