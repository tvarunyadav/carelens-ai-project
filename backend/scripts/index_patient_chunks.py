import os
import sys
import re
import asyncio
import logging
import httpx
import dotenv

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
dotenv.load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env")))

from app.core.config import settings
from app.documents.extractor import PDFExtractor
from app.documents.chunker import TextChunker
from app.retrieval.embedding import encode_texts_sync, EMBEDDING_DIM, MODEL_NAME

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("index_patient_chunks")

async def run_indexing():
    supabase_url = settings.SUPABASE_URL.rstrip('/')
    service_role_key = getattr(settings, "SUPABASE_SERVICE_ROLE_KEY", "") or settings.SUPABASE_ANON_KEY

    headers = {
        "Authorization": f"Bearer {service_role_key}",
        "apikey": service_role_key,
        "Content-Type": "application/json"
    }

    logger.info("=== Starting Repeatable Patient Document Chunk Indexing & Seed SQL Generation ===")

    documents = []
    seed_paths = [
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "database", "seeds", "003_synthetic_history_seed.sql")),
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "database", "seeds", "003_synthetic_history_seed.sql"))
    ]
    seed_sql_path = next((p for p in seed_paths if os.path.exists(p)), None)
    if seed_sql_path:
        with open(seed_sql_path, "r", encoding="utf-8") as f:
            text = f.read()
        pattern = r"INSERT INTO public\.patient_documents.*?\nVALUES\s*\('([^']+)',\s*'([^']+)',\s*'([^']+)',\s*'([^']+)',\s*'([^']+)',\s*'([^']+)',\s*'([^']+)'"
        matches = re.findall(pattern, text)
        for m in matches:
            documents.append({
                "id": m[0],
                "patient_id": m[1],
                "title": m[2],
                "doc_type": m[3],
                "clinical_date": m[4],
                "status": m[5],
                "storage_path": m[6]
            })

    logger.info(f"Loaded {len(documents)} patient documents from seed SQL.")

    all_chunks = []
    for doc in documents:
        if doc.get("status") == "pending" or not doc.get("storage_path") or doc.get("storage_path") == "NULL":
            continue

        filename = os.path.basename(doc["storage_path"])
        filepath = os.path.join("backend", "storage", "patient_documents", filename)
        if not os.path.exists(filepath):
            filepath = os.path.join("storage", "patient_documents", filename)

        if not os.path.exists(filepath):
            logger.warning(f"File not found on storage: {filepath}")
            continue

        extraction = PDFExtractor.extract_text_and_provenance(filepath)
        if extraction["status"] != "processed" or not extraction["pages"]:
            continue

        chunks = TextChunker.chunk_pages(
            patient_id=doc["patient_id"],
            document_id=doc["id"],
            document_version_id=doc["id"], # Will resolve dynamically in SQL
            pages=extraction["pages"]
        )
        all_chunks.extend(chunks)

    if not all_chunks:
        logger.info("No chunks generated.")
        return

    texts = [c["chunk_text"] for c in all_chunks]
    logger.info(f"Computing embeddings for {len(texts)} chunks using {MODEL_NAME}...")
    vectors = await asyncio.to_thread(encode_texts_sync, texts)

    sql_statements = [
        "-- Seed 004: Synthetic Patient Document Vector Chunks & Embeddings (384-dim BAAI/bge-small-en-v1.5)",
        "-- Executed SIXTH in Supabase SQL Editor\n",
        "BEGIN;\n"
    ]

    for c, vec in zip(all_chunks, vectors):
        vec_str = "[" + ",".join(str(round(v, 6)) for v in vec) + "]"
        escaped_text = c["chunk_text"].replace("'", "''")
        
        sql = f"""INSERT INTO public.patient_document_chunks (id, patient_id, document_id, document_version_id, chunk_index, chunk_text, embedding, page_number)
VALUES (
    '{c['id']}',
    '{c['patient_id']}',
    '{c['document_id']}',
    COALESCE((SELECT id FROM public.patient_document_versions WHERE document_id = '{c['document_id']}' AND version_number = 1 LIMIT 1), '{c['document_id']}'),
    {c['chunk_index']},
    '{escaped_text}',
    '{vec_str}'::vector,
    {c['page_number']}
)
ON CONFLICT (id) DO NOTHING;"""
        sql_statements.append(sql)

    sql_statements.append("\nCOMMIT;\n")

    chunks_seed_path = "database/seeds/004_patient_vector_chunks_seed.sql"
    with open(chunks_seed_path, "w", encoding="utf-8") as f:
        f.write("\n".join(sql_statements))

    logger.info(f"SUCCESS: Generated vector chunks seed file at '{chunks_seed_path}' ({len(all_chunks)} chunks processed).")

if __name__ == "__main__":
    asyncio.run(run_indexing())
