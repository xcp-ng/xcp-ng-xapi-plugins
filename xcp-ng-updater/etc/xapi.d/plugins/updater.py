#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import traceback
import XenAPIPlugin
import logging
import logging.handlers
import yum
import json

import signal

LOG_FILE = "/var/log/updater.log"
ENABLE_DEV_LOGGING_FILE = "/opt/xensource/packages/files/updater/devlogging_enabled"


def check_update(session, args):
    yum_instance = yum.YumBase()
    yum_instance.preconf.debuglevel = 0
    yum_instance.preconf.plugins = True
    packages = yum_instance.doPackageLists(pkgnarrow='updates')
    return json.dumps({'result': map(
        lambda p: {'name': p.name, 'version': p.version, 'release': p.release, 'arch': p.arch, 'fullName': p.ui_envra},
        packages)})


def handle_unhandled_exceptions(exception_type, exception_value,
                                exception_traceback):
    if not issubclass(exception_type, KeyboardInterrupt):
        log_unhandled_exception("standalone", exception_type, exception_value,
                                exception_traceback)
    sys.__excepthook__(exception_type, exception_value, exception_traceback)


def log_unhandled_exception(origin, exception_type, exception_value,
                            exception_traceback):
    _LOGGER.error("Nobody caught %s exception: %s" % (origin, exception_type))
    problem = traceback.format_exception(exception_type,
                                         exception_value,
                                         exception_traceback)
    for line in problem:
        _LOGGER.error(line)


def configure_logging():
    _LOGGER.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(asctime)s - [%(process)d] - %(levelname)s - %(message)s',
        '%Y-%m-%d %H:%M:%S')

    handlers = []
    log_level = logging.INFO

    if os.access(os.path.dirname(LOG_FILE), os.W_OK):
        fileh = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=5)
        handlers.append(fileh)

    if os.path.exists(ENABLE_DEV_LOGGING_FILE) or not handlers:
        handlers.append(logging.StreamHandler(sys.stdout))
        log_level = logging.DEBUG

    # Configure and add all handlers
    for handler in handlers:
        handler.setLevel(log_level)
        handler.setFormatter(formatter)
        _LOGGER.addHandler(handler)

    signal.signal(signal.SIGPIPE, signal.SIG_DFL)


_LOGGER = logging.getLogger()
configure_logging()
sys.excepthook = handle_unhandled_exceptions
if __name__ == "__main__":
    XenAPIPlugin.dispatch({
        'check_update': check_update
    })
