import unittest
from typing import Any

from fake import Fake

from bot.dispatcher import Dispatcher
from bot.long_polling import poll_once
from bot.messenger import Messenger


class PollOnceTest(unittest.TestCase):
    def test_single_update_dispatches_and_advances_offset(self) -> None:
        update: dict[str, Any] = {
            "update_id": 2026,
            "message": {
                "message_id": 1,
                "chat": {"id": 1, "type": "private"},
                "text": "Hello world",
            },
        }
        requested: list[dict[str, object]] = []
        dispatched: list[dict[str, Any]] = []

        def fake_get_updates(**params: object) -> list[dict[str, Any]]:
            requested.append(params)
            return [update]

        messenger: Messenger = Fake({"get_updates": fake_get_updates})
        dispatcher: Dispatcher = Fake({"dispatch": dispatched.append})

        next_offset = poll_once(dispatcher, messenger, offset=0)

        self.assertEqual(
            requested,
            [{"offset": 0, "limit": 10, "timeout": 30, "allowed_updates": ["message"]}],
        )
        self.assertEqual(dispatched, [update])
        self.assertEqual(next_offset, 2027)

    def test_empty_updates_does_not_dispatch(self) -> None:
        dispatched: list[dict[str, Any]] = []
        messenger: Messenger = Fake({"get_updates": lambda **_: []})
        dispatcher: Dispatcher = Fake({"dispatch": dispatched.append})

        next_offset = poll_once(dispatcher, messenger, offset=5)

        self.assertEqual(dispatched, [])
        self.assertEqual(next_offset, 5)

    def test_unordered_update_ids_uses_max_offset(self) -> None:
        update_high = {"update_id": 100, "message": {"text": "first"}}
        update_low = {"update_id": 50, "message": {"text": "second"}}
        dispatched: list[dict[str, Any]] = []
        messenger: Messenger = Fake(
            {"get_updates": lambda **_: [update_high, update_low]}
        )
        dispatcher: Dispatcher = Fake({"dispatch": dispatched.append})

        next_offset = poll_once(dispatcher, messenger, offset=0)

        self.assertEqual(dispatched, [update_high, update_low])
        self.assertEqual(next_offset, 101)
