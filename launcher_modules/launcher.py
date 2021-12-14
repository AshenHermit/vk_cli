import argparse
from vk_cli import VERSION

class Launcher():
    def __init__(self):
        self.operations = {}
        self.register_operation_decorators()

    def start_operation(self, id):
        if id in self.operations:
            self.operations[id]()

    def start(self, id):
        self.start_operation(id)

    def register_operation(self, id="default"):
        def _impl(func):
            self.operations[id] = func
            return func
        return _impl
    
    def register_operation_decorators(self):

        @self.register_operation(id="run")
        def run_operation():
            from vk_cli import run
            # print("run operation")
            run()

        @self.register_operation(id="install")
        def install_operation():
            # print("install operation")
            pass
