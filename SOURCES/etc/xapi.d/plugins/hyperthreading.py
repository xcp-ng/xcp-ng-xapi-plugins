#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json

import XenAPIPlugin

from xcpngutils import configure_logging, run_command, error_wrapped

@error_wrapped
def get_hyperthreading(session, args):
    result = run_command(['xl', 'info', 'threads_per_core'])
    _LOGGER.info(result)
    lines = result['stdout'].splitlines()
    return json.dumps(int(lines[0]) > 1)


_LOGGER = configure_logging('hyperthreading')
if __name__ == "__main__":
    XenAPIPlugin.dispatch({
        'get_hyperthreading': get_hyperthreading
    })
