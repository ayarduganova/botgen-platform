from typing import Dict, Optional
from app.runtime.session import SessionState

# хранилища сессий
class MemorySessionStore:
    def __init__(self) -> None:
        # словарь сессий
        self._data: Dict[str, SessionState] = {}

    # получаем сессию по ключу
    def get(self, session_id: str) -> Optional[SessionState]:
        return self._data.get(session_id)

    # сохраняем сессию
    def save(self, session: SessionState) -> None:
        self._data[session.session_id] = session