from http import HTTPStatus

from globibot.lib.web.handlers import ContextHandler
from globibot.lib.web.decorators import respond_json

import json

class ToxicityTableHandler(ContextHandler):

    def get(self):
        with open('./plugins/lirik/html/toxicity_table.html') as f:
            self.write(f.read())

user_profile_cache = dict()

class ToxicityDataHandler(ContextHandler):

    @respond_json
    def get(self):
        def user_profile(user_id):
            try:
                return user_profile_cache[user_id]
            except KeyError:
                user = self.plugin.bot.find_user(user_id)
                name = user.name if user else f'<@{user_id}>'
                avatar_url = user.avatar_url if user else None
                profile = (name, avatar_url)
                user_profile_cache[user_id] = profile
                return profile

        return tuple(
            (user_profile(user_id), data)
            for user_id, data in self.plugin.toxicity.items()
        )

class AnimalsDataHandler(ContextHandler):

    @respond_json
    def get(self):
        return {
            name: json.load(open(f'/tmp/globibot/animals_galore/{galore.file_name}', 'r'))
            for name, galore in self.plugin.animal_galore.items()
        }


class AnimalsViewHandler(ContextHandler):

    def get(self):
        with open('./plugins/lirik/html/animals.html') as f:
            self.write(f.read())
