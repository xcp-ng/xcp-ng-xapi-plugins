#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import subprocess
import sys

import XenAPIPlugin

sys.path.append('.')
from xcpngutils import configure_logging, run_command, error_wrapped
from xcpngutils.operationlocker import OperationLocker

_LOGGER = configure_logging('raid')

# returns {"raid": {"State": "clean", (...)},
#     "volumes": [["0", "8", "0", "0", "active sync", "/dev/sda"], (...)]}
@error_wrapped
def check_raid_pool(session, args):
    device = '/dev/md127'
    with OperationLocker():
        try:
            result = run_command(['mdadm', '--detail', device])
        except subprocess.CalledProcessError:
            # No RAID
            return json.dumps({})

        lines = [line.strip() for line in result['stdout'].splitlines()]
        lines = [line for line in lines if len(line) > 0]
        # remove first line ('/dev/md127:')
        lines = lines[1:]
        # look for the line 'Number   Major   Minor   RaidDevice State'
        footer_index = next(i for i, line in enumerate(lines) if line.startswith('Number'))
        # '1       8       16        1      active sync   /dev/sdb' -> ["1", "8", "16", "1", "active sync", "/dev/sdb"]
        volumes = [[field.strip() for field in line.split('  ') if len(field.strip()) > 0] for line in
                   lines[footer_index + 1:]]
        # 'Version : 1.0' -> {"Version": "1.0"}
        lines = dict([[element.strip() for element in line.split(' : ', 1)] for line in lines[0:footer_index]])
        return json.dumps({'raid': lines, 'volumes': volumes})


if __name__ == "__main__":
    XenAPIPlugin.dispatch({
        'check_raid_pool': check_raid_pool
    })
