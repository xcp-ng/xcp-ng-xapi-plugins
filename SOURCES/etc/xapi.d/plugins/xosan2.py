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

GLUSTER_PACKAGES = ['glusterfs', 'glusterfs-api', 'glusterfs-cli', 'glusterfs-client-xlators',
                    'glusterfs-extra-xlators', 'glusterfs-fuse', 'glusterfs-libs',
                    'glusterfs-server', 'python2-gluster', 'userspace-rcu']
REPO_PACKAGES = ['attr', 'xfsprogs'] + GLUSTER_PACKAGES


def _gluster_cmd(arg_array):
    result = run_command(['gluster', '--mode=script', '--xml', ] + arg_array)
    if result['exit'] != 0:
        raise_plugin_error('-1', str(result), backtrace=traceback.format_exc())
    return result


def check_run(command_array):
    result = run_command(command_array)
    if result['exit'] != 0:
        raise_plugin_error('-1', str(result), backtrace=traceback.format_exc())


# those commands will fail if any of those packages is already present.
def install_packages(_session, _args):
    check_run(['yum', '--verbose', 'install', '-y'] + REPO_PACKAGES)
    check_run(['systemctl', 'enable', 'glusterd'])
    check_run(['systemctl', 'start', 'glusterd'])
    return json.dumps(True)


# peers is a Json array of string designating machines (ip address or hostname)
def probe_peers(_session, args):
    peers = json.loads(args['peers'])
    for peer in peers:
        _gluster_cmd(['peer', 'probe', peer])
    return json.dumps(True)


def format_partition(_session, args):
    device = args['device']
    label = args['label']
    force_arg = ['-f'] if 'force' in args and args['force'] == 'true' else []
    check_run(['mkfs.xfs', '-L', label, device] + force_arg)
    return json.dumps(True)


def mount_partition(_session, args):
    label = args['label']
    mount_point = args['mountPoint']
    os.mkdir(mount_point)
    with open("/etc/fstab", "a") as fstab:
        fstab.write('LABEL=' + label + '\t' + mount_point + '\txfs\tdefaults\t0\t2\n')
    check_run(['mount', mount_point])
    return json.dumps(True)


def list_partitions(_session, _args):
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
    return json.dumps({line['NAME']: line for line in lines})


def ensure_open_iptables(_session, _args):
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
        check_run(['systemctl', 'restart', 'iptables.service'])
    return json.dumps(True)


def create_volume(_session, args):
    name = args['name']
    arguments = json.loads(args['arguments'])
    result = [_gluster_cmd(['volume', 'create', name] + arguments)]
    result += _gluster_cmd(['volume', 'set', name, 'cluster.granular-entry-heal', 'enable'])
    result += _gluster_cmd(['volume', 'set', name, 'group', 'virt'])
    result += _gluster_cmd(['volume', 'set', name, 'features.shard-block-size', '512MB'])
    result += _gluster_cmd(['volume', 'set', name, 'network.ping-timeout', '5'])
    result += _gluster_cmd(['volume', 'start', name, ])
    return json.dumps(result)


def get_generic_info(_session, _args):
    result = {'pool list': _gluster_cmd(['pool', 'list'])['stdout'],
              'volume list': _gluster_cmd(['volume', 'list', ''])['stdout']}
    return json.dumps(result)


def get_volume_info(_session, args):
    volume = args['volume']
    result = {'volume info': _gluster_cmd(['volume', 'info', volume])['stdout'],
              'volume status': _gluster_cmd(['volume', 'status', volume])['stdout'],
              'volume status detail': _gluster_cmd(['volume', 'status', volume, 'detail'])['stdout'],
              'volume status mem': _gluster_cmd(['volume', 'status', volume, 'mem'])['stdout'],
              'volume heal info': _gluster_cmd(['volume', 'heal', volume, 'info'])['stdout'],
              'volume top open': _gluster_cmd(['volume', 'top', volume, 'open'])['stdout'],
              'volume top read': _gluster_cmd(['volume', 'top', volume, 'read'])['stdout'],
              'volume top write': _gluster_cmd(['volume', 'top', volume, 'write'])['stdout'],
              'volume top opendir': _gluster_cmd(['volume', 'top', volume, 'opendir'])['stdout'],
              'volume top readdir': _gluster_cmd(['volume', 'top', volume, 'readdir'])['stdout'],
              }
    return json.dumps(result)


_LOGGER = configure_logging('xosan2')
if __name__ == "__main__":
    XenAPIPlugin.dispatch({
        'install_packages': install_packages,
        'probe_peers': probe_peers,
        'list_partitions': list_partitions,
        'format_partition': format_partition,
        'mount_partition': mount_partition,
        'ensure_open_iptables': ensure_open_iptables,
        'create_volume': create_volume,
        'get_generic_info': get_generic_info,
        'get_volume_info': get_volume_info
    })
