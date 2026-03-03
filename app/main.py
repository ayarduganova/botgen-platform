from fastapi import FastAPI  # создаёт веб-приложение (API сервер)
from pydantic import BaseModel  # описывает структуры запросов/ответов (валидирует JSON)

from app.compiler.compiler import compile_bot
from app.runtime.engine import run_step
from app.runtime.session import SessionState
from app.runtime.utils import index_nodes
from app.storage.sqlite_store import SQLiteSessionStore

# Создаём объект API-сервера
app = FastAPI(title="BotGen Runtime")

# читает YAML и строит модель бота (граф нод)
compiled_bot = compile_bot("bots/order_bot.yaml")
# делает быстрый индекс, чтобы runtime не искал ноду по списку каждый раз
nodes_index = index_nodes(compiled_bot)
# место, где храним “память” пользователей (сессии)
store = SQLiteSessionStore("botgen.db")


class ChatRequest(BaseModel):
    # id пользователя/чата
    session_id: str
    text: str | None = None


class ChatResponse(BaseModel):
    # что бот ответит
    messages: list[str]
    # новое состояние после обработки
    session: SessionState

# Создаём HTTP endpoint: метод POST;путь /chat
@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    # если сессия уже есть → продолжаем диалог
    session = store.get(req.session_id)
    if session is None:
        # если нет → создаём новую:
        # ставим текущую ноду = start_node (начало flow)
        session = SessionState(session_id=req.session_id, current_node_id=compiled_bot.start_node)

    # Исполнение шага диалога
    result = run_step(compiled_bot, nodes_index, session, req.text)
    # Сохранение обновлённой сессии
    store.save(result["session"])
    # Возврат ответа
    return ChatResponse(messages=result["messages"], session=result["session"])