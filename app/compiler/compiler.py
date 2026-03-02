import yaml
import uuid
from app.models.compiled_model import Node, CompiledBot, SlotSpec

def compile_bot(path: str) -> CompiledBot:
    # чтение yaml
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    # получаем slots или {}
    raw_slots = data.get("slots", {}) or {}
    # структурируем модель слотов
    # {
    #   "phone": SlotSpec(type="phone", pattern="regex")
    # }
    slots = {name: SlotSpec(**(spec or {})) for name, spec in raw_slots.items()}

    nodes = []
    # id первой ноды
    start_node = None

    for step in data["flow"]:
        # формируем узел
        node_id = str(uuid.uuid4())

        node = Node(
            id=node_id,
            type=step["type"],
            text=step.get("text"),
            slot=step.get("slot"),
        )

        # добавляем ноду; обозначаем следующую и предыдущую
        if not nodes:
            start_node = node_id
        else:
            nodes[-1].next_node = node_id

        nodes.append(node)

    # выводим сформированного бота
    return CompiledBot(
        bot=data["bot"],
        slots=slots,
        nodes=nodes,
        start_node=start_node,
    )