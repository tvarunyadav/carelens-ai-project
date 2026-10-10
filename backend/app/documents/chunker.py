import uuid
from typing import List, Dict, Any

from app.retrieval.embedding import MODEL_NAME

class TextChunker:
    @staticmethod
    def chunk_pages(
        patient_id: str,
        document_id: str,
        document_version_id: str,
        pages: List[Dict[str, Any]],
        max_chunk_chars: int = 500,
        embedding_model: str = MODEL_NAME
    ) -> List[Dict[str, Any]]:
        """
        Splits page-level extracted text into bounded chunks while preserving exact page provenance.
        Each chunk is assigned a deterministic UUID, page_number, chunk_index, and metadata.
        """
        chunks: List[Dict[str, Any]] = []
        global_chunk_idx = 0

        for page in pages:
            page_num = page.get("page_number", 1)
            text = (page.get("text") or "").strip()
            if not text:
                continue

            # Split by double newlines or lines
            blocks = [b.strip() for b in text.split("\n\n") if b.strip()]
            if not blocks:
                blocks = [text]

            current_chunk = ""
            for block in blocks:
                if len(current_chunk) + len(block) + 2 <= max_chunk_chars:
                    current_chunk = f"{current_chunk}\n\n{block}".strip()
                else:
                    if current_chunk:
                        chunk_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{document_id}_p{page_num}_c{global_chunk_idx}"))
                        chunks.append({
                            "id": chunk_id,
                            "patient_id": patient_id,
                            "document_id": document_id,
                            "document_version_id": document_version_id,
                            "page_number": page_num,
                            "chunk_index": global_chunk_idx,
                            "chunk_text": current_chunk,
                            "embedding_model": embedding_model,
                            "metadata_json": {
                                "page_number": page_num,
                                "chunk_index": global_chunk_idx
                            }
                        })
                        global_chunk_idx += 1
                    current_chunk = block

            if current_chunk:
                chunk_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{document_id}_p{page_num}_c{global_chunk_idx}"))
                chunks.append({
                    "id": chunk_id,
                    "patient_id": patient_id,
                    "document_id": document_id,
                    "document_version_id": document_version_id,
                    "page_number": page_num,
                    "chunk_index": global_chunk_idx,
                    "chunk_text": current_chunk,
                    "embedding_model": embedding_model,
                    "metadata_json": {
                        "page_number": page_num,
                        "chunk_index": global_chunk_idx
                    }
                })
                global_chunk_idx += 1

        return chunks
