import re
from typing import Optional

from app.models.compiled_model import CompiledBot, RuleSpec
from app.runtime.session import SessionState
from app.runtime.templating import render_template


# проверка на правило
def match_rule(bot: CompiledBot, text: Optional[str]) -> Optional[RuleSpec]:
    # обработка пустого текста
    if text is None:
        return None

    t = text.strip()
    if not t:
        return None

    # проверка на правило
    for rule in bot.rules:
        if re.match(rule.pattern, t, flags=re.IGNORECASE):
            return rule
    return None

# применяем правило
def apply_rule(bot: CompiledBot, session: SessionState, rule: RuleSpec) -> list[str]:
    # получаем сообщение бота
    messages = [render_template(rule.response, session.slots)]
    # получаем действие
    action = (rule.action or "none").lower()

    # заканчиваем
    if action == "end":
        session.is_finished = True
        session.awaiting_slot = None

    # перезапуск бота
    elif action == "restart":
        session.is_finished = False
        session.awaiting_slot = None
        session.slots = {}
        session.current_node_id = bot.start_node

    # action == "none" -> ничего не меняем

    return messages