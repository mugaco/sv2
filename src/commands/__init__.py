# /usr/local/bin/sv2/src/commands/__init__.py


class Command:
    def __init__(self, app):
        self.app = app

    def run(self, args):
        raise NotImplementedError("El método run() debe ser implementado.")
