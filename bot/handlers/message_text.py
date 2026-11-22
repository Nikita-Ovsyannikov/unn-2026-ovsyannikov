from typing import Any, override

from bot.handlers.handler import Handler, HandlerStatus
from bot.messenger import Messenger


class MessageTextHandler(Handler):
    @override
    def can_handle(self, update: dict[str, Any]) -> bool:
        message = update.get("message")
        return isinstance(message, dict) and isinstance(message.get("text"), str)

    @override
    def handle(self, update: dict[str, Any], messenger: Messenger) -> HandlerStatus:
        message = update["message"]
        messenger.send_message(
            chat_id=message["chat"]["id"],
            text=message["text"],
        )
        return HandlerStatus.STOP
