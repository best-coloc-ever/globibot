# globibot [![Build Status](https://travis-ci.org/best-coloc-ever/globibot.svg?branch=master)](https://travis-ci.org/best-coloc-ever/globibot)
A plugin-based, extensible bot for [Discord](https://discordapp.com)

## Configuration
The bot configuration is read from a `yaml` file (specified with `--config-path`)  
You can copy the existing [`config.example.yaml`](./bot/config.example.yaml) file and fill in the values yourself

You must at least provide a valid `token` for your bot under the top level `bot` configuration key  
There must also be a top level `web` key as well as a top level `db`

A minimalistic configuration file could look like this:
```yaml
bot:
  # A valid discord application token
  token: 'MyaWes0mebOtT0k3n'

  # Plugins to enable
  plugins:
    some_plugin: {}
    some_other_plugin_with_conf:
      conf_key: 'conf value'

  # Server named on which Globibot will process messages
  servers:
    - 'Some server name'

  # Ids of people able to use "master commands"
  masters:
    - 'Some snowflake id for a discord account'

web:
  port: 80

db:
  host: db
  user: postgres
```

## Deployment :whale:
If you want to use the webserver:

Place/generate your SSL/TLS certificate in `./web/server/fullchain.pem`  
Place the associated private key in `./web/server/privkey.pem`

Then make sure `docker >= 1.10` and `docker-compose >= 1.6` are installed and run:

```sh
./dev run --rm web-builder npm install # Fetch node dependencies
./dev run --rm web-builder webpack -p # Bundle the website

./prod up -d db # Boots up the db
./dev run --rm db flyway migrate # Populate the db

./prod up -d # Boots up the bot and the webserver

./prod logs -f bot # To access the bot's stdout logs
```

## Using plugins
Globibot comes with a minimalistic set of plugins

Plugins are python modules loaded from the directory specified by `--plugin-path`

To enable a plugin, you can just add its name in the configuration file under the `plugins` key

### Creating plugins
For globibot to be able to load a plugin, your plugin module must export a symbol called `plugin_cls` which would point to a class that inherits `Plugin` from `bot.lib.plugin`

Let's create a simple plugin called `foo`

In `./bot/plugins/foo/__init__.py`:
```python
from .foo_plugin import Foo

plugin_cls = Foo
```

In `./bot/plugins/foo/foo_plugin.py`:
```python
from bot.lib.plugin import Plugin

class Foo(Plugin):
    pass
```

In `./bot/config.yaml` let's add our plugin with a dummy config:
```yaml
bot:
  # ...

  plugins:

    foo:
      bar: 1337

  # ...
```

Now if you start/restart the bot:
```sh
docker-compose up -d bot # To start the bot
# Or
docker-compose restart -t 0 bot # To restart the bot
```

You should see in the logs that Globibot loaded your plugin:
![image](https://cloud.githubusercontent.com/assets/2079561/17460022/b11212a6-5c53-11e6-9428-913714d5edd8.png)

From this moment on, any changes to your `foo` modules will be reloaded automatically when module files change

Let's add a simple command to the plugin:

In `./bot/src/bot/plugins/foo/foo_plugin.py`:
```python
from globibot.lib.plugin import Plugin

from globibot.lib.decorators import command # Command declaration helper

from globibot.lib.helpers import parsing as p # Parser combinator tools
from globibot.lib.helpers.hooks import master_only # Hook to only allow master users

class Foo(Plugin):

    def load(self):
        '''
        Called on plugin load/reload
        '''

        # Loads the value of the `bar` configuration key with a default value
        # if the key were to be absent
        self.bar = self.config.get('bar', 42)

    @command(p.string('!foo') + p.bind(p.integer, 'number'))
    async def foo_command(self, message, number):
        '''
        Called on inputs starting with the string '!foo' (case insensitive)
        followed by an integer whose value will be bound to the `number`
        variable
        '''

        await self.send_message(
            message.channel, # Sends a message in the same channel as the input
            '{} * {} = {}'.format(number, self.bar, number * self.bar)
        )

    @command(p.string('!id') + p.bind(p.mention, 'user_id'), master_only)
    async def id_command(self, message, user_id):
        '''
        Called on inputs starting with the string '!id' (case insensitive)
        followed by a discord user mention (usually displayed '@SomeUser' on
        discord's client)

        We have access to SomeUser's discord's ID in the `user_id` variable

        The command is marked as `master_only` and will execute only if the
        input was sent by someone who was registered as 'master' in the
        configuration file
        '''

        await self.send_message(
            message.channel,
            '{}: the id is {}'
                .format(message.author.mention, user_id),
            delete_after = 30 # Message deletes itself after 30 seconds
        )

```

Upon saving this file, you should see this:  
![image](https://cloud.githubusercontent.com/assets/2079561/17460080/4b7c968e-5c56-11e6-8de8-003a5434c9fa.png)

And then you can simply test the results in discord directly:  
![image](https://cloud.githubusercontent.com/assets/2079561/17460094/33230536-5c57-11e6-801b-20801d23be63.png)
