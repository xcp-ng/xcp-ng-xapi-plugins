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
        disks.append(line.split()[0])
    return disks

@error_wrapped
def _list_raids():
    raids = []
    result = run_command(['smartctl', '--scan'])
    for line in result['stdout'].splitlines():
        disks.append(line.split()[2])
    return raids

@error_wrapped
def get_information(session, args):
    results = {}
    raids = {}
    i = 0
    with OperationLocker():
        disks = _list_disks()
        raids = _list_raids()
        for disk in disks:
            cmd = run_command(["smartctl", "-j", "-a", "-d", raids[i], disk], check=False)
            results[disk] = json.loads(cmd['stdout'])
            i = i + 1
        return json.dumps(results)

@error_wrapped
def get_health(session, args):
    results = {}
    raids = {}
    i = 0
    with OperationLocker():
        disks = _list_disks()
        raids = _list_raids()
        for disk in disks:
            cmd = run_command(["smartctl", "-j", "-H", "-d", raids[i], disk])
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
