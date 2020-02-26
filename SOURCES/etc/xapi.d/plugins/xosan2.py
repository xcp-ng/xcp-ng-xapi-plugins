#!/usr/bin/env python
# -*- coding: utf-8 -*-

# this is a XCP-ng plugin. It goes to /etc/xapi.d/plugins/ with the exec bit set.
# it expects to have the XCP-ng python xapi plugins library installed. (https://github.com/xcp-ng/xcp-ng-xapi-plugins)
# notes: https://gist.github.com/olivierlambert/c05f09221bdb5953c6c1b6f20c6b9f58
# deployment: scp -r SOURCES/etc/xapi.d/plugins/* root@192.168.0.29:/etc/xapi.d/plugins/
import json
import os
import re
import sys
import shlex
import traceback

import XenAPIPlugin

sys.path.append('.')
from xcpngutils import configure_logging, error_wrapped, install_package, raise_plugin_error, run_command
from xcpngutils.filelocker import FileLocker

PACKAGES = {
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

REPO_PACKAGES = ['attr', 'xfsprogs']


def _gluster_cmd(arg_array):
    result = run_command(['gluster', '--mode=script', '--xml', ] + arg_array)
    if result['exit'] != 0:
        raise_plugin_error('-1', str(result), backtrace=traceback.format_exc())
    return result


# those commands will fail if any of those packages is already present.
def install_packages(session, args):
    # REMOVE THIS LINE before merging !!!
    run_command(['rpm', '-e'] + PACKAGES.keys() + REPO_PACKAGES)
    # #######
    result = run_command(['yum', 'install', '-y'] + REPO_PACKAGES)
    if result['exit'] != 0:
        raise_plugin_error('-1', str(result), backtrace=traceback.format_exc())
    result = run_command(['rpm', '-U'] + PACKAGES.values())
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
    return json.dumps(True)


# peers is a Json array of string designating machines (ip address or hostname)
def probe_peers(session, args):
    peers = json.loads(args['peers'])
    for peer in peers:
        _gluster_cmd(['peer', 'probe', peer])
    return json.dumps(True)


def format_partition(session, args):
    device = args['device']
    label = args['label']
    force_arg = ['-f'] if 'force' in args and args['force'] == 'true' else []
    result = run_command(['mkfs.xfs', '-L', label, device] + force_arg)
    if result['exit'] != 0:
        raise_plugin_error('-1', str(result), backtrace=traceback.format_exc())
    return json.dumps(True)


def mount_partition(session, args):
    label = args['label']
    mount_point = args['mountPoint']
    os.mkdir(mount_point)
    with open("/etc/fstab", "a") as fstab:
        fstab.write('LABEL=' + label + '\t' + mount_point + '\txfs\tdefaults\t0\t2\n')
    result = run_command(['mount', mount_point])
    if result['exit'] != 0:
        raise_plugin_error('-1', str(result), backtrace=traceback.format_exc())
    return json.dumps(True)


def list_partitions(session, args):
    result = run_command(['lsblk', '-P', '-b', '-o',
                          'NAME,KNAME,FSTYPE,MOUNTPOINT,LABEL,UUID,PARTUUID,PARTLABEL,RO,RM,MODEL,SERIAL,SIZE,TYPE,VENDOR,PKNAME'])
    if result['exit'] != 0:
        raise_plugin_error('-1', str(result), backtrace=traceback.format_exc())
    # attempt to parse this:
    # NAME="sr0" MAJ:MIN="11:0" RM="1" SIZE="1073741312" RO="0" TYPE="rom" MOUNTPOINT=""
    # NAME="sda" MAJ:MIN="8:0" RM="0" SIZE="107374182400" RO="0" TYPE="disk" MOUNTPOINT=""
    lines = result['stdout'].splitlines()

    def parse_line(line):
        res = {}
        for pair in shlex.split(line):
            split_pair = pair.split('=')
            res[split_pair[0]] = split_pair[1].strip('\"')
        return res

    lines = map(parse_line, lines)
    return json.dumps({l['NAME']: l for l in lines})


def ensure_open_iptables(session, args):
    xosan_part = '''# XOSANv2 - do not edit
-A RH-Firewall-1-INPUT -m conntrack --ctstate NEW -m tcp -p tcp --dport 24007 -j ACCEPT
-A RH-Firewall-1-INPUT -m conntrack --ctstate NEW -m tcp -p tcp --dport 24008 -j ACCEPT
-A RH-Firewall-1-INPUT -m conntrack --ctstate NEW -m tcp -p tcp --dport 49152 -j ACCEPT
-A RH-Firewall-1-INPUT -m conntrack --ctstate NEW -m tcp -p tcp --dport 111 -j ACCEPT
-A RH-Firewall-1-INPUT -m conntrack --ctstate NEW -m udp -p udp --dport 111 -j ACCEPT
# END XOSANv2\n'''
    need_iptable_update = False
    with open('/etc/sysconfig/iptables') as f:
        collected = []
        content = f.readlines()
        regex = re.compile('^\\s*#\\s*XOSANv2')
        found_xosan = [line for line in content if re.match(regex, line)]
        if not found_xosan:
            for l in content:
                if '-j REJECT' in l:
                    collected.append(xosan_part)
                collected.append(l)
            need_iptable_update = True
    if need_iptable_update:
        with open('/etc/sysconfig/iptables', 'w') as f:
            f.write(''.join(collected))
        result = run_command(['systemctl', 'restart', 'iptables.service'])
        if result['exit'] != 0:
            raise_plugin_error('-1', str(result), backtrace=traceback.format_exc())
    return json.dumps(True)


def create_volume(session, args):
    name = args['name']
    arguments = json.loads(args['arguments'])
    _gluster_cmd(['volume', 'create', name] + arguments)
    _gluster_cmd(['volume', 'set', name, 'cluster.granular-entry-heal', 'enable'])
    _gluster_cmd(['volume', 'set', name, 'group', 'virt'])
    _gluster_cmd(['volume', 'set', name, 'features.shard-block-size', '512MB'])
    _gluster_cmd(['volume', 'set', name, 'network.ping-timeout', '5'])
    _gluster_cmd(['volume', 'start', name, ])
    result = _gluster_cmd(['volume', 'set', name, ])
    return json.dumps(result['stdout'])


# TODO observability of gluster volumes and peers

_LOGGER = configure_logging('xosan2')
if __name__ == "__main__":
    XenAPIPlugin.dispatch({
        'install_packages': install_packages,
        'probe_peers': probe_peers,
        'list_partitions': list_partitions,
        'format_partition': format_partition,
        'mount_partition': mount_partition,
        'ensure_open_iptables': ensure_open_iptables,
        'create_volume': create_volume
    })
