from xcpngutils.filelocker import FileLocker


class OperationLocker(FileLocker):
    def lock(self, override_timeout=None):
        try:
            # noinspection PyProtectedMember
            super(OperationLocker, self).lock(override_timeout)
        except Exception:
            raise Exception("The plugin is busy.")
