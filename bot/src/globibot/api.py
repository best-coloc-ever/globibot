from tornado.web import RequestHandler
from tornado.escape import json_encode

from http import HTTPStatus

def extract_attributes(obj, attribute_names):
    attrs = dict()

    for attr_name in attribute_names:
        attrs[attr_name] = getattr(obj, attr_name)

    return attrs

class RequestHandlerWithBotContext(RequestHandler):

    def initialize(self, bot):
        self.bot = bot

class ResourceHandler(RequestHandlerWithBotContext):

    def get(self, *args, **kwargs):
        resource = self.resource(*args, **kwargs)
        if resource is None:
            self.set_status(HTTPStatus.BAD_REQUEST)
        else:
            data = extract_attributes(resource, self.attribute_names)
            self.set_header("Content-Type", 'application/json')
            self.write(json_encode(data))

class ResourceCollectionHandler(RequestHandlerWithBotContext):

    def get(self, *args, **kwargs):
        collection = self.collection(*args, **kwargs)
        if collection is None:
            self.set_status(HTTPStatus.BAD_REQUEST)
        else:
            data = [
                extract_attributes(resource, self.attribute_names)
                for resource in collection
            ]
            self.set_header("Content-Type", 'application/json')
            self.write(json_encode(data))

def make_resource_handler(resource_getter, resource_attr_names):

    class Handler(ResourceHandler):

        def resource(self, *args, **kwargs):
            return resource_getter(self.bot, *args, **kwargs)

        @property
        def attribute_names(_):
            return resource_attr_names

    return Handler

def make_collection_handler(collection_getter, resource_attr_names):

    class Handler(ResourceCollectionHandler):

        def collection(self, *args, **kwargs):
            return collection_getter(self.bot, *args, **kwargs)

        @property
        def attribute_names(_):
            return resource_attr_names

    return Handler

UserHandler = make_resource_handler(
    lambda bot, user_id: bot.find_user(user_id),
    ('id', 'name', 'avatar_url')
)

def get_members(bot, server_id):
    server = bot.find_server(server_id)
    if server:
        return server.members

UsersHandler = make_collection_handler(
    get_members,
    ('id', 'name', 'avatar_url')
)

ServersHandler = make_collection_handler(
    lambda bot: bot.servers,
    ('id', 'name', 'icon_url')
)
