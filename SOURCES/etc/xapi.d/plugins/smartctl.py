#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import sys
import XenAPIPlugin

sys.path.append('.')
from xcpngutils import configure_logging, run_command, error_wrapped
from xcpngutils.operationlocker import OperationLocker

@error_wrapped
def _list_devices():
    devices = []
    result = run_command(['smartctl', '--scan'])
    for line in result['stdout'].splitlines():
        devices.append({'name': line.split()[0], 'type':line.split()[2]})
    return devices

@error_wrapped
def get_information(session, args):
    results = {}
    i = 0
    with OperationLocker():
        devices = _list_devices()
        for device in devices:
            cmd = run_command(["smartctl", "-j", "-a", "-d", devices[i]['name'], devices[i]['type']], check=False)
            results[device] = json.loads(cmd['stdout'])
            i = i + 1
        return json.dumps(results)

@error_wrapped
def get_health(session, args):
    results = {}
    i = 0
    with OperationLocker():
        devices = _list_devices()
        for device in devices:
            cmd = run_command(["smartctl", "-j", "-H", "-d", devices[i]['name'], devices[i]['type']])
            json_output = json.loads(cmd['stdout'])
            if json_output['smart_status']['passed']:
                results[disk] = "PASSED"
            else:
                results[disk] = "FAILED"
            i = i + 1
        return json.dumps(results)


_LOGGER = configure_logging('smartctl')
if __name__ == "__main__":
    XenAPIPlugin.dispatch({
        'information': get_information,
        'health': get_health
    })
