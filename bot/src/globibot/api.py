from tornado.web import RequestHandler, MissingArgumentError
from tornado.escape import json_encode

from utils.logging import logger

from .lib.transaction import Transaction

from http import HTTPStatus
from hashlib import pbkdf2_hmac
from binascii import hexlify

import random
import string
import jwt

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

ServerHandler = make_resource_handler(
    lambda bot, server_id: next((s for s in bot.servers if s.id == server_id), None),
    ('id', 'name', 'icon_url')
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

PluginsHandler = make_collection_handler(
    lambda bot: bot.plugin_collection.plugins,
    ('name', )
)

class FindHandler(RequestHandlerWithBotContext):

    def get(self):
        try:
            user_name = self.get_query_argument('user_name')
        except MissingArgumentError:
            self.set_status(HTTPStatus.BAD_REQUEST)
            return

        user = self.bot.find_user_by_name(user_name)
        if user:
            data = extract_attributes(user, ('id', 'name', 'avatar_url'))
            self.write(json_encode(data))
        else:
            self.set_status(HTTPStatus.BAD_REQUEST)

tokenCache = dict()

def make_token():
    return ''.join(
        random.choice(string.ascii_uppercase + string.digits)
        for _ in range(32)
    )

class RegistrationTokenHandler(RequestHandlerWithBotContext):

    async def post(self, user_id):
        user = self.bot.find_user(user_id)
        if user and user_id not in tokenCache:
            token = make_token()
            await self.bot.send_message(
                user,
                'Here is your registration token: `{}`'.format(token)
            )
            tokenCache[user_id] = token
        else:
            self.set_status(HTTPStatus.BAD_REQUEST)

def make_salt():
    return ''.join(
        random.choice(string.ascii_uppercase + string.digits)
        for _ in range(32)
    )

class RegistrationHandler(RequestHandlerWithBotContext):

    async def post(self):
        try:
            user_id = self.get_body_argument('user')
            token = self.get_body_argument('token')
            password = self.get_body_argument('password')
        except MissingArgumentError:
            self.set_status(HTTPStatus.BAD_REQUEST)
            return

        if tokenCache.get(user_id) != token:
            self.set_status(HTTPStatus.BAD_REQUEST)
            self.write('Invalid token')
            return
        if len(password) == 0:
            self.set_status(HTTPStatus.BAD_REQUEST)
            self.write('Password too short')
            return
        if not self.register_user(user_id, password):
            self.set_status(HTTPStatus.BAD_REQUEST)
            self.write('Already registered')
            return

    def register_user(self, user_id, password):
        try:
            with Transaction(self.bot.db) as trans:
                trans.execute('''
                    select * from person where id = %(id)s
                ''', dict(id=user_id))

                if trans.fetchone():
                    return False

                password_salt = make_salt()
                hashed_password = pbkdf2_hmac(
                    'sha256',
                    password.encode(),
                    password_salt.encode(),
                    10000
                )

                data = dict(
                    id            = user_id,
                    password      = hexlify(hashed_password).decode('ascii'),
                    password_salt = password_salt
                )
                trans.execute('''
                    insert into person (id, password, password_salt)
                                values (%(id)s, %(password)s, %(password_salt)s)
                ''', data)

                return True
        except Exception as e:
            logger.error(e)
            return False

class LoginHandler(RequestHandlerWithBotContext):

    JWT_SALT = 'Gl0b1Bo7'

    def post(self):
        try:
            user_name = self.get_body_argument('user')
            password = self.get_body_argument('password')
        except MissingArgumentError:
            self.set_status(HTTPStatus.BAD_REQUEST)
            return

        user = self.bot.find_user_by_name(user_name)
        if not user:
            self.set_status(HTTPStatus.BAD_REQUEST)
            return
        logger.info('found user: {}'.format(user.name))
        if not self.check_user(user, password):
            self.set_status(HTTPStatus.BAD_REQUEST)
            return

        logger.info('password matched')

        data = dict(
            user = extract_attributes(user, ('id', 'name', 'avatar_url')),
            token = self.make_token(user).decode('utf-8')
        )
        self.set_header("Content-Type", 'application/json')
        self.write(json_encode(data))

    def check_user(self, user, password):
        with Transaction(self.bot.db) as trans:
            trans.execute('''
                select      password, password_salt from person
                    where   id = %(id)s
            ''', dict(id=user.id))

            credentials = trans.fetchone()
            logger.info(credentials)
            if not credentials:
                return False

            expected_hashed_password, password_salt = credentials
            hashed_password = pbkdf2_hmac(
                'sha256',
                password.encode(),
                password_salt.encode(),
                10000
            )
            logger.info(hexlify(hashed_password).decode('ascii'))
            logger.info(expected_hashed_password)

            return (expected_hashed_password == hexlify(hashed_password).decode('ascii'))

        return False

    def make_token(self, user):
        payload = dict(
            user = user.id
        )
        return jwt.encode(
            payload,
            LoginHandler.JWT_SALT,
            algorithm='HS256'
        )
