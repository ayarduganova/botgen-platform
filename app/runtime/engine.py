from typing import List, Dict, Optional
from app.models.compiled_model import CompiledBot, Node
from app.runtime.session import SessionState
from app.runtime.validators import validate_slot
from app.runtime.rules import match_rule, apply_rule

# словарь
class EngineResponse(dict):
    pass


def run_step(
    bot: CompiledBot,
    # индекс {node_id -> Node} для быстрого доступа
    nodes: Dict[str, Node],
    # текущее состояние пользователя
    session: SessionState,
    # сообщение пользователя
    user_text: Optional[str],
) -> EngineResponse:
    messages: List[str] = []

    # обработка правил
    # проверяем правило ли
    rule = match_rule(bot, user_text)
    if rule is not None:
        # применяем его
        rule_msgs = apply_rule(bot, session, rule)

        # если это restart — сразу продолжаем диалог с начала
        if (rule.action or "").lower() == "restart":
            cont = run_step(bot, nodes, session, None)
            # склеиваем сообщения: "начинаем заново" + приветствие/вопрос
            return EngineResponse(
                messages=rule_msgs + cont["messages"],
                session=cont["session"],
            )
        # если не restart - выводим сообщение бота
        return EngineResponse(messages=rule_msgs, session=session)

    if session.is_finished:
        return EngineResponse(messages=["Диалог уже завершён."], session=session)

    # Если мы ждём ответ для слота — валидируем и сохраняем
    if session.awaiting_slot:
        # например phone;name
        slot_name = session.awaiting_slot
        # SlotSpec из compiled model, где лежат: тип;pattern(regex);error_text
        spec = bot.slots.get(slot_name)

        if user_text is None:
            return EngineResponse(messages=["Пожалуйста, введите значение."], session=session)

        # если слот не описан (spec is None) → принимаем любой текст
        # если описан → проверяем через validate_slot
        if spec is None:
            ok, normalized = True, user_text.strip()
        else:
            ok, normalized = validate_slot(spec, user_text)

        # Если ввод невалидный
        if not ok:
            err = spec.error_text if spec and spec.error_text else "Неверный формат. Попробуйте ещё раз."
            return EngineResponse(messages=[err], session=session)

        # Если ввод валидный — сохраняем слот и снимаем режим ожидания
        session.slots[slot_name] = normalized if normalized is not None else user_text.strip()
        session.awaiting_slot = None

        # переходим к следующей ноде после ask
        cur = nodes[session.current_node_id]
        if cur.next_node:
            session.current_node_id = cur.next_node

    # Исполняем ноды до первой ask или end
    while True:
        node = nodes[session.current_node_id]

        if node.type == "say":
            # если есть текст → добавляем в messages
            if node.text:
                messages.append(node.text)
            # если есть next_node → двигаемся дальше и продолжаем цикл
            if node.next_node:
                session.current_node_id = node.next_node
                continue
            # если next_node нет → считаем, что диалог закончился
            session.is_finished = True
            break

        if node.type == "ask":
            # если есть текст → добавляем в messages наш вопрос
            if node.text:
                messages.append(node.text)
            # ожидаем ответ
            session.awaiting_slot = node.slot
            break

        if node.type == "end":
            session.is_finished = True
            messages.append("✅ Диалог завершён.")
            break

        messages.append(f"⚠️ Неизвестная нода: {node.type}")
        session.is_finished = True
        break

    return EngineResponse(messages=messages, session=session)