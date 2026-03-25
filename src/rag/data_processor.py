"""
Data preprocessing and enhancement module.
Improves data quality and retrieval performance.
"""

import re
from typing import List, Dict, Tuple
from langchain_core.documents import Document


class DataCleaner:
    """Data cleaner - remove noise from PDF and Markdown extraction"""

    @staticmethod
    def clean_text(text: str) -> str:
        """
        Clean extracted text from PDF/Markdown documents

        Removes:
          - Extra whitespace and newlines
          - Header/footer markers
          - Special control characters
          - Multiple consecutive blank lines
          - Markdown frontmatter
        """
        if not text:
            return text

        # 1. Remove YAML frontmatter (if present)
        if text.startswith('---'):
            parts = text.split('---', 2)
            if len(parts) >= 3:
                text = parts[2]

        # 2. Remove special control characters
        text = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]', '', text)

        # 3. Normalize line breaks
        text = text.replace('\r\n', '\n').replace('\r', '\n')

        # 4. Remove common header/footer patterns
        lines = text.split('\n')
        cleaned_lines = []
        for line in lines:
            # Skip lines that are only page numbers or separators
            if re.match(r'^\s*[-–—_]+\s*$', line):
                continue
            if re.match(r'^\s*\d+\s*$', line) and len(line.strip()) <= 5:
                continue
            # Skip very short lines (likely headers)
            if len(line.strip()) > 2:
                cleaned_lines.append(line)

        text = '\n'.join(cleaned_lines)

        # 5. Merge multiple consecutive blank lines into single blank line
        text = re.sub(r'\n\n\n+', '\n\n', text)

        # 6. Remove trailing whitespace from each line
        text = '\n'.join(line.rstrip() for line in text.split('\n'))

        return text.strip()

    @staticmethod
    def extract_sections(text: str) -> List[Tuple[str, str]]:
        """
        Extract sections and subsections from text

        Returns: [(title, content), ...]
        """
        # Simple section detection patterns
        # Matches "1. Title", "1.1 Subtitle", "## Markdown Header", etc.
        patterns = [
            r'^(#{1,6}\s+.*?)$',  # Markdown headers
            r'^([\d]+\.[\d]+ .*?)$',  # Numbered titles (1.1, 2.3, etc.)
            r'^([\d]+\. .*?)$',  # Simple numbered titles (1., 2., etc.)
        ]

        sections = []
        current_title = "Introduction"
        current_content = []

        for line in text.split('\n'):
            is_title = False
            for pattern in patterns:
                if re.match(pattern, line):
                    # Save previous section
                    if current_content:
                        sections.append((current_title, '\n'.join(current_content)))
                    current_title = line.strip().lstrip('#').strip()
                    current_content = []
                    is_title = True
                    break

            if not is_title and line.strip():
                current_content.append(line)

        # Save last section
        if current_content:
            sections.append((current_title, '\n'.join(current_content)))

        return sections

    @staticmethod
    def generate_summary(text: str, max_length: int = 100) -> str:
        """
        Generate text summary (simple implementation: first N sentences).

        Parameters:
          text - Input text
          max_length - Maximum characters for summary
        """
        # Split by sentence boundaries (period, question mark, newline)
        sentences = re.split(r'[.!?\n]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]

        summary = ""
        for sentence in sentences:
            if len(summary) + len(sentence) <= max_length:
                summary += sentence + ". "
            else:
                break

        return summary.strip() if summary else text[:max_length]


class ChunkEnhancer:
    """Chunk enhancer - add context and metadata to chunks"""

    @staticmethod
    def add_context_title(chunks: List[Document], documents: List[Document]) -> List[Document]:
        """
        Add source document title/topic to each chunk.

        Parameters:
          chunks - List of chunked documents
          documents - List of original documents

        Returns: List of enhanced chunks
        """
        # 为原始文档创建标题索引
        doc_titles = {}
        for doc in documents:
            source = doc.metadata.get('source', 'unknown')
            # 尝试从内容提取标题
            first_line = doc.page_content.split('\n')[0]
            title = first_line[:50] if len(first_line) > 10 else source
            doc_titles[source] = title

        # 为chunks添加上下文标题
        for chunk in chunks:
            source = chunk.metadata.get('source', 'unknown')
            if source in doc_titles:
                chunk.metadata['document_title'] = doc_titles[source]

        return chunks

    @staticmethod
    def add_chunk_summary(chunks: List[Document]) -> List[Document]:
        """
        Generate summary for each chunk.

        Parameters:
          chunks - List of chunks

        Returns: Chunks with summaries added
        """
        for chunk in chunks:
            summary = DataCleaner.generate_summary(chunk.page_content, max_length=80)
            chunk.metadata['summary'] = summary

        return chunks

    @staticmethod
    def extract_keywords(text: str, top_k: int = 5) -> List[str]:
        """
        Extract keywords from text (simple frequency-based implementation)

        Parameters:
          text - Input text
          top_k - Number of keywords to return
        """
        # Common English stopwords
        stopwords = {
            'the', 'is', 'at', 'which', 'on', 'a', 'an', 'and', 'or', 'in', 'of', 'to',
            'for', 'by', 'with', 'as', 'be', 'from', 'are', 'has', 'have', 'that',
            'this', 'it', 'you', 'we', 'i', 'they', 'not', 'can', 'will', 'than',
            'if', 'also', 'how', 'when', 'where', 'what', 'who', 'why', 'such',
            'more', 'all', 'some', 'any', 'each', 'every', 'both', 'other', 'many',
            'no', 'up', 'so', 'into', 'would', 'could', 'should', 'may', 'should'
        }

        # Simple tokenization (based on word boundaries)
        words = re.findall(r'\b[a-z_][a-z0-9_]*\b', text.lower())
        word_freq = {}
        for word in words:
            if len(word) > 2 and word not in stopwords:
                word_freq[word] = word_freq.get(word, 0) + 1

        # Sort by frequency
        keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in keywords[:top_k]]

    @staticmethod
    def add_keywords(chunks: List[Document]) -> List[Document]:
        """
        Add keywords to each chunk.

        Parameters:
          chunks - List of chunks

        Returns: Chunks with keywords added
        """
        for chunk in chunks:
            keywords = ChunkEnhancer.extract_keywords(chunk.page_content, top_k=5)
            chunk.metadata['keywords'] = keywords

        return chunks


