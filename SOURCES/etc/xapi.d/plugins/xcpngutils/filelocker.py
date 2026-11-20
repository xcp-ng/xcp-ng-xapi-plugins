import errno
import fcntl
import os
import signal
import sys
from typing import Optional

from xcpngutils import TimeoutException, timeout

FILE_LOCKER_DIRECTORY = "/var/run/"

def safe_flock(file, flags: int) -> None:
    filename = file.name

    while True:
        try:
            fd = file.fileno()
            fcntl.flock(fd, flags)
            return
        except IOError as e:
            if e.errno == errno.EINTR:
                continue

            if e.errno != errno.EBADF and e.errno != errno.EINVAL:
                raise

            # Retry if file has been removed.
            stat = os.fstat(fd)
            if stat.st_nlink or (flags & fcntl.LOCK_UN):
                raise e

            file.close()
            file = open(filename, 'a+')

class FileLocker(object):
    __slots__ = ('pid', 'lockname', 'filename', 'previous_signal', 'file', 'timeout', 'auto_remove')

    def __init__(self, lockname: Optional[str] = None, timeout: int = 0,
                 auto_remove: bool = True, dir: Optional[str] = None) -> None:
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

    def __del__(self) -> None:
        self.unlock()

    def __enter__(self) -> "FileLocker":
        self.lock()
        return self

    def __exit__(self, exception_type: Optional[type], exception_value: Optional[BaseException],
                 traceback: object) -> None:
        self.unlock()

    def lock(self, override_timeout: Optional[int] = None) -> None:
        cur_timeout = override_timeout if override_timeout is not None else self.timeout
        try:
            self.file = open(self.filename, 'a+')
            if cur_timeout <= 0:
                safe_flock(self.file, fcntl.LOCK_EX | fcntl.LOCK_NB)
            else:
                try:
                    with timeout(cur_timeout):
                        safe_flock(self.file, fcntl.LOCK_EX)
                except TimeoutException:
                    self._timeout_reached()
                    raise Exception('Timeout reached') from None
        except Exception:
            if self.file:
                self.file.close()
                self.file = None
            raise

        self._register_signal_handler()
        self._locked()

    def unlock(self) -> None:
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
            safe_flock(file, fcntl.LOCK_UN)
        except IOError as error:
            if error.errno != errno.EBADF:
                raise
        finally:
            # An exception can be thrown if it exists remaining data to flush, so reset file before close.
            self.file = None
            file.close()

    def _make_filename(self, dir: str) -> str:
        if self.lockname is not None:
            filename = self.lockname
        else:
            filename = '{}.lock'.format(os.path.basename(sys.argv[0]))
        return os.path.abspath(os.path.join(dir, filename))

    def _handle_sigterm(self, signum: int, frame: Optional[object]) -> None:
        self.unlock()
        raise SystemExit(1)

    def _register_signal_handler(self) -> None:
        def handler(signum: int, frame: Optional[object]) -> None:
            self._handle_sigterm(signum, frame)
        self.previous_signal = signal.signal(signal.SIGTERM, handler)

    def _unregister_signal_handler(self) -> None:
        signal.signal(signal.SIGTERM, self.previous_signal)
        self.previous_signal = None

    def _timeout_reached(self) -> None:
        pass

    def _locked(self) -> None:
        pass

    def _unlocked(self) -> None:
        pass
