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

# 总加载器
def load_multi_format_data(data_dir,cache_dir,use_cache=True):
    "参数："
    "data_dir:存放配置文件的文件夹路径,其中存储着文件存储的真实路径"
    "cache_dir:存放缓存文件的文件夹路径"
    "use_cache:是否启用缓存,如果启用且缓存文件存在,则直接加载缓存文件,否则重新加载数据并生成缓存文件"
    all_documents = []

    # 先检查是否启用缓存，并且缓存文件存在
    cache_file = os.path.join(cache_dir, "cached_documents.pkl")
    if use_cache and os.path.exists(cache_file):
        print("检测到缓存文件，正在加载...")
        import pickle
        with open(cache_file, 'rb') as f:
            all_documents = pickle.load(f)
        print(f"成功从缓存加载 {len(all_documents)} 个文档")
        return all_documents
    
    # 加载文件
    for root, dirs, files in os.walk(data_dir):
        for file in files:
            file_path = os.path.join(root, file)

            # 文件类型检查
            if file.endswith(".pdf"):
                # 先用PyMuPDFLoader尝试加载（文字版PDF）
                loader = PyMuPDFLoader(file_path)
                docs = loader.load()

                # 如果没有提取到文字，改用OCR（扫描版PDF）
                if not docs or all(len(doc.page_content.strip()) == 0 for doc in docs):
                    print(f"检测到扫描版PDF: {file_path}，开始OCR处理...")
                    docs = ScanPDFLoader(file_path)
                else:
                    docs = _enhance_pdf_metadata(docs, file_path)

                all_documents.extend(docs)    
    print("成功加载",len(all_documents),"个文件")

    # 加载完成后，如果启用缓存，则将结果保存到缓存文件
    if use_cache:
        os.makedirs(cache_dir, exist_ok=True)
        import pickle
        with open(cache_file, 'wb') as f:
            pickle.dump(all_documents, f)
        print(f"已将 {len(all_documents)} 个文档保存到缓存")
        
    return all_documents
