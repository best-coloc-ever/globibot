from tornado.websocket import WebSocketHandler

class LoggerWebSocketHandler(WebSocketHandler):

    def initialize(self, module):
        self.module = module

    def check_origin(self, origin):
        return True

    def open(self):
        self.module.debug('WebSocket opened')
        self.module.ws_consumers.add(self)

    def on_close(self):
        self.module.debug('WebSocket closed')
        self.module.ws_consumers.discard(self)
