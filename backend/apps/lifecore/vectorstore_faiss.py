from __future__ import annotations

import os
from typing import List, Tuple, Dict, Any

import numpy as np

try:
    import faiss  # type: ignore
    _HAVE_FAISS = True
except Exception:
    faiss = None  # type: ignore
    _HAVE_FAISS = False

from django.conf import settings
from apps.lifecore.models import DocumentChunk
from apps.lifecore.embedding import text_to_embedding


INDEX_DIR = os.path.join(getattr(settings, 'BASE_DIR', ''), 'var', 'faiss')


class FaissVectorStore:
    def __init__(self, user_id: int):
        self.user_id = int(user_id)
        self.index_path = os.path.join(INDEX_DIR, f'user_{self.user_id}.index')
        self.meta_path = os.path.join(INDEX_DIR, f'user_{self.user_id}.meta.npy')

    @staticmethod
    def is_available() -> bool:
        return _HAVE_FAISS

    def _ensure_dir(self):
        os.makedirs(INDEX_DIR, exist_ok=True)

    def build(self) -> int:
        """Build or rebuild FAISS index for this user. Returns number of vectors indexed."""
        if not _HAVE_FAISS:
            return 0
        self._ensure_dir()
        chunks: List[DocumentChunk] = list(DocumentChunk.objects.filter(user_id=self.user_id).select_related('document'))
        vectors: List[List[float]] = []
        meta: List[Tuple[int, int]] = []  # (chunk_id, doc_id)
        for ch in chunks:
            emb = ch.embedding or []
            if emb and isinstance(emb, (list, tuple)):
                try:
                    vec = [float(x) for x in emb]
                except Exception:
                    continue
                vectors.append(vec)
                meta.append((int(ch.id), int(ch.document_id)))
        if not vectors:
            # remove old index if exists
            try:
                if os.path.exists(self.index_path):
                    os.remove(self.index_path)
                if os.path.exists(self.meta_path):
                    os.remove(self.meta_path)
            except Exception:
                pass
            return 0
        xb = np.array(vectors, dtype='float32')
        d = xb.shape[1]
        index = faiss.IndexFlatIP(d)
        # Normalize vectors to use cosine similarity via dot product
        faiss.normalize_L2(xb)
        index.add(xb)
        faiss.write_index(index, self.index_path)
        np.save(self.meta_path, np.array(meta, dtype='int64'))
        return xb.shape[0]

    def _load_index(self):
        if not (_HAVE_FAISS and os.path.exists(self.index_path) and os.path.exists(self.meta_path)):
            return None, None
        try:
            index = faiss.read_index(self.index_path)
            meta = np.load(self.meta_path)
            return index, meta
        except Exception:
            return None, None

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        if not query or not _HAVE_FAISS:
            return []
        index, meta = self._load_index()
        if index is None or meta is None:
            # try to build if missing
            n = self.build()
            if n == 0:
                return []
            index, meta = self._load_index()
            if index is None or meta is None:
                return []
        q = np.array([text_to_embedding(query)], dtype='float32')
        faiss.normalize_L2(q)
        D, I = index.search(q, top_k)
        refs: List[Dict[str, Any]] = []
        idxs = I[0]
        for i in idxs:
            if int(i) < 0:
                continue
            try:
                chunk_id, doc_id = map(int, meta[int(i)])
                ch = DocumentChunk.objects.select_related('document').get(id=chunk_id)
                snippet = (ch.text or '')[:300].replace('\n', ' ')
                refs.append({
                    'title': ch.document.title,
                    'source': ch.document.source,
                    'snippet': snippet,
                })
            except Exception:
                continue
        return refs


