#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json

import XenAPIPlugin

from xcpngutils import configure_logging, run_command, error_wrapped

def run_service_command(cmd_name, args):
    service = args.get('service')
    if not service:
        raise Exception('Missing or empty argument `service`')
    run_command(['systemctl', cmd_name, service])
    return json.dumps(True)

@error_wrapped
def start_service(session, args):
    return run_service_command('start', args)

@error_wrapped
def stop_service(session, args):
    return run_service_command('stop', args)

@error_wrapped
def restart_service(session, args):
    return run_service_command('restart', args)

@error_wrapped
def try_restart_service(session, args):
    return run_service_command('try-restart', args)

_LOGGER = configure_logging('service')
if __name__ == "__main__":
    XenAPIPlugin.dispatch({
        'start_service': start_service,
        'stop_service': stop_service,
        'restart_service': restart_service,
        'try_restart_service': try_restart_service
    })
