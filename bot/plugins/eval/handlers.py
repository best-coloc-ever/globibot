from http import HTTPStatus

from globibot.lib.web.handlers import ContextHandler

class ContainerLogHandler(ContextHandler):

    def get(self, container_id):
        logs = self.plugin.container_logs.get(container_id)

        if logs is None:
            self.set_status(HTTPStatus.NOT_FOUND)
        else:
            self.set_header('Content-Type', 'text/plain')
            self.write(''.join(logs) if logs else 'No output')
