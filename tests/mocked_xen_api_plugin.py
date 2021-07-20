class Failure(Exception):
    def __init__(self, code, params):
        Exception.__init__(self)
        self.params = [code] + params

    def __str__(self):
        return str(self.params)
