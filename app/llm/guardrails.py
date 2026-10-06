import re

FALLBACK = ("I don't have verified information about that in Ajanta's current profile. "
            "You can contact Ajanta directly for the most accurate answer.")

RULES = [
    ("HIRE_AJANTA", r"\bhire\b|\bhiring\b|freelanc|available for|work with (you|ajanta)|engage"),
    ("CONTACT", r"contact|email|reach|linkedin|github|phone"),
    ("EDUCATION", r"educat|degree|universit|college|school|study|studied|certif|gpa|workshop|oracle|cisco"),
    ("EXPERIENCE", r"experience|employ|\bwork(ed|ing|s)?\b|\bjobs?\b|career|intern|compan|resume|cv\b|pixis|voguetech|ibex|current role|position"),
    ("PROJECT", r"project|built|build|drone|quadcopter|uav|visioneye|hrmis|case study"),
    ("SKILLS", r"skill|technolog|tech stack|stack|tools?|language|strongest|proficien"),
    ("AI_ENGINEERING", r"\brag\b|embedding|vector|llm|agent|prompt|evaluat|computer vision|deploy|fine-?tun|transformer|retriev"),
    ("PERSONAL_PROFILE", r"who is|about (ajanta|her|you)|tell me about (ajanta|yourself)|introduce|leadership|ambassador|ieee|volunteer|community"),
]
PERSONAL = {"PERSONAL_PROFILE", "PROJECT", "SKILLS", "EXPERIENCE", "EDUCATION", "CONTACT"}


def detect_intent(q: str) -> str:
    q = q.lower()
    ai_pat = dict(RULES)["AI_ENGINEERING"]
    if re.search(ai_pat, q) and not re.search(r"ajanta|\byou(r)?\b|\bher\b|\bshe\b", q):
        return "AI_ENGINEERING"  # general technical question, not about Ajanta
    # Questions about Ajanta's own work stay personal even if they mention technical words
    if re.search(r"ajanta|\byou(r)?\b", q) and re.search(r"project|built|experience|work", q):
        for name in ("PROJECT", "EXPERIENCE"):
            if re.search(dict(RULES)[name], q):
                return name
    for name, pat in RULES:
        if re.search(pat, q):
            return name
    return "UNKNOWN"


def is_personal(intent: str) -> bool:
    return intent in PERSONAL


INJECTION = re.compile(r"ignore (all |previous |the )*(instructions|rules)|system prompt|reveal.*prompt|developer message", re.I)


def looks_like_injection(q: str) -> bool:
    return bool(INJECTION.search(q))


def validate_grounding(answer: str, n_sources: int) -> bool:
    """Personal answers must cite at least one valid [S#] and no unknown ids."""
    ids = [int(x) for x in re.findall(r"\[S(\d+)\]", answer)]
    return bool(ids) and all(1 <= i <= n_sources for i in ids)
