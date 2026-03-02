from pydantic import BaseModel
from typing import List, Optional, Dict


# BaseModel — базовый класс Pydantic (автоматическая валидация типов + удобная сериализация в JSON).

class SlotSpec(BaseModel):
    type: str = "text"
    pattern: Optional[str] = None
    error_text: Optional[str] = None

# узел графа диалога
class Node(BaseModel):
    id: str
    # тип узла (say; ask; end)
    type: str
    # текст сообщения
    text: Optional[str] = None
    # слот - информация, полученная от пользователя.
    slot: Optional[str] = None
    # ссылка на следующую ноду
    next_node: Optional[str] = None


class CompiledBot(BaseModel):
    # имя бота
    bot: str
    # список всех узлов
    nodes: List[Node]
    # слоты
    slots: Dict[str, SlotSpec] = {}
    # id первого узла
    start_node: str