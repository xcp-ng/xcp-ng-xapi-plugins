#!/usr/bin/env python
# -*- coding: utf-8 -*-

import errno
import json
import subprocess
import sys

import XenAPIPlugin

sys.path.append('.')
from xcpngutils import configure_logging, run_command


# returns a JSON dict {<poolname>: {mountpoint: <mountpoint>, ...}}
# xe host-call-plugin host-uuid=<UUID> plugin=zfs.py fn=list_zfs_pools
def get_hyperthreading(session, args):
    try:
        result = run_command(['xl', 'info', 'threads_per_core'])
        _LOGGER.info(result)
        lines = result['stdout'].splitlines()

        return json.dumps(int(lines[0]) > 1)
    except OSError as e:
        if e.errno == errno.ENOENT:
            return json.dumps({})
        else:
            raise e


_LOGGER = configure_logging('pyperthreading')
if __name__ == "__main__":
    XenAPIPlugin.dispatch({
        'get_hyperthreading': get_hyperthreading
    })
