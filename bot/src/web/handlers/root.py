from tornado.web import RequestHandler

from os.path import join as join_path

class RootHandler(RequestHandler):

    def initialize(self, path):
        self.path = path

    def get(self):
        with open(join_path(self.path, 'index.html'), 'r') as f:
            self.write(f.read())
