import re
from typing import Iterable, List, Set


def normalize_skills(raw: Iterable[str] | str | None) -> List[str]:
    """
    Convert comma/semicolon separated skills into a unique, lowercase list.
    """
    if raw is None:
        return []

    if isinstance(raw, str):
        tokens = re.split(r"[;,/]", raw)
    else:
        tokens = list(raw)

    cleaned: Set[str] = {token.strip().lower() for token in tokens if token and token.strip()}
    return sorted(cleaned)







