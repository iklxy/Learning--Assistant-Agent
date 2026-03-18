import os
import numpy as np
import tqdm
from langchain_community.document_loaders import (
    PyMuPDFLoader, 
    TextLoader, 
    UnstructuredMarkdownLoader
)
import Vision
from Quartz import CIImage
from Foundation import NSURL
import io
from PIL import Image
from pdf2image import convert_from_path
from langchain_core.documents import Document
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
                "method": "Apple Vision OCR",
                "type":"pdf"
            }
        )
        all_documents.append(doc)
                                                                                                                                                                               
    return all_documents

# 总加载器
def load_multi_format_data(data_dir):
    "参数："
    "data_dir:存放配置文件的文件夹路径,其中存储着文件存储的真实路径"

    all_documents = []

    # 加载文件
    for root, dirs,files in os.walk(data_dir):
        for file in files:
            file_path = os.path.join(root, file)
            if file.endswith(".cpp") or file.endswith(".h") or file.endswith(".c") or file.endswith(".go"):
                loader = TextLoader(file_path)                                                                                                                                   
                all_documents.extend(loader.load())
            elif file.endswith(".pdf"):
            # 先用PyMuPDFLoader尝试加载                                                                                                                          
                loader = PyMuPDFLoader(file_path)                                                                                                                                        
                docs = loader.load()                                                                                                                                                     
                                                                                                                                                                               
                # 如果没有提取到文字，改用OCR                                                                                                                              
                if not docs or all(len(doc.page_content.strip()) == 0 for doc in docs):
                    print(f"检测到扫描版PDF: {file_path}，开始OCR处理...")                                                                                                               
                    docs = ScanPDFLoader(file_path)                                                                                                                                   
                all_documents.extend(docs)
                
    print("成功加载",len(all_documents),"个文件")
    return all_documents
