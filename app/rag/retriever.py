import math
import re
from collections import Counter

from app.rag.ingestion import Chunk, load_chunks

STOP = set("""where when did before previously currently ever i my we us a an the is are was were be been of to in on for with and or but what who how which
about tell me you your do does did can could would should it its this that these those at by from as
ajanta luhana ajanta's has have had any some please
technology technologies use used using skill skills project projects built build experience work worked
education educational background strongest area areas contact reach software her she""".split())

# Which source files best answer each intent
PREFERRED = {
    "PERSONAL_PROFILE": ["about_me.md"], "EDUCATION": ["education.md"],
    "EXPERIENCE": ["experience.md", "resume.md"], "SKILLS": ["skills.md"],
    "CONTACT": ["contact.md"], "PROJECT": [],
}
CATEGORY_FILTER = {"AI_ENGINEERING": "technical", "PROJECT": "projects"}


def tokens(text: str) -> list[str]:
    out = []
    for w in re.findall(r"[a-z0-9\+#\.]+", text.lower().replace("'s", "")):
        w = w.strip(".")
        if not w or w in STOP:
            continue
        if w.endswith("s") and len(w) > 4:
            w = w[:-1]
        if len(w) > 6:  # crude prefix stem so education/educational, retrieval/retrieve match
            w = w[:5]
        out.append(w)
    return out


class Retriever:
    """BM25 over chunks with intent-aware filtering/boosting.
    The interface (search -> [(chunk, relevance)]) is what a pgvector/Chroma retriever must also satisfy."""

    def __init__(self, knowledge_dir: str):
        self.knowledge_dir = knowledge_dir
        self.reindex()

    def reindex(self) -> int:
        self.chunks: list[Chunk] = load_chunks(self.knowledge_dir)
        self.docs = [Counter(tokens(f"{c.title} {c.section} {c.text}")) for c in self.chunks]
        self.avg = (sum(sum(d.values()) for d in self.docs) / len(self.docs)) if self.docs else 1
        df = Counter(t for d in self.docs for t in d)
        n = len(self.docs)
        self.idf = {t: math.log(1 + (n - f + 0.5) / (f + 0.5)) for t, f in df.items()}
        return len(self.chunks)

    def doc_count(self) -> int:
        return len({c.source for c in self.chunks})

    def get(self, chunk_id: str) -> Chunk | None:
        return next((c for c in self.chunks if c.id == chunk_id), None)

    def search(self, query: str, intent: str, k: int = 4) -> list[tuple[Chunk, float]]:
        q = tokens(query)
        cat = CATEGORY_FILTER.get(intent)
        pref = PREFERRED.get(intent, [])
        pool = [i for i, c in enumerate(self.chunks)
                if (cat is None or c.category == cat) and (intent == "AI_ENGINEERING" or c.category != "technical")
                and (not pref or c.source in pref)]
        if not q:  # e.g. "Who is Ajanta Luhana?" -> serve the preferred documents directly
            seen, hits = set(), []
            for i in pool:  # preferred docs: their sections in order; projects: first chunk of each so every project is listed
                if pref or self.chunks[i].source not in seen:
                    seen.add(self.chunks[i].source)
                    hits.append((self.chunks[i], 0.5))
            return hits[:k]
        scored = []
        for i in pool:
            d, length, s = self.docs[i], sum(self.docs[i].values()), 0.0
            for t in set(q):
                if t in d:
                    f = d[t]
                    s += self.idf[t] * f * 2.2 / (f + 1.2 * (0.25 + 0.75 * length / self.avg))
            matched = sum(1 for t in set(q) if t in d) / len(set(q))
            if self.chunks[i].source in pref:
                matched = min(1.0, matched + 0.2)
                s *= 1.3
            if s > 0:
                scored.append((s, matched, i))
        scored.sort(reverse=True)
        return [(self.chunks[i], round(m, 2)) for _, m, i in scored[:k]]
