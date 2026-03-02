from pydantic import BaseModel
from typing import List, Optional, Dict

# класс для слотов
class SlotSpec(BaseModel):
    # тип
    type: str = "text"
    # паттерн
    pattern: Optional[str] = None
    # сообщение при ошибке валидации
    error_text: Optional[str] = None

# класс для правил (stop/help)
class RuleSpec(BaseModel):
    # название
    name: str
    # паттерн
    pattern: str
    # ответ бота на это правило
    response: str
    # действие
    action: str = "none"  # none | end | restart

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
    # правила
    rules: List[RuleSpec] = []
    # id первого узла
    start_node: str