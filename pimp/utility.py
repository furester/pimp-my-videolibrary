class Utility:
    _debug = False

    def __init__(self, debug=False):
        self._debug = debug

    def log(self, *message):
        if self._debug:
            print message

    def out(self, message):
        print message
