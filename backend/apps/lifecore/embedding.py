from __future__ import annotations
from typing import List
import hashlib
import math
from django.conf import settings
import openai

try:
    _OPENAI_CLIENT = None
    if settings.OPENAI_API_KEY:
        _OPENAI_CLIENT = openai.Client(api_key=settings.OPENAI_API_KEY)
except Exception:
    pass

def _tokenize(text: str) -> List[str]:
    return [t.lower() for t in (text or '').split() if t.strip()]


def text_to_embedding(text: str, dim: int = 1536) -> List[float]:
    """
    Generates embedding for text.
    Tries to use OpenAI if available, otherwise falls back to MD5 hashing (legacy).
    """
    if not text:
        return [0.0] * dim

    # Try OpenAI first
    global _OPENAI_CLIENT
    if _OPENAI_CLIENT:
        try:
            # Replace newlines for best results
            text = text.replace("\n", " ")
            resp = _OPENAI_CLIENT.embeddings.create(input=[text], model="text-embedding-3-small")
            return resp.data[0].embedding
        except Exception as e:
            print(f"OpenAI embedding failed: {e}")
            # Fallback below
            pass
    
    # Fallback to MD5 hashing (Legacy) - adjusted for requested dim if possible
    # Note: MD5 hashing into 1536 dimensions is just as random/bad semantically as 256.
    vec = [0.0] * dim
    tokens = _tokenize(text)
    if not tokens:
        return vec
    for tok in tokens:
        h = int(hashlib.md5(tok.encode('utf-8')).hexdigest(), 16)
        idx = h % dim
        vec[idx] += 1.0
    # l2 normalize
    norm = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [v / norm for v in vec]


def cosine_similarity(a: List[float], b: List[float]) -> float:
    if not a or not b:
        return 0.0
    n = min(len(a), len(b))
    num = sum(a[i] * b[i] for i in range(n))
    # a and b are normalized in text_to_embedding
    return float(num)


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    if not text:
        return []
    text = text.strip()
    chunks: List[str] = []
    start = 0
    N = len(text)
    while start < N:
        end = min(N, start + chunk_size)
        chunks.append(text[start:end])
        if end >= N:
            break
        start = end - overlap
        if start < 0:
            start = 0
    return chunks
