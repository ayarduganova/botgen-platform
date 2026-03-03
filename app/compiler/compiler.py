import uuid
from typing import Dict, Any, List

import yaml

from app.models.compiled_model import Node, CompiledBot, SlotSpec, RuleSpec


def _new_id() -> str:
    return str(uuid.uuid4())

# компилируем список шагов в ноды (без внеш переходов)
def _compile_steps(steps: List[Dict[str, Any]]) -> List[Node]:
    nodes: List[Node] = []
    for step in steps:
        node = Node(
            id=_new_id(),
            type=step["type"],
            text=step.get("text"),
            slot=step.get("slot"),
            op=step.get("op"),
            value=step.get("value"),
        )
        nodes.append(node)
    # линейные next_node для обычных шагов
    for i in range(len(nodes) - 1):
        if nodes[i].type not in ("condition", "end"):
            nodes[i].next_node = nodes[i + 1].id
    return nodes

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

    # получаем rules или []
    raw_rules = data.get("rules", []) or []
    rules = [RuleSpec(**r) for r in raw_rules]

    # получаем labels
    raw_labels = data.get("labels", {}) or {}

    # компилируем основной flow
    main_nodes = _compile_steps(data["flow"])
    if not main_nodes:
        raise ValueError("flow is empty")

    # компилируем label blocks
    label_nodes_map: Dict[str, List[Node]] = {}
    for label, steps in raw_labels.items():
        # проверка, что есть список
        if not isinstance(steps, list) or not steps:
            raise ValueError(f"labels.{label} must be a non-empty list")
        label_nodes_map[label] = _compile_steps(steps)

    # собираем общий список всех нод
    all_nodes: List[Node] = []
    all_nodes.extend(main_nodes)
    for nodes in label_nodes_map.values():
        all_nodes.extend(nodes)

    # обрабатываем label
    # создаём словарь:
    # ключ: имя label
    # значение: id первой ноды в этом label-блоке
    label_start_id = {label: nodes[0].id for label, nodes in label_nodes_map.items()}

    # проходимся по основным нодам
    for node, step in zip(main_nodes, data["flow"]):
        # обрабатываем ветвление
        if node.type == "condition":
            true_label = step.get("if_true")
            false_label = step.get("if_false")
            if true_label not in label_start_id or false_label not in label_start_id:
                raise ValueError("condition requires if_true/if_false pointing to existing labels")

            node.next_true = label_start_id[true_label]
            node.next_false = label_start_id[false_label]

            # у condition нет next_node (потому что дальше идём по ветвлению)
            node.next_node = None

    # выводим сформированного бота
    return CompiledBot(
        bot=data["bot"],
        slots=slots,
        rules=rules,
        nodes=all_nodes,
        start_node=main_nodes[0].id,
    )