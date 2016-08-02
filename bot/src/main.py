from utils.async import run_async

from bot.globibot import Globibot
from web.app import init_web_app

from utils.config import web_config, db_config, bot_config

def main():
    web_app = init_web_app(web_config)
    globibot = Globibot(bot_config, db_config, web_app)

    run_async(
        web_app.run(),
        globibot.boot()
    )

if __name__ == '__main__':
    main()
