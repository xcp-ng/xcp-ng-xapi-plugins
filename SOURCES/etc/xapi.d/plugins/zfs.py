#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import errno
import subprocess
import sys
import traceback
import XenAPIPlugin
import logging
import logging.handlers
import json

import signal

LOG_FILE = "/var/log/zfs-plugin.log"
ENABLE_DEV_LOGGING_FILE = "/opt/xensource/packages/files/zfs-plugin/devlogging_enabled"


# returns a JSON dict {<poolname>: {mountpoint: <mountpoint>, ...}}
# xe host-call-plugin host-uuid=<UUID> plugin=zfs.py fn=list_zfs_pools
def list_zfs_pools(session, args):
    try:
        result = run_command(['zfs', 'get', '-H', 'all'])
        lines = result['stdout'].splitlines()
        res = {}

        def set_entry(pool, key, value):
            if pool in res:
                res.get(pool)[key] = value
            else:
                res[pool] = {key: value}

        for line in lines:
            split_line = line.split('\t')
            set_entry(split_line[0], split_line[1], split_line[2])
        return json.dumps(res)
    except OSError as e:
        if e.errno == errno.ENOENT:
            return json.dumps({})
        else:
            raise e


def run_command(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    result = {'exit': process.returncode, 'stdout': stdout, 'stderr': stderr, 'command': command}
    _LOGGER.info(result)
    return result


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


_LOGGER = logging.getLogger('zfs')
configure_logging()
sys.excepthook = handle_unhandled_exceptions
if __name__ == "__main__":
    XenAPIPlugin.dispatch({
        'list_zfs_pools': list_zfs_pools
    })
