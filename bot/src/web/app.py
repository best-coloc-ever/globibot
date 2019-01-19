from tornado import web
from tornado.platform.asyncio import AsyncIOMainLoop

from utils.logging import logger

from collections import defaultdict

from . import constants as c

def init_web_app(config):
    AsyncIOMainLoop().install()

    port = config.get(c.WEB_PORT_KEY, c.DEFAULT_WEB_PORT)

    return WebApplication(
        port,
        cookie_secret = config.get(c.COOKIE_SECRET_KEY)
    )

class WebApplication(web.Application):

    def __init__(self, port, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.port = port
        self.handlers = defaultdict(list)

    async def run(self):
        try:
            self.listen(self.port)
            logger.info('Web server listening on port {}'.format(self.port))
        except Exception as e:
            logger.error('Could not start web server: {}'.format(e))

    def add_routes(self, context, *handlers):
        self.handlers[context] += [
            handler[1] for handler in handlers
        ]

        self.add_handlers(r'.*$', handlers)

    def remove_routes(self, context):
        logger.debug(len(self.default_router.rules))
        filtered_rules = [
            rule for rule in self.default_router.rules if
            len([r for r in rule.target.rules if r.target not in self.handlers[context]])
        ]
        self.default_router.rules = filtered_rules
        logger.debug(len(filtered_rules))
