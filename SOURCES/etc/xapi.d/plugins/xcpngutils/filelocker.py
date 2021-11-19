from functools import partial
from xcpngutils import timeout
import errno
import fcntl
import os
import signal
import sys

FILE_LOCKER_DIRECTORY = "/var/run/"

class FileLockerError(Exception):
    pass

class FileLocker(object):
    __slots__ = ('pid', 'lockname', 'filename', 'previous_signal', 'file', 'timeout', 'auto_remove')

    def __init__(self, lockname=None, timeout=0, auto_remove=True, dir=None):
        if not dir:
            dir = FILE_LOCKER_DIRECTORY
        if not os.path.exists(dir):
            os.makedirs(dir)

        self.pid = os.getpid()
        self.lockname = lockname
        self.filename = self._make_filename(dir)
        self.previous_signal = None
        self.file = None
        self.timeout = timeout
        self.auto_remove = auto_remove

    def __del__(self):
        self._unlock()

    def __enter__(self):
        self._lock()
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self._unlock()

    def _lock(self):
        try:
            while True:
                self.file = open(self.filename, 'a+')
                fd = self.file.fileno()
                if self.timeout <= 0:
                    self._prelock()
                    fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                else:
                    try:
                        self._prelock()
                        with timeout(self.timeout):
                            fcntl.flock(fd, fcntl.LOCK_EX)
                    except IOError as error:
                        if error.errno != errno.EINTR:
                            raise error
                        self._timeout_reached()
                        raise FileLockerError('Timeout reached')

                # Retry if file has been removed.
                # TODO: I'm not sure if it's a good idea to retry when timeout expires.
                # Maybe avoid this behavior.
                stat = os.fstat(fd)
                if stat.st_nlink:
                    break
                self.file.close()
        except Exception:
            if self.file:
                self.file.close()
                self.file = None
            raise

        self._register_signal_handler()
        self._locked()

    def _unlock(self):
        file = self.file
        if not file:
            return

        self._unregister_signal_handler()

        try:
            self._unlocked()
        except Exception:
            pass

        if self.auto_remove:
            try:
                os.remove(self.filename)
            except Exception:
                pass

        try:
            fcntl.flock(file.fileno(), fcntl.LOCK_UN)
        except IOError as error:
            if error.errno != errno.EBADF:
                raise
        finally:
            # An exception can be thrown if it exists remaining data to flush, so reset file before close.
            self.file = None
            file.close()

    def _make_filename(self, dir):
        if self.lockname is not None:
            filename = self.lockname
        else:
            filename = '{}.lock'.format(os.path.basename(sys.argv[0]))
        return os.path.abspath(os.path.join(dir, filename))

    def _handle_sigterm(self, signum, frame):
        self._unlock()
        raise SystemExit(1)

    def _register_signal_handler(self):
        self.previous_signal = signal.signal(signal.SIGTERM, partial(self._handle_sigterm, self))

    def _unregister_signal_handler(self):
        signal.signal(signal.SIGTERM, self.previous_signal)
        self.previous_signal = None

    def _prelock(self):
        pass

    def _timeout_reached(self):
        pass

    def _locked(self):
        pass

    def _unlocked(self):
        pass
