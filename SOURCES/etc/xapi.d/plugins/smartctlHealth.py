#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import sys
import subprocess
import XenAPIPlugin

sys.path.append('.')
from xcpngutils import configure_logging, run_command, error_wrapped
from xcpngutils.operationlocker import OperationLocker

_LOGGER = configure_logging('smartctl')

def list_disks():
    disks = []
    try:
        output = subprocess.check_output(['sudo', 'smartctl', '--scan'], universal_newlines=True)
        lines = output.split('\n')
        for line in lines:
            if line.startswith('/dev/') and not line.startswith('/dev/bus/'):
                disks.append(line.split()[0])
    except subprocess.CalledProcessError:
        print('Error: smartctl command failed.')
    return disks

@error_wrapped
def check_smartctl(a,b):
    with OperationLocker():
        results = {}
        disks = list_disks()
        for disk in disks:
            #print(disk)
            cmd = ["smartctl", "-j", "-H", disk]
            try:
                output = subprocess.check_output(cmd)
                json_output = json.loads(output)
                #print(json_output)
                if json_output['smart_status']['passed']:
                    results[disk] = "PASSED"
                else:
                    results[disk] = "FAILED"
            except subprocess.CalledProcessError as e:
                results[disk] = "Error: " + str(e)
        return json.dumps(results)

if __name__ == "__main__":
    XenAPIPlugin.dispatch({
        'check_smartctl': check_smartctl
    })
