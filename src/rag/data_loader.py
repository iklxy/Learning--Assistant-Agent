import os
import numpy as np
import tqdm
from langchain_community.document_loaders import (
    PyMuPDFLoader,
    TextLoader,
    UnstructuredMarkdownLoader
)
import io
from PIL import Image
from pdf2image import convert_from_path
from langchain_core.documents import Document
import yaml
import re

# Optional imports for macOS Vision Framework (only needed for scanned PDFs)
try:
    import Vision
    from Quartz import CIImage
    from Foundation import NSURL
    HAS_VISION_FRAMEWORK = True
except ImportError:
    HAS_VISION_FRAMEWORK = False

def _enhance_pdf_metadata(docs, file_path):
    """
    增强 PDF Document 的 metadata
   
    参数：
    docs - PyMuPDFLoader 返回的 Document 列表
    file_path - PDF 文件路径
    method - 加载方法标识（"PyMuPDF" 或 "Apple Vision OCR"）
   
    职责：
    为每个 Document 添加统一的自定义元数据
   
    返回：增强后的 Document 列表
    """
    enhanced_docs = []

    for doc in docs:
        metadata = doc.metadata.copy() if doc.metadata else {}

        # 添加或覆盖自定义字段
        metadata['source'] = file_path
        metadata['type'] = 'pdf'

        # 如果原始 metadata 中没有 page，尝试添加
        if 'page' not in metadata:
            metadata['page'] = doc.metadata.get('page', 1) if doc.metadata else 1

        # 创建新的 Document 对象（而不是修改原有的）
        enhanced_doc = Document(
            page_content=doc.page_content,
            metadata=metadata
        )
        enhanced_docs.append(enhanced_doc)

    return enhanced_docs

# 扫描版PDF加载器
def ScanPDFLoader(file_path):
    """         
    加载扫描版PDF（使用OCR）                                                                                                                                                 
    参数：pdf_path - PDF文件的绝对路径
    返回：Document对象列表                                                                                                                                                   
    """                                                                                                                        
                                                                                                                                                                               
    # 将PDF转换为图像                                                                                                                                                       
    images = convert_from_path(file_path)                                                                                                                                     
                                                                                                                                                                               
    all_documents = []
                                                                                                                                                                                                                                                                                                                            
    for page_num, pil_image in tqdm.tqdm(enumerate(images), total=len(images), desc="Apple Vision OCR 识别中"):
        # 1. 将图片存入内存缓存
        img_byte_arr = io.BytesIO()
        pil_image.save(img_byte_arr, format='PNG')
        img_data = img_byte_arr.getvalue()
        
        # 2. 创建 CIImage
        ci_image = CIImage.imageWithData_(img_data)
        
        # 3. 创建识别请求
        # VNRecognizeTextRequest 是 Vision 识别文本的核心类
        request = Vision.VNRecognizeTextRequest.alloc().init()
        request.setRecognitionLevel_(0) # 0 = Accurate (高精度), 1 = Fast (快速)
        request.setUsesLanguageCorrection_(True) # 开启语言纠错
        request.setRecognitionLanguages_(["zh-Hans", "en-US"]) 

        # 4. 执行请求
        handler = Vision.VNImageRequestHandler.alloc().initWithCIImage_options_(ci_image, None)
        success, error = handler.performRequests_error_([request], None)
        
        text = ""
        if success:
            results = request.results()
            for observation in results:
                # 获取置信度最高的候选结果
                candidate = observation.topCandidates_(1)[0]
                text += candidate.string() + " "

        # 5. 封装为 Document 对象
        doc = Document(
            page_content=text.strip(),
            metadata={
                "source": file_path,
                "page": page_num + 1,
                "type":"pdf"
            }
        )
        all_documents.append(doc)
                                                                                                                                                                               
    return all_documents

def load_markdown_file(file_path):
    """
    Load Markdown file.

    Parameters: file_path - Absolute path to Markdown file
    Returns: List of Document objects
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 移除 YAML frontmatter
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            content = parts[2]

    enhanced_docs = []
    doc = Document(
        page_content=content.strip(),
        metadata={
            'source': file_path,
            'type': 'markdown',
            'page': 1
        }
    )
    enhanced_docs.append(doc)

    return enhanced_docs


# Main loader for multiple file formats
def load_multi_format_data(data_dir, cache_dir, use_cache=True):
    """
    Load documents from multiple file formats (PDF, Markdown, etc.)

    Parameters:
      data_dir: Directory containing data files
      cache_dir: Directory for caching loaded documents
      use_cache: Whether to use cache. If enabled and cache exists, load from cache;
                 otherwise load fresh data and generate cache
    """
    all_documents = []

    # Check if cache exists and is enabled
    cache_file = os.path.join(cache_dir, "cached_documents.pkl")
    if use_cache and os.path.exists(cache_file):
        print("Cache file detected. Loading from cache...")
        import pickle
        with open(cache_file, 'rb') as f:
            all_documents = pickle.load(f)
        print(f"Successfully loaded {len(all_documents)} documents from cache")
        return all_documents

    # Load files from disk
    for root, dirs, files in os.walk(data_dir):
        for file in files:
            file_path = os.path.join(root, file)

            # Check file type
            if file.endswith(".pdf"):
                # Try PyMuPDFLoader first (for text-based PDFs)
                loader = PyMuPDFLoader(file_path)
                docs = loader.load()

                # If no text extracted, use OCR (for scanned PDFs)
                if not docs or all(len(doc.page_content.strip()) == 0 for doc in docs):
                    print(f"Detected scanned PDF: {file_path}. Starting OCR processing...")
                    docs = ScanPDFLoader(file_path)
                else:
                    docs = _enhance_pdf_metadata(docs, file_path)

                all_documents.extend(docs)

            elif file.endswith(".md"):
                # Load Markdown file
                try:
                    docs = load_markdown_file(file_path)
                    all_documents.extend(docs)
                except Exception as e:
                    print(f"Failed to load Markdown file: {file_path}, Error: {e}")

    print(f"Successfully loaded {len(all_documents)} documents")

    # Save to cache after loading, if cache is enabled
    if use_cache:
        os.makedirs(cache_dir, exist_ok=True)
        import pickle
        with open(cache_file, 'wb') as f:
            pickle.dump(all_documents, f)
        print(f"Saved {len(all_documents)} documents to cache")
        
    return all_documents
