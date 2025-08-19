import re

def normalize(s: str) -> str:
    s = s.strip()
    s = re.sub(r"\s+", " ", s)
    return s
