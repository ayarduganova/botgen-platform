import re
from typing import Dict

# выражение для вида {slot}
_PLACEHOLDER_RE = re.compile(r"\{([a-zA-Z_][a-zA-Z0-9_]*)\}")

# Заменяет {slot} на значение из slots.
# Если слота нет — оставляет как есть.
def render_template(text: str, slots: Dict[str, str]) -> str:
    if not text:
        return text

    def repl(m: re.Match) -> str:
        key = m.group(1)
        return str(slots.get(key, m.group(0)))

    return _PLACEHOLDER_RE.sub(repl, text)