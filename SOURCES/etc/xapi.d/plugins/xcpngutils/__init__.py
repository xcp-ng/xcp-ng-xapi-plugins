#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import logging.handlers
import os
import signal
import subprocess
import sys
import traceback
import types
from contextlib import contextmanager
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Sequence, Type, Union

import XenAPIPlugin


class NoNewlineFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        formatted = super(NoNewlineFormatter, self).format(record)
        return formatted.replace("\n", "\\n").replace("\r", "\\r")

def configure_logging(name: str) -> logging.Logger:
    log_file = "/var/log/" + name + "-plugin.log"
    enable_dev_logging_file = "/opt/xensource/packages/files/" + name + "-plugin/devlogging_enabled"

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    def handle_unhandled_exceptions(exception_type: Type[BaseException],
                                    exception_value: BaseException,
                                    exception_traceback: types.TracebackType) -> None:
        if not issubclass(exception_type, KeyboardInterrupt):
            log_unhandled_exception("standalone", exception_type, exception_value,
                                    exception_traceback)
        sys.__excepthook__(exception_type, exception_value, exception_traceback)

    def log_unhandled_exception(origin: str, exception_type: Type[BaseException],
                                exception_value: BaseException,
                                exception_traceback: types.TracebackType) -> None:
        logger.error("Nobody caught %s exception: %s" % (origin, exception_type))
        problem = traceback.format_exception(exception_type,
                                             exception_value,
                                             exception_traceback)
        for line in problem:
            logger.error(line)

    formatter = NoNewlineFormatter(
        '%(asctime)s - [%(process)d] - %(levelname)s - %(message)s',
        '%Y-%m-%d %H:%M:%S')

    handlers: List[logging.Handler] = []
    log_level: int = logging.INFO

    if os.access(os.path.dirname(log_file), os.W_OK):
        fileh = logging.handlers.RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=5)
        handlers.append(fileh)

    if os.path.exists(enable_dev_logging_file) or not handlers:
        handlers.append(logging.StreamHandler(sys.stdout))
        log_level = logging.DEBUG

    # Configure and add all handlers
    for handler in handlers:
        handler.setLevel(log_level)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    sys.excepthook = handle_unhandled_exceptions
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)
    return logger


class ProcessException(subprocess.CalledProcessError):
    def __init__(self, code: int, command: Sequence[str], stdout: bytes, stderr: bytes) -> None:
        super(ProcessException, self).__init__(code, command, output=stdout)
        self.stderr = stderr

    def __str__(self) -> str:
        return "Command '%s' failed with code: %d" % (self.cmd, self.returncode)

def run_command(command: Sequence[str], check: bool = True) -> Dict[str, Union[bytes, Sequence[str], int]]:
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    code = process.returncode
    if check and code != 0:
        raise ProcessException(code, command, stdout, stderr)
    result = {'stdout': stdout, 'stderr': stderr, 'command': command, 'returncode': code}
    return result


class TimeoutException(Exception):
    pass

@contextmanager
def timeout(seconds: int):
    def handler(signum: int, frame: Optional[object]) -> None:
        raise TimeoutException()

    old_handler = signal.signal(signal.SIGALRM, handler)

    try:
        signal.alarm(seconds)
        yield
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old_handler)


def strtobool(str: Optional[str]) -> bool:
    # Note: `distutils` package is deprecated and slated for removal in Python 3.12.
    # There is not alternative for strtobool.
    # See: https://peps.python.org/pep-0632/#migration-advice
    # So this is a custom implementation with differences:
    # - A boolean is returned instead of integer
    # - Empty string and None are supported (False is returned in this case)
    if not str:
        return False
    str = str.lower()
    if str in ('y', 'yes', 't', 'true', 'on', '1'):
        return True
    if str in ('n', 'no', 'f', 'false', 'off', '0'):
        return False
    raise ValueError("invalid truth value '{}'".format(str))


def raise_plugin_error(code: Union[str, int], message: str, details: str = '', backtrace: str = '') -> None:
    raise XenAPIPlugin.Failure(str(code), [message, details, backtrace])


def error_wrapped(func: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(func)
    def wrapper(*args: Any, **kwds: Any) -> Any:
        try:
            return func(*args, **kwds)
        except XenAPIPlugin.Failure:
            # pass through what was already handled
            raise
        except EnvironmentError as e:
            message = e.strerror if e.strerror is not None else str(e.args)
            raise XenAPIPlugin.Failure(str(e.errno), [message, str(e.filename), traceback.format_exc()]) from e
        except ProcessException as e:
            raise_plugin_error(
                e.returncode, str(e),
                details="stdout: '%s', stderr: '%s'" % (e.output, e.stderr), backtrace=traceback.format_exc()
            )
        except Exception as e:
            raise_plugin_error('-1', str(e), backtrace=traceback.format_exc())

    return wrapper


def install_package(package_name: str) -> Dict[str, Union[bytes, Sequence[str], int]]:
    return run_command(['yum', 'install', '-y', package_name])
