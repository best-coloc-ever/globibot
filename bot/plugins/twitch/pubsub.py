from collections import defaultdict

import json
import random
import string
import asyncio
import websockets

def nonce(n = 32):
    return ''.join(
        random.choice(string.ascii_uppercase + string.digits)
        for _ in range(n)
    )

def make_order(order_type, data):
    return dict(
        type = order_type,
        nonce = nonce(),
        data = data
    )

def listen_order(*topics):
    return make_order(
        'LISTEN',
        dict(topics=topics)
    )

def unlisten_order(*topics):
    return make_order(
        'UNLISTEN',
        dict(topics=topics)
    )

class QueueIterator:

    def __init__(self):
        self.queue = asyncio.Queue()
        self.stop_next = False

    async def put(self, item):
        await self.queue.put(item)

    async def stop(self):
        self.stop_next = True
        await self.queue.put('dummy item')

    async def __aiter__(self):
        return self

    async def __anext__(self):
        item = await self.queue.get()
        self.queue.task_done()

        if self.stop_next:
            raise StopAsyncIteration

        return item

class PubSub:

    WS_URL = 'wss://pubsub-edge.twitch.tv'

    class Topics:
        VIDEO_PLAYBACK = lambda name: 'video-playback.{}'.format(name)

    def __init__(self, debug, run_async):
        self.debug = debug
        self.run_async = run_async

        self.orders = asyncio.Queue()
        self.iterators_by_topic = defaultdict(dict)
        self.ws = None
        self.service_started = False

    async def shutdown(self):
        for iterators in self.iterators_by_topic.values():
            for iterator in iterators.values():
                await iterator.stop()

        if self.ws:
            await self.ws.close()

    async def subscribe(self, topic, request_id):
        if not self.iterators_by_topic[topic]:
            order = listen_order(topic)
            await self.issue_order(order)

        iterator = QueueIterator()
        self.iterators_by_topic[topic][request_id] = iterator

        return iterator

    async def unsubscribe(self, topic, request_id):
        try:
            iterator = self.iterators_by_topic[topic][request_id]
            await iterator.stop()
            del self.iterators_by_topic[topic][request_id]
        except KeyError:
            return

        if not self.iterators_by_topic[topic]:
            order = unlisten_order(topic)
            await self.issue_order(order)

    async def issue_order(self, order):
        if not self.service_started:
            self.service_started = True
            self.run_async(self.run_ws())

        await self.orders.put(order)

    async def run_ws(self):
        self.debug('Connecting to PubSub service')

        async with websockets.connect(PubSub.WS_URL) as ws:
            self.ws = ws

            self.run_async(self.send_pings())
            self.run_async(self.process_pubsub_orders())

            while True:
                try:
                    message = await self.ws.recv()
                except:
                    break
                data = json.loads(message)

                await self.on_ws_data(data)

        self.ws = None
        self.service_started = False
        self.debug('Disconnected from PubSub service')

    async def on_ws_data(self, data):
        self.debug('PubSub data received: {}'.format(data))

        if data['type'] == 'MESSAGE':
            message_data = data['data']
            topic = message_data['topic']
            message_content = json.loads(message_data['message'])

            iterators = self.iterators_by_topic[topic]
            for iterator in iterators.values():
                await iterator.put(message_content)

    async def process_pubsub_orders(self):
        while True:
            order = await self.orders.get()
            self.orders.task_done()

            try:
                await self.send_data(order)
            except:
                self.debug('Failed to send order')
                break

    async def send_pings(self):
        ping = dict(type='PING')

        while True:
            try:
                await self.send_data(ping)
            except:
                self.debug('Failed to send ping')
                break

            await asyncio.sleep(60 * 4)

    async def send_data(self, data):
        frame = json.dumps(data)
        self.debug('Sending frame: {}'.format(frame))
        await self.ws.send(frame)
