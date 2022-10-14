#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import sys

import XenAPIPlugin

sys.path.append('.')
from xcpngutils import configure_logging, run_command, error_wrapped
from xcpngutils.operationlocker import OperationLocker

_LOGGER = configure_logging('raid')

@error_wrapped
def check_smartctl(session, args):
    with OperationLocker():
        # for i in /dev/sda, sdb.... do
        result = run_command(['smartctl','-H',device,'--json'])
        # get json, search for   "smart_status": { "passed": true}"
        # Store result: /dev/SDA -> PASSED
        # done
        
if __name__ == "__main__":
    XenAPIPlugin.dispatch({
        'check_smartctl': check_smartctl
    })
