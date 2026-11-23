import os
import sys
from typing import Optional

from xcpngutils.filelocker import FileLocker


class PidFile(FileLocker):
    def __init__(self, lockname: Optional[str] = None, timeout: int = 0,
                 auto_remove: bool = True, dir: Optional[str] = None) -> None:
        if lockname is not None:
            lockname = self.lockname
        else:
            lockname = '{}.pid'.format(os.path.basename(sys.argv[0]))
        super(PidFile, self).__init__(lockname, timeout, auto_remove, dir)

    def _locked(self) -> None:
        file = self.file
        if file is None:
            return
        file.seek(0)
        file.truncate()
        file.write('{}\n'.format(self.pid))
        file.flush()
