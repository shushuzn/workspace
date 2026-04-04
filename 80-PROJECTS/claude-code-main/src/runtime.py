from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass
from typing import Sequence

from .commands import PORTED_COMMANDS
from .tools import PORTED_TOOLS
from .models import PortingModule


@dataclass(frozen=True)
class RoutedMatch:
    kind: str
    name: str
    source_hint: str
    score: float


class BM25:
    """Lightweight BM25 ranker for PortingModule fields."""

    def __init__(self, modules: Sequence[PortingModule], k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        # Combine name + source_hint + responsibility as the document text
        self.documents: list[str] = [
            f"{m.name} {m.source_hint} {m.responsibility}".lower() for m in modules
        ]
        self.module_refs: list[PortingModule] = list(modules)
        self.avgdl = sum(len(d.split()) for d in self.documents) / max(len(self.documents), 1)
        self.idf: dict[str, float] = self._compute_idf()
        self.doc_term_freqs: list[Counter[str]] = [Counter(d.split()) for d in self.documents]

    def _compute_idf(self) -> dict[str, float]:
        df: Counter[str] = Counter()
        for doc in self.documents:
            for term in set(doc.split()):
                df[term] += 1
        N = len(self.documents)
        idf = {}
        for term, df_t in df.items():
            # BM25 IDF formula (with smoothing to avoid -inf for unseen terms)
            idf[term] = math.log((N - df_t + 0.5) / (df_t + 0.5) + 1)
        return idf

    def score(self, query_tokens: list[str], doc_index: int) -> float:
        doc_len = len(self.documents[doc_index].split())
        tf = self.doc_term_freqs[doc_index]
        score = 0.0
        for token in query_tokens:
            if token not in self.idf:
                continue
            tf_t = tf.get(token, 0)
            idf_t = self.idf[token]
            numerator = idf_t * tf_t * (self.k1 + 1)
            denominator = tf_t + self.k1 * (1 - self.b + self.b * doc_len / max(self.avgdl, 1))
            score += numerator / denominator if denominator else 0
        return score


class PortRuntime:
    # Class-level BM25 instances (lazily initialized per kind)
    _bm25_command: BM25 | None = None
    _bm25_tool: BM25 | None = None

    def route_prompt(self, prompt: str, limit: int = 5) -> list[RoutedMatch]:
        query_tokens = [t.lower() for t in prompt.replace('/', ' ').replace('-', ' ').split() if t]

        # Build BM25 rankers lazily
        if PortRuntime._bm25_command is None:
            PortRuntime._bm25_command = BM25(PORTED_COMMANDS)
        if PortRuntime._bm25_tool is None:
            PortRuntime._bm25_tool = BM25(PORTED_TOOLS)

        command_matches = self._bm25_score(query_tokens, PORTED_COMMANDS, PortRuntime._bm25_command, 'command')
        tool_matches = self._bm25_score(query_tokens, PORTED_TOOLS, PortRuntime._bm25_tool, 'tool')

        # Prefer at least one representative from each kind when available
        selected: list[RoutedMatch] = []
        for matches in [command_matches, tool_matches]:
            if matches:
                selected.append(matches[0])

        leftovers = sorted(
            [m for matches in [command_matches, tool_matches] for m in matches],
            key=lambda item: (-item.score, item.kind, item.name),
        )
        selected.extend(leftovers[: max(0, limit - len(selected))])
        return selected[:limit]

    def _bm25_score(
        self, query_tokens: list[str], modules: tuple[PortingModule, ...], bm25: BM25, kind: str
    ) -> list[RoutedMatch]:
        matches: list[RoutedMatch] = []
        for i, module in enumerate(modules):
            s = bm25.score(query_tokens, i)
            if s > 0:
                matches.append(RoutedMatch(kind=kind, name=module.name, source_hint=module.source_hint, score=s))
        matches.sort(key=lambda item: (-item.score, item.name))
        return matches
