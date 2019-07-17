#!/usr/bin/env python
# -*- coding: utf-8 -*-
from xcpngutils.filelocker import FileLocker
import os
import sys

class PidFile(FileLocker):
    def __init__(self, lockname=None, timeout=0, auto_remove=True, dir=None):
        if lockname is not None:
            lockname = self.lockname
        else:
            lockname = '{}.pid'.format(os.path.basename(sys.argv[0]))
        super(PidFile, self).__init__(lockname, timeout, auto_remove, dir)

    def _locked(self):
        self.file.seek(0)
        self.file.truncate()
        self.file.write('{}\n'.format(self.pid))
        self.file.flush()
