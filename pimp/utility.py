class Utility:
    _debug = False

    def __init__(self, debug=False):
        self._debug = debug

    def log(self, *message):
        if len(message) == 1:
            _m = message[0]
        else:
            _m = message
        if self._debug:
            print _m

    def out(self, message):
        print message

    def pretty(self, d, indent=0):
        for key, value in d.items():
            print('\t' * indent + str(key))
            if isinstance(value, dict):
                self.pretty(value, indent + 1)
            else:
                print('\t' * (indent + 1) + str(value))
