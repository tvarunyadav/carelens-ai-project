import asyncio
import logging
from typing import List, Optional
from fastembed import TextEmbedding

logger = logging.getLogger(__name__)

EMBEDDING_DIM = 384
MODEL_NAME = "BAAI/bge-small-en-v1.5"
_fastembed_instance: Optional[TextEmbedding] = None

def get_embedding_model() -> TextEmbedding:
    global _fastembed_instance
    if _fastembed_instance is None:
        logger.info(f"Loading FastEmbed ONNX semantic model: {MODEL_NAME}")
        try:
            _fastembed_instance = TextEmbedding(model_name=MODEL_NAME)
        except Exception as exc:
            logger.error(f"Failed to load semantic embedding model {MODEL_NAME}: {exc}")
            raise RuntimeError(f"Semantic embedding model initialization failed for {MODEL_NAME}: {exc}") from exc
    return _fastembed_instance

def encode_text_sync(text: str) -> List[float]:
    model = get_embedding_model()
    # model.embed returns a generator of numpy arrays
    vecs = list(model.embed([text]))
    return vecs[0].tolist()

def encode_texts_sync(texts: List[str]) -> List[List[float]]:
    if not texts:
        return []
    model = get_embedding_model()
    vecs = list(model.embed(texts))
    return [v.tolist() for v in vecs]

async def generate_embedding(text: str) -> List[float]:
    """
    Generates a normalized 384-dimensional semantic embedding vector using FastEmbed (ONNX Runtime),
    offloading CPU computation to a thread pool.
    """
    return await asyncio.to_thread(encode_text_sync, text)

async def generate_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Generates normalized 384-dimensional semantic embedding vectors for a batch of texts using FastEmbed.
    """
    return await asyncio.to_thread(encode_texts_sync, texts)
