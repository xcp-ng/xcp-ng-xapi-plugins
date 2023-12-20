#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import sys
import XenAPIPlugin

sys.path.append('.')
from xcpngutils import configure_logging, run_command, error_wrapped
from xcpngutils.operationlocker import OperationLocker

@error_wrapped
def _list_disks():
    disks = []
    result = run_command(['smartctl', '--scan'])
    for line in result['stdout'].splitlines():
        if line.startswith('/dev/') and not line.startswith('/dev/bus/'):
            disks.append(line.split()[0])
    return disks

@error_wrapped
def get_information(session, args):
    results = {}
    with OperationLocker():
        disks = _list_disks()
        for disk in disks:
            cmd = run_command(["smartctl", "-j", "-a", disk], check=False)
            results[disk] = json.loads(cmd['stdout'])
        return json.dumps(results)

@error_wrapped
def get_health(session, args):
    results = {}
    with OperationLocker():
        disks = _list_disks()
        for disk in disks:
            cmd = run_command(["smartctl", "-j", "-H", disk])
            json_output = json.loads(cmd['stdout'])
            if json_output['smart_status']['passed']:
                results[disk] = "PASSED"
            else:
                results[disk] = "FAILED"
        return json.dumps(results)


_LOGGER = configure_logging('smartctl')
if __name__ == "__main__":
    XenAPIPlugin.dispatch({
        'information': get_information,
        'health': get_health
    })
