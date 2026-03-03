import re
from typing import Tuple, Optional

from app.models.compiled_model import SlotSpec

DEFAULT_PATTERNS = {
    "phone": r"^(\+?\d[\d\s\-()]{7,}\d)$",
    "email": r"^[^@\s]+@[^@\s]+\.[^@\s]+$",
}

# нормализуем номер телефона
def normalize_phone(value: str) -> str:
    v = value.strip()
    plus = v.startswith("+")
    # удаляем всё, кроме цифр.
    digits = re.sub(r"\D", "", v)
    return ("+" if plus else "") + digits


def validate_slot(spec: SlotSpec, user_text: str) -> Tuple[bool, Optional[str]]:
    # текст пустой - невалидно
    text = (user_text or "").strip()
    if not text:
        return False, None

    # тип не указан → считаем text
    slot_type = (spec.type or "text").lower()

    if slot_type == "text":
        return True, text

    pattern = spec.pattern or DEFAULT_PATTERNS.get(slot_type)
    if not pattern:
        return True, text

    # проверяем совпадение с паттерном и нормализуем
    if re.match(pattern, text):
        if slot_type == "phone":
            return True, normalize_phone(text)
        return True, text

    return False, None