#!/usr/bin/env python
# -*- coding: utf-8 -*-

import errno
import json
import subprocess
import sys

import XenAPIPlugin

sys.path.append('.')
from vatesutils import configure_logging

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


_LOGGER = configure_logging('zfs')
if __name__ == "__main__":
    XenAPIPlugin.dispatch({
        'list_zfs_pools': list_zfs_pools
    })
