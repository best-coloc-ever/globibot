from watchdog.observers import Observer as PathObserver
from watchdog.events import FileSystemEventHandler

from importlib import import_module, reload
from traceback import format_exc
from os.path import join as path_join
from types import ModuleType

from utils.logging import logger

import bot.plugins as plugins_root

def unsafe(action, *args, **kwargs):
    try:
        action(*args, **kwargs)
    except:
        logger.error(format_exc(10))

class PluginReloader(FileSystemEventHandler):

    def __init__(self, name, *args):
        self.name = name
        self.args = args
        self.scope = '{}.{}'.format(plugins_root.__name__, name)
        self.import_args = ('.{}'.format(name), plugins_root.__name__)
        self.plugin = None
        self.loaded = False

        unsafe(self.load_plugin)

    def load_plugin(self):
        logger.info('Loading plugin: {}...'.format(self.name))

        self.module = import_module(*self.import_args)
        self.loaded = True
        self.plugin = self.module.plugin_cls(*self.args)
        logger.info('...done')

    def reload_plugin(self):
        logger.info('reloading {}...'.format(self.module))

        self.reload_module(self.module)
        self.plugin = self.module.plugin_cls(*self.args)
        logger.info('...done')

    def on_modified(self, modified):
        if self.loaded:
            unsafe(self.reload_plugin)
        else:
            unsafe(self.load_plugin)

    def reload_module(self, module):
        for attribute_name in dir(module):
            attribute = getattr(module, attribute_name)

            if type(attribute) is ModuleType:
                if attribute.__name__.startswith(self.scope):
                    self.reload_module(attribute)

        reload(module)

class PluginCollection:

    def __init__(self, bot, plugin_descriptors):
        self.path_observer = PathObserver()
        self.plugin_reloaders = []

        for name, config in plugin_descriptors:
            reloader = PluginReloader(name, bot, config)
            self.plugin_reloaders.append(reloader)
            self.path_observer.schedule(
                reloader,
                path_join(plugins_root.__path__._path[0], name),
                recursive=True
            )

        self.path_observer.start()

    @property
    def plugins(self):
        return [
            reloader.plugin for reloader in
            self.plugin_reloaders
            if reloader.plugin
        ]
