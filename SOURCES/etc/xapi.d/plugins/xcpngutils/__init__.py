#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import logging
import logging.handlers
import os
import signal
import subprocess
import sys
import traceback
import XenAPIPlugin
from contextlib import contextmanager
from functools import wraps


def configure_logging(name):
    log_file = "/var/log/" + name + "-plugin.log"
    enable_dev_logging_file = "/opt/xensource/packages/files/" + name + "-plugin/devlogging_enabled"

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    def handle_unhandled_exceptions(exception_type, exception_value,
                                    exception_traceback):
        if not issubclass(exception_type, KeyboardInterrupt):
            log_unhandled_exception("standalone", exception_type, exception_value,
                                    exception_traceback)
        sys.__excepthook__(exception_type, exception_value, exception_traceback)

    def log_unhandled_exception(origin, exception_type, exception_value,
                                exception_traceback):
        logger.error("Nobody caught %s exception: %s" % (origin, exception_type))
        problem = traceback.format_exception(exception_type,
                                             exception_value,
                                             exception_traceback)
        for line in problem:
            logger.error(line)

    formatter = logging.Formatter(
        '%(asctime)s - [%(process)d] - %(levelname)s - %(message)s',
        '%Y-%m-%d %H:%M:%S')

    handlers = []
    log_level = logging.INFO

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
    def __init__(self, code, command, stdout, stderr):
        super(ProcessException, self).__init__(code, command, output=stdout)
        self.stderr = stderr

    def __str__(self):
        return "Command '%s' failed with code: %d" % (self.cmd, self.returncode)

def run_command(command, check=True):
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
def timeout(seconds):
    def handler(signum, frame):
        raise TimeoutException()

    old_handler = signal.signal(signal.SIGALRM, handler)

    try:
        signal.alarm(seconds)
        yield
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old_handler)


def strtobool(str):
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


def raise_plugin_error(code, message, details='', backtrace=''):
    raise XenAPIPlugin.Failure(str(code), [message, details, backtrace])


def error_wrapped(func):
    @wraps(func)
    def wrapper(*args, **kwds):
        try:
            return func(*args, **kwds)
        except XenAPIPlugin.Failure:
            # pass through what was already handled
            raise
        except EnvironmentError as e:
            message = e.strerror if e.strerror is not None else str(e.args)
            raise XenAPIPlugin.Failure(str(e.errno), [message, str(e.filename), traceback.format_exc()])
        except ProcessException as e:
            raise_plugin_error(
                e.returncode, str(e),
                details="stdout: '%s', stderr: '%s'" % (e.output, e.stderr), backtrace=traceback.format_exc()
            )
        except Exception as e:
            raise_plugin_error('-1', str(e), backtrace=traceback.format_exc())

    return wrapper


def install_package(package_name):
    return run_command(['yum', 'install', '-y', package_name])
