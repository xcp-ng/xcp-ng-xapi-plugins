#!/usr/bin/env python
# -*- coding: utf-8 -*-

# this is a XCP-ng plugin. It goes to /etc/xapi.d/plugins/ with the exec bit set.
# it expects to have the XCP-ng python xapi plugins library installed. (https://github.com/xcp-ng/xcp-ng-xapi-plugins)

import json
import sys
import traceback

import XenAPIPlugin

sys.path.append('.')
from xcpngutils import configure_logging, error_wrapped, install_package, raise_plugin_error, run_command
from xcpngutils.filelocker import FileLocker

packages = {
    'glusterfs-7.0rc3-0.1.gita92e9e8.el7.x86_64': 'https://nextcloud.vates.fr/index.php/s/PabagxbHY3zAeqK/download?path=%2F&files=glusterfs-7.0rc3-0.1.gita92e9e8.el7.x86_64.rpm',
    'glusterfs-api-7.0rc3-0.1.gita92e9e8.el7.x86_64': 'https://nextcloud.vates.fr/index.php/s/PabagxbHY3zAeqK/download?path=%2F&files=glusterfs-api-7.0rc3-0.1.gita92e9e8.el7.x86_64.rpm',
    'glusterfs-cli-7.0rc3-0.1.gita92e9e8.el7.x86_64': 'https://nextcloud.vates.fr/index.php/s/PabagxbHY3zAeqK/download?path=%2F&files=glusterfs-cli-7.0rc3-0.1.gita92e9e8.el7.x86_64.rpm',
    'glusterfs-client-xlators-7.0rc3-0.1.gita92e9e8.el7.x86_64': 'https://nextcloud.vates.fr/index.php/s/PabagxbHY3zAeqK/download?path=%2F&files=glusterfs-client-xlators-7.0rc3-0.1.gita92e9e8.el7.x86_64.rpm',
    'glusterfs-extra-xlators-7.0rc3-0.1.gita92e9e8.el7.x86_64': 'https://nextcloud.vates.fr/index.php/s/PabagxbHY3zAeqK/download?path=%2F&files=glusterfs-extra-xlators-7.0rc3-0.1.gita92e9e8.el7.x86_64.rpm',
    'glusterfs-fuse-7.0rc3-0.1.gita92e9e8.el7.x86_64': 'https://nextcloud.vates.fr/index.php/s/PabagxbHY3zAeqK/download?path=%2F&files=glusterfs-fuse-7.0rc3-0.1.gita92e9e8.el7.x86_64.rpm',
    'glusterfs-libs-7.0rc3-0.1.gita92e9e8.el7.x86_64': 'https://nextcloud.vates.fr/index.php/s/PabagxbHY3zAeqK/download?path=%2F&files=glusterfs-libs-7.0rc3-0.1.gita92e9e8.el7.x86_64.rpm',
    'glusterfs-server-7.0rc3-0.1.gita92e9e8.el7.x86_64': 'https://nextcloud.vates.fr/index.php/s/PabagxbHY3zAeqK/download?path=%2F&files=glusterfs-server-7.0rc3-0.1.gita92e9e8.el7.x86_64.rpm',
    'python2-gluster-7.0rc3-0.1.gita92e9e8.el7.x86_64': 'https://nextcloud.vates.fr/index.php/s/PabagxbHY3zAeqK/download?path=%2F&files=python2-gluster-7.0rc3-0.1.gita92e9e8.el7.x86_64.rpm',
    'userspace-rcu-0.7.16-1.el7.x86_64': 'https://nextcloud.vates.fr/index.php/s/PabagxbHY3zAeqK/download?path=%2F&files=userspace-rcu-0.7.16-1.el7.x86_64.rpm'}


# those commands will fail if any of those packages is already present.
def install_packages(session, args):
    result = run_command(['yum', 'install', '-y', 'attr'])
    if result['exit'] != 0:
        raise_plugin_error('-1', str(result), backtrace=traceback.format_exc())
    run_command(['rpm', '-e'] + packages.keys())
    result = run_command(['rpm', '-U'] + packages.values())
    if result['exit'] != 0:
        raise_plugin_error('-1', str(result), backtrace=traceback.format_exc())
    result = run_command(['systemctl', 'enable', 'glusterd'])
    if result['exit'] != 0:
        raise_plugin_error('-1', str(result), backtrace=traceback.format_exc())
    result = run_command(['systemctl', 'start', 'glusterd'])
    if result['exit'] != 0:
        raise_plugin_error('-1', str(result), backtrace=traceback.format_exc())
    result = run_command(['iptables', '-F'])
    if result['exit'] != 0:
        raise_plugin_error('-1', str(result), backtrace=traceback.format_exc())
    return 'true'


# peers is a Json array of string designating machines (ip address or hostname)
def probe_peers(session, args):
    peers = json.loads(args['peers'])
    for peer in peers:
        result = run_command(['gluster', 'peer', 'probe', peer])
        if result['exit'] != 0:
            raise_plugin_error('-1', str(result), backtrace=traceback.format_exc())
    return 'true'


def format_partition(session, args):
    device = args['device']

    return 'true'

def list_partitions(session, args):
    result = run_command(['lsblk', '-P', '-b'])
    if result['exit'] != 0:
        raise_plugin_error('-1', str(result), backtrace=traceback.format_exc())
    # attempt to parse this:
    # NAME="sr0" MAJ:MIN="11:0" RM="1" SIZE="1073741312" RO="0" TYPE="rom" MOUNTPOINT=""
    # NAME="sda" MAJ:MIN="8:0" RM="0" SIZE="107374182400" RO="0" TYPE="disk" MOUNTPOINT=""
    lines = result['stdout'].splitlines()

    def parse_line(line):
        res = {}
        # let's hope there are no wonky spaces or double quote in the chain
        line.split(' ')
        for pair in line.split(' '):
            split_pair = pair.split('=')
            res[split_pair[0]] = split_pair[1].strip('\"')
        return res

    lines = map(parse_line, lines)
    return json.dumps(lines)


_LOGGER = configure_logging('xosan2')
if __name__ == "__main__":
    XenAPIPlugin.dispatch({
        'install_packages': install_packages,
        'probe_peers': probe_peers,
        'list_partitions': list_partitions
    })
