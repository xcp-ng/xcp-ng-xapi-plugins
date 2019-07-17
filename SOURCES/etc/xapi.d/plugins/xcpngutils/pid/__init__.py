#!/usr/bin/env python
# -*- coding: utf-8 -*-
from .. import timeout
from functools import partial
import errno
import fcntl
import os
import signal
import sys

PID_DIRECTORY = "/var/run/"

class PidFileError(Exception):
    pass

class PidFile(object):
    __slots__ = ('pid', 'lockname', 'filename', 'previousSignal', 'file', 'timeout')

    def __init__(self, lockname=None, timeout=0):
        self.pid = os.getpid()
        self.lockname = lockname
        self.filename = self._make_filename()
        self.previousSignal = None
        self.file = None
        self.timeout = timeout

    def __enter__(self):
        self._create()
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self._destroy()

    def _create(self):
        self.file = open(self.filename, 'a+')

        try:
            fd = self.file.fileno()
            if self.timeout <= 0:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            else:
                with timeout(self.timeout):
                    try:
                        fcntl.flock(fd, fcntl.LOCK_EX)
                    except IOError, error:
                        if error.errno != errno.EINTR:
                            raise error
                        raise PidFileError('Timeout reached')
        except Exception as error:
            self.file.close()
            self.file = None
            raise PidFileError(error)

        self._register_signal_handler()

        self.file.seek(0)
        self.file.truncate()
        self.file.write('{}\n'.format(self.pid))
        self.file.flush()

    def _destroy(self):
        self._unregister_signal_handler()

        try:
            if self.file is None:
                return
            self.file.close()
        except IOError as error:
            if error.errno != errno.EBADF:
                raise
        finally:
            os.remove(self.filename)
            self.file = None

    def _make_filename(self):
        progname = os.path.basename(sys.argv[0])
        if self.lockname is not None:
            filename = '{}-{}.pid'.format(progname, self.lockname)
        else:
            filename = '{}.pid'.format(progname)
        return os.path.abspath(os.path.join(PID_DIRECTORY, filename))

    def _handle_sigterm(self, signum, frame):
        self._destroy()
        raise SystemExit(1)

    def _register_signal_handler(self):
        self.previousSignal = signal.signal(signal.SIGTERM, partial(self._handle_sigterm, self))

    def _unregister_signal_handler(self):
        signal.signal(signal.SIGTERM, self.previousSignal)
        self.previousSignal = None
