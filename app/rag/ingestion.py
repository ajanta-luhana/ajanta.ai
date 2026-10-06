import json
from dataclasses import dataclass, field
from pathlib import Path

from app.rag.chunking import split_markdown


@dataclass
class Chunk:
    id: str
    text: str
    source: str       # file name, e.g. education.md
    category: str     # personal | projects | technical
    title: str
    section: str
    url: str = ""
    meta: dict = field(default_factory=dict)


def load_chunks(knowledge_dir: str) -> list[Chunk]:
    root = Path(knowledge_dir)
    meta_file = root / "metadata" / "sources.json"
    meta = json.loads(meta_file.read_text()) if meta_file.exists() else {}
    chunks: list[Chunk] = []
    for path in sorted(root.glob("*/*.md")):
        category = path.parent.name
        info = meta.get(path.name, {})
        title = info.get("title") or path.stem.replace("_", " ").title()
        for i, (section, body) in enumerate(split_markdown(path.read_text(encoding="utf-8"))):
            chunks.append(Chunk(
                id=f"{path.stem}-{i}", text=body, source=path.name, category=category,
                title=title, section=section, url=info.get("url", ""),
                meta={"updated": info.get("updated", "")},
            ))
    return chunks
