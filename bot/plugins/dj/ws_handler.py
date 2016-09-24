from tornado.websocket import WebSocketHandler

from globibot.lib.web import constants as c

class VoiceWebSocketHandler(WebSocketHandler):

    def initialize(self, plugin, bot):
        self.plugin = plugin
        self.bot = bot

    def get_current_user(self):
        cookie = self.get_secure_cookie(c.USER_COOKIE_NAME)

        if cookie:
            user_id = cookie.decode('ascii')
            return self.plugin.bot.find_user(user_id)

    def check_origin(self, origin):
        return True

    def open(self):
        user = self.current_user
        if user is None:
            self.close()
        else:
            self.plugin.debug('Voice WebSocket opened for: {}'.format(user))
            for server in self.plugin.bot.servers_of(user):
                self.plugin.ws_consumers[server.id].add(self)
                queue_data = self.plugin.server_queue_data(server)
                self.write_message(queue_data)

    def on_message(self, message):
        self.ping(b'PONG')

    def on_close(self):
        user = self.current_user
        self.plugin.debug('Voice WebSocket closed for: {}'.format(user))
        for server in self.plugin.bot.servers_of(user):
            self.plugin.ws_consumers[server.id].discard(self)
