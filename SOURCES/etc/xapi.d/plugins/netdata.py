#!/usr/bin/env python
# -*- coding: utf-8 -*-

# this is a XCP-ng plugin. It goes to /etc/xapi.d/plugins/ with the exec bit set.
# it expects to have the XCP-ng python xapi plugins library installed. (https://github.com/xcp-ng/xcp-ng-xapi-plugins)

import errno
import json
import os
import shutil
import sys
import urllib2

import XenAPIPlugin

from urlparse import urlparse

sys.path.append('.')
from xcpngutils import configure_logging, error_wrapped, install_package, run_command
from xcpngutils.filelocker import FileLocker


class OperationLocker(FileLocker):
    def _lock(self):
        try:
            # noinspection PyProtectedMember
            super(OperationLocker, self)._lock()
        except Exception:
            raise Exception('The plugin is busy.')


netdata_streaming_content = '''
# do not edit, managed by XCP-ng

[stream]
    # Enable this on slaves, to have them send metrics.
    enabled = yes
    destination = {0}
    api key = {1}
    timeout seconds = 60
    default port = 19999
    send charts matching = *
    buffer size bytes = 1048576
    reconnect delay seconds = 5
    initial clock resync iterations = 60
'''

# xe host-call-plugin host-uuid=a34931d6-fcc5-4f4a-9896-f03ea1ede176 plugin=netdata.py fn=install_netdata args:api_key='c1814542-c066-11e9-a752-080027d5b5e4' args:destination='tcp:192.168.0.34:19999'
# should return JSON true or error
@error_wrapped
def install_netdata(session, args):
    api_key = args['api_key']
    destination = args['destination']
    with OperationLocker():
        install_package('netdata')
        with open("/etc/netdata/stream.conf", "w") as conf_file:
            conf_file.write(
                netdata_streaming_content.format(destination, api_key))
        result = run_command(['service', 'netdata', 'restart'])
        if result['exit'] == 0:
            return json.dumps(True)
        else:
            raise Exception(result)


@error_wrapped
def is_netdata_installed(session, args):
    with OperationLocker():
        result = run_command(['service', 'netdata', 'status'])
        return json.dumps(result['exit'] == 0)


# returns empty string if no streaming is configured
@error_wrapped
def get_netdata_api_key(session, args):
    with OperationLocker():
        try:
            with open("/etc/netdata/stream.conf", "r") as conf_file:
                content = conf_file.readlines()
                content = map(lambda line: line.split('#')[0].strip(), content)
                api_key_line = filter(lambda line: line.startswith('api key'), content)[0]
                api_key = api_key_line.split('=')[1].strip()
                return api_key
        except EnvironmentError as e:
            # if the file doesn't exist, the system is not configured for streaming, return empty string
            if e.errno == errno.ENOENT:
                return ''
            raise e


_LOGGER = configure_logging('netdata')
if __name__ == "__main__":
    XenAPIPlugin.dispatch({
        'is_netdata_installed': is_netdata_installed,
        'install_netdata': install_netdata,
        'get_netdata_api_key': get_netdata_api_key
    })
