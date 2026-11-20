from typing import Optional

from xcpngutils.filelocker import FileLocker


class OperationLocker(FileLocker):
    def lock(self, override_timeout: Optional[int] = None) -> None:
        try:
            # noinspection PyProtectedMember
            super(OperationLocker, self).lock(override_timeout)
        except Exception:
            raise Exception('The plugin is busy.') from None
