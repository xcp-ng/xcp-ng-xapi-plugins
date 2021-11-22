from xcpngutils.filelocker import FileLocker

class OperationLocker(FileLocker):
    def _lock(self):
        try:
            # noinspection PyProtectedMember
            super(OperationLocker, self)._lock()
        except Exception:
            raise Exception('The plugin is busy.')
