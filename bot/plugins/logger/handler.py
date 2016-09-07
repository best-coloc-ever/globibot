from tornado.web import RequestHandler
from tornado.escape import json_encode

from collections import defaultdict

from . import queries as q

import jwt

JWT_SALT = 'Gl0b1Bo7'

class Cache:

    def __init__(self):
        self.member_caches = defaultdict(dict)

    def member(self, server, user_id):
        try:
            return self.member_caches[server.id][user_id]
        except KeyError:
            member = server.get_member(user_id)
            if member:
                self.member_caches[server.id][user_id] = member
                return member

cache = Cache()

class LogsApiTopHandler(RequestHandler):

    def initialize(self, plugin):
        self.plugin = plugin

    def get(self):
        auth = self.request.headers.get('Authorization')
        if auth:
            token = auth[7:]
            payload = jwt.decode(token, JWT_SALT, algorithms=['HS256'])
            self.plugin.info(payload)
            user = self.plugin.bot.find_user(payload['user'])
            if user:
                server = user.server

                with self.plugin.transaction() as trans:
                    trans.execute(q.most_logs, dict(
                        server_id = server.id,
                        limit     = 200
                    ))

                    results = dict(server_id=server.id, data=[])
                    for r in trans.fetchall():
                        user_id = str(r[0])
                        member = cache.member(server, user_id)
                        if member:
                            results['data'].append(((user_id, member.name), r[1], r[2].timestamp()))

                    self.set_header("Content-Type", 'application/json')
                    self.write(json_encode(results))
        else:
            self.set_status(400)

class LogsApiUserHandler(RequestHandler):

    def initialize(self, plugin):
        self.plugin = plugin

    def get(self, user_id):
        with self.plugin.transaction() as trans:
            content = '''
                select content, stamp from log
                    where   author_id = %(author_id)s
            '''
            trans.execute(content, dict(
                author_id = user_id,
            ))

            self.set_header("Content-Type", 'application/json')
            self.write(json_encode([(r[0], r[1].timestamp()) for r in trans.fetchall()]))
