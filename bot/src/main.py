from utils.async import run_async

from globibot.bot import Globibot
from web.app import init_web_app

from utils.config import load_config
from utils.options import parse_args

def main():
    args = parse_args()
    bot_config, web_config, db_config = load_config(args.config_path)

    web_app = init_web_app(
        web_config,
        args.static_root
    )

    globibot = Globibot(
        bot_config,
        db_config,
        web_app,
        args.plugin_path
    )

    run_async(
        web_app.run(),
        globibot.boot()
    )

if __name__ == '__main__':
    main()
