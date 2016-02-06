from utils import run_async

from bot import init_globibot
from web import run_web_app

def main():
    globibot = init_globibot()

    run_async(
        run_web_app(globibot),
        globibot.boot()
    )

if __name__ == '__main__':
    main()
