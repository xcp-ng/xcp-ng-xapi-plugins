#!/usr/bin/env python
# -*- coding: utf-8 -*-

import errno
import json
import sys

import XenAPIPlugin

sys.path.append('.')
from xcpngutils import configure_logging, run_command, error_wrapped

# returns a JSON dict {<poolname>: {mountpoint: <mountpoint>, ...}}
# xe host-call-plugin host-uuid=<UUID> plugin=zfs.py fn=list_zfs_pools
@error_wrapped
def list_zfs_pools(session, args):
    try:
        command = ['zfs', 'get', '-H', 'all']
        _LOGGER.info('executing command {}...'.format(command))
        result = run_command(command)
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
            raise

_LOGGER = configure_logging('zfs')
if __name__ == "__main__":
    XenAPIPlugin.dispatch({
        'list_zfs_pools': list_zfs_pools
    })
