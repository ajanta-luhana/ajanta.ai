import re

PLACEHOLDER = re.compile(r"TODO", re.I)


def clean(text: str) -> str:
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    lines = [l.rstrip() for l in text.splitlines() if not PLACEHOLDER.search(l)]
    return re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()


def split_markdown(text: str, max_chars: int = 900) -> list[tuple[str, str]]:
    """Split by heading, then by paragraph. Returns (section, body). Drops empty/placeholder-only sections."""
    out, section, buf = [], "Overview", []

    def flush():
        body = "\n".join(buf).strip()
        if len(body) < 20:
            return
        para, cur = body.split("\n\n"), ""
        for p in para:
            if cur and len(cur) + len(p) > max_chars:
                out.append((section, cur.strip()))
                cur = ""
            cur += p + "\n\n"
        if cur.strip():
            out.append((section, cur.strip()))

    for line in clean(text).splitlines():
        m = re.match(r"^#{1,3}\s+(.*)", line)
        if m:
            flush()
            buf, section = [], m.group(1).strip()
        else:
            buf.append(line)
    flush()
    return out
