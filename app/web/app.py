from tornado import web
from tornado.platform.asyncio import AsyncIOMainLoop

from utils.logging import logger

from . import constants as c
from . import handlers

async def run_web_app(bot):
    AsyncIOMainLoop().install()

    routes = [

    ]

    web_app = web.Application(
        routes,
        autoreload=True,
    )

    try:
        web_app.listen(c.DEFAULT_PORT)
        logger.info('Web server listening on port {}'.format(c.DEFAULT_PORT))
    except Exception as e:
        logger.error('Could not start web server: {}'.format(e))
