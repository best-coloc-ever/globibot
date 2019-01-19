from watchdog.observers import Observer as PathObserver
from watchdog.events import PatternMatchingEventHandler

from importlib import import_module, reload
from traceback import format_exc
from os.path import join as path_join
from types import ModuleType
from queue import Queue

from utils.logging import logger

import asyncio

import sys
import os

def unsafe(action, *args, **kwargs):
    try:
        action(*args, **kwargs)
    except:
        logger.error(format_exc())

class PluginReloader(PatternMatchingEventHandler):

    def __init__(self, plugin_dir, name, *args):
        super().__init__(patterns=("*.py",))
        self.name = name
        self.args = args
        self.scope = '{}.{}'.format(plugin_dir, name)
        self.import_args = (self.scope,)

        self.plugin = None
        self.module_imported = False
        self.reload_queue = Queue()
        self.debouncing = False

        asyncio.ensure_future(self.watch_modified())

    def on_modified(self, modified):
        if not self.debouncing and self.reload_queue.empty():
            self.reload_queue.put(modified)

    def initialize(self):
        unsafe(self.load_plugin)

    def load_plugin(self):
        logger.info('Loading plugin: {}...'.format(self.name))

        self.module = import_module(*self.import_args)
        self.module_imported = True
        self.plugin = self.module.plugin_cls(*self.args)
        self.plugin.do_load()

    def reload_plugin(self):
        logger.info('Unloading plugin: {}'.format(self.name))
        self.plugin.do_unload()

        logger.info('Reloading module: {}...'.format(self.module))
        self.reload_module(self.module)

        logger.info('Loading plugin: {}'.format(self.name))
        self.plugin = self.module.plugin_cls(*self.args)
        self.plugin.do_load()

    def reload_module(self, module):
        for attribute_name in dir(module):
            attribute = getattr(module, attribute_name)

            if type(attribute) is ModuleType:
                if attribute.__name__.startswith(self.scope):
                    self.reload_module(attribute)

        reload(module)

    async def watch_modified(self):
        while True:
            while self.reload_queue.empty():
                await asyncio.sleep(.5)

            self.debouncing = True

            async def undebounce():
                await asyncio.sleep(3)
                self.debouncing = False

            asyncio.ensure_future(undebounce())

            self.reload_queue.get()

            if self.module_imported:
                unsafe(self.reload_plugin)
            else:
                unsafe(self.load_plugin)

            self.reload_queue.task_done()

class PluginCollection:

    def __init__(self, bot, plugin_path):
        plugin_abs_path = os.path.join(os.getcwd(), plugin_path)
        parent_plugin_abs_path, plugin_dir = os.path.split(plugin_abs_path)
        sys.path.insert(0, parent_plugin_abs_path)

        self.path_observer = PathObserver()
        self.plugin_reloaders = []

        for name, config in bot.plugin_descriptors:
            reloader = PluginReloader(plugin_dir, name, bot, config)
            self.plugin_reloaders.append(reloader)
            self.path_observer.schedule(
                reloader,
                path_join(plugin_abs_path, name),
                recursive=True
            )

        self.loaded = False

    def load_plugins(self):
        if not self.loaded:
            self.loaded = True

            for reloader in self.plugin_reloaders:
                reloader.initialize()

            self.path_observer.start()

    @property
    def plugins(self):
        return [
            reloader.plugin for reloader in
            self.plugin_reloaders
            if reloader.plugin
        ]
