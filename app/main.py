GLOBIBOT_EMAIL_KEY = 'GLOBIBOT_EMAIL'
GLOBIBOT_PASSWORD_KEY = 'GLOBIBOT_PASSWORD'

GLOBIBOT_DEFAULT_EMAIL = 'globibot.official@gmail.com'

from bot import Globibot

import sys
import os

def main():
    email = os.getenv(GLOBIBOT_EMAIL_KEY, GLOBIBOT_DEFAULT_EMAIL)
    password = os.getenv(GLOBIBOT_PASSWORD_KEY)

    if password is None:
        sys.exit(
            "Please specify Globibot's credentials:\n"
            " - Globibot's email:    {}\n"
            " - Globibot's password: {}\n"
                .format(GLOBIBOT_EMAIL_KEY, GLOBIBOT_PASSWORD_KEY)
        )

    globibot = Globibot(email, password)
    globibot.boot()

if __name__ == '__main__':
    main()
