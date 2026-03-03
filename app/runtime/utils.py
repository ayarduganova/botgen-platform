from typing import Dict

from app.models.compiled_model import CompiledBot, Node


# список нод в словарь
def index_nodes(bot: CompiledBot) -> Dict[str, Node]:
    return {n.id: n for n in bot.nodes}