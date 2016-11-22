from globibot.lib.web.handlers import ContextHandler
from globibot.lib.web.constants import USER_COOKIE_NAME
from globibot.lib.web.decorators import with_body_arguments, async_handler
from globibot.lib.transaction import Transaction

from . import queries as q
from . import constants as c

from http import HTTPStatus
from hashlib import pbkdf2_hmac
from binascii import hexlify

import random
import string

tokenCache = dict()

def make_token():
    return ''.join(
        random.choice(string.ascii_uppercase + string.digits)
        for _ in range(32)
    )

make_salt = make_token

def hash_password(password, salt):
    hashed = pbkdf2_hmac(
        c.PKCS_HASH_NAME,
        password.encode(),
        salt.encode(),
        c.PKCS_ITERATION_COUNT
    )

    return hexlify(hashed).decode('ascii')

def check_credentials_for(user, password, db):
    with Transaction(db) as trans:
        trans.execute(q.get_credentials, dict(id=user.id))

        credentials = trans.fetchone()

        if not credentials:
            return False

        expected_hashed_password, password_salt = credentials
        hashed_password = hash_password(password, password_salt)

        return (expected_hashed_password == hashed_password)

    return False

def register_user(user_id, password, db):
    with Transaction(db) as trans:
        trans.execute(q.get_person, dict(id=user_id))

        if trans.fetchone():
            return False

        password_salt = make_salt()
        hashed_password = hash_password(password, password_salt)

        data = dict(
            id            = user_id,
            password      = hashed_password,
            password_salt = password_salt
        )
        trans.execute(q.create_user, data)

        return True

class LoginHandler(ContextHandler):

    @with_body_arguments('user', 'password')
    def post(self, user, password):
        users = self.bot.find_users_by_name(user)

        if users:
            for user in users:
                if check_credentials_for(user, password, self.bot.db):
                    self.set_secure_cookie(
                        USER_COOKIE_NAME,
                        user.id,
                        expires_days=c.SESSION_COOKIE_DURATION
                    )
                    return

        self.set_status(HTTPStatus.BAD_REQUEST)

class RegistrationHandler(ContextHandler):

    @with_body_arguments('user', 'token', 'password')
    def post(self, user, token, password):
        if tokenCache.get(user) != token:
            self.set_status(HTTPStatus.BAD_REQUEST)
            self.write('Invalid token')
            return

        if len(password) == 0:
            self.set_status(HTTPStatus.BAD_REQUEST)
            self.write('Password too short')
            return

        if not register_user(user, password, self.bot.db):
            self.set_status(HTTPStatus.BAD_REQUEST)
            self.write('Already registered')
            return

class RegistrationTokenHandler(ContextHandler):

    @async_handler
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
