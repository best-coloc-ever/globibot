from tornado.web import MissingArgumentError
from tornado.escape import json_encode

from http import HTTPStatus
from functools import wraps

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

def respond_json_async(method):

    @wraps(method)
    async def call(self, *args, **kwargs):
        future = method(self, *args, **kwargs)

        if future:
            data = await future

            if data:
                self.set_header('Content-Type', 'application/json')
                self.write(json_encode(data))

    return call

def with_query_parameters(*parameter_names):

    def wrapped(method):

        @wraps(method)
        def call(self, *args, **kwargs):
            try:
                for param in parameter_names:
                    kwargs[param] = self.get_query_argument(param)

                return method(self, *args, **kwargs)
            except MissingArgumentError:
                self.set_status(HTTPStatus.BAD_REQUEST)

        return call

    return wrapped

def with_body_arguments(*parameter_names):

    def wrapped(method):

        @wraps(method)
        def call(self, *args, **kwargs):
            try:
                for param in parameter_names:
                    kwargs[param] = self.get_body_argument(param)

                return method(self, *args, **kwargs)
            except MissingArgumentError:
                self.set_status(HTTPStatus.BAD_REQUEST)

        return call

    return wrapped

import asyncio

def async_handler(fn):

    async def wrapped(*args, **kwargs):
        loop = asyncio.get_event_loop()
        return loop.create_task(fn(*args, **kwargs))

    return wrapped
