import json

from app.models import database as db
from app.models.schemas import HireRequest
from app.rag.retriever import Retriever, tokens


def match(req: HireRequest, retriever: Retriever) -> dict:
    """Match requested skills/scope against verified skill and project chunks only."""
    wanted = set(tokens(" ".join(req.skills) + " " + req.scope + " " + req.role_type))
    projects, skills_hit = [], set()
    for c in retriever.chunks:
        if c.category not in ("projects", "personal"):
            continue
        overlap = wanted & set(tokens(c.text))
        if not overlap:
            continue
        if c.category == "projects":
            projects.append({"title": c.title, "section": c.section, "matched": sorted(overlap)[:6], "n": len(overlap)})
        elif c.source == "skills.md":
            skills_hit |= overlap
    projects = sorted(projects, key=lambda p: -p["n"])[:3]
    if projects or skills_hit:
        summary = (f"Verified overlap found: {len(skills_hit)} skill keyword(s) and {len(projects)} related project(s). "
                   "See the projects below, then contact Ajanta to confirm scope and availability.")
    else:
        summary = ("No verified overlap found in the current profile for these requirements. "
                   "Ajanta can tell you directly whether this is a fit.")
    return {"summary": summary, "projects": projects}


def save(req: HireRequest) -> int:
    return db.execute("INSERT INTO hire_requests(ts,role_type,scope,skills,name,email) VALUES(?,?,?,?,?,?)",
                      (db.now(), req.role_type, req.scope, json.dumps(req.skills), req.name, req.email))
