import io
import re
import uuid
from typing import List, Dict, Tuple
import pypdf
from app.models.schemas import DocumentChunk

class DocumentProcessor:
    def __init__(self, chunk_size: int = 450, chunk_overlap: int = 60):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def extract_text_from_bytes(self, file_bytes: bytes, filename: str) -> str:
        """Extracts clean UTF-8 text from PDF, TXT, or MD files."""
        lower_name = filename.lower()
        if lower_name.endswith(".pdf"):
            try:
                reader = pypdf.PdfReader(io.BytesIO(file_bytes))
                extracted_pages = []
                for idx, page in enumerate(reader.pages):
                    page_text = page.extract_text() or ""
                    if page_text.strip():
                        extracted_pages.append(f"--- [Page {idx + 1}] ---\n{page_text.strip()}")
                return "\n\n".join(extracted_pages)
            except Exception as e:
                # Fallback decoding if pdf parsing fails
                return file_bytes.decode("utf-8", errors="ignore")
        else:
            # Text, Markdown, or code files
            return file_bytes.decode("utf-8", errors="ignore")

    def recursive_split_text(self, text: str, chunk_size: int = None, chunk_overlap: int = None) -> List[str]:
        """
        Splits text hierarchically by paragraphs, sentences, and words to preserve semantic boundaries.
        """
        c_size = chunk_size or self.chunk_size
        c_overlap = chunk_overlap or self.chunk_overlap
        
        # Clean text
        text = re.sub(r'\r\n', '\n', text)
        paragraphs = text.split('\n\n')
        
        chunks: List[str] = []
        current_chunk = ""

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            # If paragraph itself is larger than chunk size, split by sentences
            if len(para) > c_size:
                sentences = re.split(r'(?<=[.?!])\s+', para)
                for sentence in sentences:
                    sentence = sentence.strip()
                    if not sentence:
                        continue
                    if len(current_chunk) + len(sentence) + 1 <= c_size:
                        current_chunk = f"{current_chunk} {sentence}".strip()
                    else:
                        if current_chunk:
                            chunks.append(current_chunk)
                        # Start next chunk with overlap if possible
                        if len(current_chunk) > c_overlap:
                            overlap_text = current_chunk[-c_overlap:]
                            current_chunk = f"{overlap_text} {sentence}".strip()
                        else:
                            current_chunk = sentence
            else:
                if len(current_chunk) + len(para) + 2 <= c_size:
                    current_chunk = f"{current_chunk}\n\n{para}".strip()
                else:
                    if current_chunk:
                        chunks.append(current_chunk)
                    if len(current_chunk) > c_overlap:
                        overlap_text = current_chunk[-c_overlap:]
                        current_chunk = f"{overlap_text}\n{para}".strip()
                    else:
                        current_chunk = para

        if current_chunk:
            chunks.append(current_chunk)

        # Filter out empty or excessively short chunks
        return [c.strip() for c in chunks if len(c.strip()) > 15]

    def create_chunks(self, text: str, doc_name: str, chunk_size: int = None, chunk_overlap: int = None) -> List[DocumentChunk]:
        raw_chunks = self.recursive_split_text(text, chunk_size, chunk_overlap)
        doc_chunks: List[DocumentChunk] = []

        curr_pos = 0
        for idx, chunk_text in enumerate(raw_chunks):
            start = text.find(chunk_text[:30], curr_pos)
            if start == -1:
                start = curr_pos
            end = start + len(chunk_text)
            curr_pos = max(curr_pos, start)

            doc_chunks.append(
                DocumentChunk(
                    chunk_id=idx + 1,
                    doc_name=doc_name,
                    text=chunk_text,
                    score=0.0,
                    start_char=start,
                    end_char=end
                )
            )
        return doc_chunks

doc_processor = DocumentProcessor()