class DataProcessor:
    """Comprehensive data processor"""

    def __init__(self, enable_cleaning: bool = True, enable_summary: bool = True,
                 enable_keywords: bool = True):
        """
        Initialize data processor.

        Parameters:
          enable_cleaning - Whether to enable data cleaning
          enable_summary - Whether to generate chunk summaries
          enable_keywords - Whether to extract chunk keywords
        """
        self.enable_cleaning = enable_cleaning
        self.enable_summary = enable_summary
        self.enable_keywords = enable_keywords

    def process_documents(self, documents: List[Document]) -> List[Document]:
        """
        Process raw documents.

        Parameters:
          documents - Loaded raw documents

        Returns: List of cleaned documents
        """
        processed_docs = []

        for doc in documents:
            if self.enable_cleaning:
                cleaned_content = DataCleaner.clean_text(doc.page_content)
            else:
                cleaned_content = doc.page_content

            processed_doc = Document(
                page_content=cleaned_content,
                metadata=doc.metadata.copy()
            )
            processed_docs.append(processed_doc)

        return processed_docs

    def process_chunks(self, chunks: List[Document], original_documents: List[Document]) -> List[Document]:
        """
        Process chunked documents.

        Parameters:
          chunks - Chunked documents
          original_documents - Original documents (used to extract titles, etc.)

        Returns: Enhanced chunks
        """
        enhanced_chunks = chunks.copy()

        # 添加文档标题
        enhanced_chunks = ChunkEnhancer.add_context_title(enhanced_chunks, original_documents)

        # 生成摘要
        if self.enable_summary:
            enhanced_chunks = ChunkEnhancer.add_chunk_summary(enhanced_chunks)

        # 提取关键词
        if self.enable_keywords:
            enhanced_chunks = ChunkEnhancer.add_keywords(enhanced_chunks)

        return enhanced_chunks

    def get_chunk_info(self, chunk: Document) -> Dict:
        """
        Get complete chunk information (for debugging).

        Parameters:
          chunk - Chunk document

        Returns: Dictionary with all metadata
        """
        return {
            'content': chunk.page_content,
            'source': chunk.metadata.get('source'),
            'page': chunk.metadata.get('page'),
            'document_title': chunk.metadata.get('document_title', 'N/A'),
            'summary': chunk.metadata.get('summary', 'N/A'),
            'keywords': chunk.metadata.get('keywords', []),
            'chunk_idx': chunk.metadata.get('chunk_in', -1),
        }
