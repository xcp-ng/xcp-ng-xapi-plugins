class FileLockerError(Exception):
    pass

class FileLocker(object):
    def __init__(self, lockname=None, timeout=0, auto_remove=True, dir=None):
        self.locked = False

    def __del__(self):
        self._unlock()

    def __enter__(self):
        self._lock()
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self._unlock()

    def _lock(self):
        if self.locked:
            raise FileLockerError
        else:
            self.locked = True

    def _unlock(self):
        self.locked = False
