from pydantic import BaseModel
from typing import Dict, Optional


class SessionState(BaseModel):
    # идентификатор диалога/пользователя
    session_id: str
    # где мы сейчас находимся в графе
    current_node_id: str
    # память бота (данные которые дал пользователь)
    slots: Dict[str, str] = {}
    # чего сейчас ждём от пользователя
    awaiting_slot: Optional[str] = None
    # Флаг завершения диалога
    is_finished: bool = False