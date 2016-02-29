from utils import run_async

from bot import init_globibot
from web import init_web_app

def main():
    web_app = init_web_app()
    globibot = init_globibot(web_app)

    run_async(
        web_app.run(),
        globibot.boot()
    )

if __name__ == '__main__':
    main()
