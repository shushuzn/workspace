"""
Vector store module - semantic search using embeddings.
"""

import json
import numpy as np
from pathlib import Path
from typing import Optional

try:
    from sentence_transformers import SentenceTransformer

    HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    HAS_SENTENCE_TRANSFORMERS = False


class VectorStore:
    """
    Vector storage for semantic memory search.
    Uses numpy for lightweight vector operations.
    """

    def __init__(
        self,
        storage_path: Path,
        model_name: str = "all-MiniLM-L6-v2",
    ):
        self._storage_path = Path(storage_path)
        self._vectors_path = self._storage_path.parent / "vectors.json"
        self._index_path = self._storage_path.parent / "vector_index.json"

        self._vectors: dict[str, list[float]] = {}
        self._model_name = model_name
        self._model = None

        self._load_vectors()

    def _get_model(self):
        if self._model is None and HAS_SENTENCE_TRANSFORMERS:
            try:
                self._model = SentenceTransformer(self._model_name)
            except Exception:
                pass
        return self._model

    def _load_vectors(self) -> None:
        if self._vectors_path.exists():
            try:
                with open(self._vectors_path, "r", encoding="utf-8") as f:
                    self._vectors = json.load(f)
            except (json.JSONDecodeError, IOError):
                self._vectors = {}

    def save_vectors(self) -> None:
        self._vectors_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self._vectors_path, "w", encoding="utf-8") as f:
            json.dump(self._vectors, f, ensure_ascii=False)

    def add(self, key: str, text: str) -> None:
        model = self._get_model()
        if model is None:
            return

        try:
            embedding = model.encode(text).tolist()
            self._vectors[key] = embedding
        except Exception:
            pass

    def remove(self, key: str) -> bool:
        if key in self._vectors:
            del self._vectors[key]
            return True
        return False

    def search(self, query: str, texts: dict[str, str], top_k: int = 5) -> list[dict]:
        model = self._get_model()
        if model is None or not self._vectors:
            return []

        try:
            query_embedding = model.encode(query)
        except Exception:
            return []

        results = []
        for key, embedding in self._vectors.items():
            if key not in texts:
                continue

            text_embedding = np.array(embedding)
            similarity = float(
                np.dot(query_embedding, text_embedding)
                / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(text_embedding)
                    + 1e-8
                )
            )

            results.append(
                {
                    "key": key,
                    "value": texts[key],
                    "score": similarity,
                }
            )

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

    def clear(self) -> None:
        self._vectors.clear()

    def size(self) -> int:
        return len(self._vectors)
