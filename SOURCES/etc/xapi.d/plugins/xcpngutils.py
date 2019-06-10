#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import logging.handlers
import os
import sys
import traceback
import signal
import subprocess


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


def run_command(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    result = {'exit': process.returncode, 'stdout': stdout, 'stderr': stderr, 'command': command}
    return result
