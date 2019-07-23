#!/usr/bin/env python
# -*- coding: utf-8 -*-

from functools import wraps
import sys
import json

import XenAPIPlugin

sys.path.append('.')
from xcpngutils import configure_logging, run_command
from xcpngutils.filelocker import FileLocker

_LOGGER = configure_logging('raid')


def lock(*pid_args, **pid_kwargs):
    def wrapper(func):
        @wraps(func)
        def decorator(*args, **kwargs):
            try:
                with FileLocker(*pid_args, **pid_kwargs):
                    return func(*args, **kwargs)
            except Exception as e:
                return json.dumps({'error': str(e)})
        return decorator
    return wrapper


# returns {"status": {"State": "clean", (...)}, "volumes": [["0", "8", "0", "0", "active sync", "/dev/sda"], (...)]}
@lock()
def check_raid_pool(session, args):
    device = '/dev/md127'
    result = run_command(['mdadm', '--detail', device])

    lines = [line.strip() for line in result['stdout'].splitlines()]
    lines = [line for line in lines if len(line) > 0]
    # remove first line ('/dev/md127:')
    lines = lines[1:]
    # look for the line 'Number   Major   Minor   RaidDevice State'
    footer_index = next(i for i, line in enumerate(lines) if line.startswith('Number'))
    # '1       8       16        1      active sync   /dev/sdb' -> ["1", "8", "16", "1", "active sync", "/dev/sdb"]
    volumes = [[field.strip() for field in line.split('  ') if len(field.strip()) > 0] for line in
               lines[footer_index + 1:]]
    # 'Version : 1.0' -> {"Version ": " 1.0"}
    lines = dict([[element.strip() for element in line.split(' : ', 1)] for line in lines[0:footer_index]])
    return json.dumps({'status': lines, 'volumes': volumes})


if __name__ == "__main__":
    XenAPIPlugin.dispatch({
        'check_raid_pool': check_raid_pool
    })
