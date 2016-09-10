from http import HTTPStatus
from functools import wraps

from tornado.escape import json_encode

def authenticated(method):

    @wraps(method)
    def call(self, *args, **kwargs):
        if self.current_user is None:
            self.set_status(HTTPStatus.FORBIDDEN)
        else:
            return method(self, *args, **kwargs)

    return call

def respond_json(method):

    @wraps(method)
    def call(self, *args, **kwargs):
        data = method(self, *args, **kwargs)

        if data:
            self.set_header('Content-Type', 'application/json')
            self.write(json_encode(data))

    return call
