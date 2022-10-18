import json
import logging
from typing import Callable, Optional, Coroutine

from aiokafka import AIOKafkaConsumer

from common import PayloadMessage

ConsumerCallback = Callable[[PayloadMessage], Coroutine]


class TelegramConsumer:
    def __init__(self, loop):
        self._consumer = AIOKafkaConsumer(
            'results',
            loop=loop,
            bootstrap_servers='localhost:9092',
            enable_auto_commit=True
        )
        self._callback: Optional[ConsumerCallback] = None

    async def run(self):
        await self._consumer.start()
        try:
            while True:
                rec = await self._consumer.getone()
                data = json.loads(rec.value.decode('utf-8'))
                if self._callback is None:
                    logging.warning('consumer has no callback function set')
                    continue
                await self._callback(data)
        finally:
            await self._consumer.stop()

    def set_async_callback(self, callback: ConsumerCallback):
        self._callback = callback
