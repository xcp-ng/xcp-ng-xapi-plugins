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
        devices.append({'name': line.split()[0], 'type': line.split()[2]})
    return devices

@error_wrapped
def get_information(session, args):
    results = {}
    with OperationLocker():
        devices = _list_devices()
        for device in devices:
            cmd = run_command(["smartctl", "-j", "-a", "-d", device['type'], device['name']], check=False)
            # We use the name + type as a key because we can have several megaraid with the same name.
            # So we use the type to differenciate them.
            results[device['name'] + ":" + device['type']] = json.loads(cmd['stdout'])
        return json.dumps(results)

@error_wrapped
def get_health(session, args):
    results = {}
    with OperationLocker():
        devices = _list_devices()
        for device in devices:
            cmd = run_command(["smartctl", "-j", "-H", "-d", device['type'], device['name']], check=False)
            json_output = json.loads(cmd['stdout'])
            if json_output['smart_status']['passed']:
                results[device['name'] + ":" + device['type']] = "PASSED"
            else:
                results[device['name'] + ":" + device['type']] = "FAILED"
        return json.dumps(results)


_LOGGER = configure_logging('smartctl')
if __name__ == "__main__":
    XenAPIPlugin.dispatch({
        'information': get_information,
        'health': get_health
    })
