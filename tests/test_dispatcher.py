import unittest
from typing import Any, override

from fake import Fake

from bot.dispatcher import Dispatcher
from bot.handlers.handler import Handler, HandlerStatus
from bot.handlers.message_text import MessageTextHandler
from bot.messenger import Messenger


class RecordingHandler(Handler):
    def __init__(
        self,
        name: str,
        can_handle: bool,
        status: HandlerStatus,
        calls: list[str],
    ) -> None:
        self._name = name
        self._can_handle = can_handle
        self._status = status
        self._calls = calls

    @override
    def can_handle(self, update: dict[str, Any]) -> bool:
        del update
        return self._can_handle

    @override
    def handle(self, update: dict[str, Any], messenger: Messenger) -> HandlerStatus:
        del update, messenger
        self._calls.append(self._name)
        return self._status


class DispatcherRoutingTest(unittest.TestCase):
    def setUp(self) -> None:
        self.sent_messages: list[dict[str, object]] = []

        def fake_send_message(**params: object) -> None:
            self.sent_messages.append(params)

        messenger: Messenger = Fake({"send_message": fake_send_message})
        self.dispatcher = Dispatcher(messenger)
        self.dispatcher.add_handlers(MessageTextHandler())

    def test_text_message_is_echoed(self) -> None:
        update = {"update_id": 1, "message": {"chat": {"id": 42}, "text": "Hello"}}

        self.dispatcher.dispatch(update)

        self.assertEqual(self.sent_messages, [{"chat_id": 42, "text": "Hello"}])

    def test_non_text_updates_are_ignored(self) -> None:
        updates: list[dict[str, Any]] = [
            {"update_id": 1, "message": {"chat": {"id": 42}, "photo": []}},
            {
                "update_id": 2,
                "message": {"chat": {"id": 42}, "sticker": {"file_id": "abc"}},
            },
            {"update_id": 3},
        ]

        for update in updates:
            self.dispatcher.dispatch(update)

        self.assertEqual(self.sent_messages, [])


class DispatcherChainTest(unittest.TestCase):
    def _dispatch(self, first: RecordingHandler, second: RecordingHandler) -> None:
        dispatcher = Dispatcher(Fake({}))
        dispatcher.add_handlers(first, second)
        dispatcher.dispatch({"update_id": 1})

    def test_stop_breaks_chain(self) -> None:
        calls: list[str] = []
        self._dispatch(
            RecordingHandler(
                name="first",
                can_handle=True,
                status=HandlerStatus.STOP,
                calls=calls,
            ),
            RecordingHandler(
                name="second",
                can_handle=True,
                status=HandlerStatus.STOP,
                calls=calls,
            ),
        )

        self.assertEqual(calls, ["first"])

    def test_continue_passes_to_next_handler(self) -> None:
        calls: list[str] = []
        self._dispatch(
            RecordingHandler(
                name="first",
                can_handle=True,
                status=HandlerStatus.CONTINUE,
                calls=calls,
            ),
            RecordingHandler(
                name="second",
                can_handle=True,
                status=HandlerStatus.STOP,
                calls=calls,
            ),
        )

        self.assertEqual(calls, ["first", "second"])

    def test_handler_that_cannot_handle_is_skipped(self) -> None:
        calls: list[str] = []
        self._dispatch(
            RecordingHandler(
                name="first",
                can_handle=False,
                status=HandlerStatus.STOP,
                calls=calls,
            ),
            RecordingHandler(
                name="second",
                can_handle=True,
                status=HandlerStatus.STOP,
                calls=calls,
            ),
        )

        self.assertEqual(calls, ["second"])
