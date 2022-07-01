#!/usr/bin/env python
# -*- coding: utf-8 -*-

import errno
import json
import sys

import XenAPIPlugin

from xcpngutils import configure_logging, run_command, error_wrapped, strtobool, raise_plugin_error

def raise_lvm_error(code, stderr):
    raise_plugin_error('LVM_ERROR({})'.format(code), stderr)

def is_vg_not_found_error(name, error):
    return 'Volume group "{}" not found'.format(name) in error

@error_wrapped
def list_physical_volumes(session, args):
    command = ['pvs', '--noheadings', '--units', 'B', '--nosuffix']
    result = run_command(command)

    # Default format:
    # PV device name
    # VG name
    # Format
    # Attributes
    # Physical size
    # Physical free size

    pvs_result = {}
    for index, line in enumerate(result['stdout'].splitlines()):
        fields = line.split()
        if len(fields) != 6:
            raise Exception('Unexpected pv result at index {}: `{}`.'.format(index, line))

        pv_name = fields[0].strip()

        pv_result = {}
        pv_result['vg_name'] = fields[1].strip()
        pv_result['format'] = fields[2].strip()
        pv_result['attributes'] = fields[3].strip()
        pv_result['capacity'] = int(fields[4])
        pv_result['free'] = int(fields[5])

        pvs_result[pv_name] = pv_result

    return json.dumps(pvs_result)

@error_wrapped
def list_volume_groups(session, args):
    vg_name = args.get('vg_name')
    command = ['vgs', '--noheadings', '--units', 'B', '--nosuffix']
    if vg_name:
        command.append(vg_name)
    result = run_command(command, check=False)
    code = result['returncode']
    if code:
        if vg_name and is_vg_not_found_error(vg_name, result['stderr']):
            return '{}'
        raise_lvm_error(code, result['stderr'])

    # Default format:
    # VG name
    # Number of PVs used
    # Number of LVs in this group
    # Number of snapshots
    # Attributes
    # Total size in bytes
    # Free size in byes

    vgs_result = {}
    for index, line in enumerate(result['stdout'].splitlines()):
        fields = line.split()
        if len(fields) != 7:
            raise Exception('Unexpected vg result at index {}: `{}`.'.format(index, line))

        vg_name = fields[0].strip()

        vg_result = {}
        vg_result['pv_count'] = int(fields[1])
        vg_result['lv_count'] = int(fields[2])
        vg_result['sn_count'] = int(fields[3])
        vg_result['attributes'] = fields[4].strip()
        vg_result['capacity'] = int(fields[5])
        vg_result['free'] = int(fields[6])

        vgs_result[vg_name] = vg_result

    return json.dumps(vgs_result)

@error_wrapped
def list_logical_volumes(session, args):
    vg_name = args.get('vg_name')

    # Use a separator because few fields like "Pool" can be empty.
    # Note: The valid characters for VG and LV names are: a-z A-Z 0-9 + _ . -
    # So we use another char.
    columns = ['-olv_name,vg_name,lv_attr,lv_size,pool_lv']
    command = ['lvs', '--noheadings', '--units', 'B', '--nosuffix', '--separator', ':'] + columns
    if vg_name:
        command.append(vg_name)
    result = run_command(command)

    # Default format:
    # LV name
    # VG name
    # Attributes
    # Logical volume size
    # Pool (if thin is used)
    # Origin
    # Data (in %)
    # Meta (in %)
    # Move
    # Log
    # Cpy%Sync
    # Convert

    lvs_result = {}
    for index, line in enumerate(result['stdout'].splitlines()):
        fields = line.split(':')
        if len(fields) != 5:
            raise Exception('Unexpected lv result at index {}: `{}`.'.format(index, line))

        lv_name = fields[0].strip()

        lv_result = {}
        lv_result['vg_name'] = fields[1].strip()
        lv_result['attributes'] = fields[2].strip()
        lv_result['capacity'] = int(fields[3])
        lv_result['pool'] = fields[4].strip()

        lvs_result[lv_name] = lv_result

    return json.dumps(lvs_result)

@error_wrapped
def create_physical_volume(session, args):
    devices = args['devices'].split(',')
    ignore_fs = strtobool(args.get('ignore_existing_filesystems'))
    force = strtobool(args.get('force'))

    command = ['pvcreate'] + devices
    if force:
        command.extend(('-ff', '-y'))
    elif ignore_fs:
        command.extend(('-f', '-y'))
    else:
        command.append('-qq')

    result = run_command(command, check=False)
    code = result['returncode']
    if code:
        raise_lvm_error(code, result['stderr'])

    return '{}'

@error_wrapped
def create_volume_group(session, args):
    vg_name = args['vg_name']
    devices = args['devices'].split(',')
    force = strtobool(args.get('force'))

    command = ['vgcreate', vg_name] + devices
    if force:
        command.append('-f')

    result = run_command(command, check=False)
    code = result['returncode']
    if code:
        raise_lvm_error(code, result['stderr'])

    return '{}'

@error_wrapped
def destroy_volume_group(session, args):
    vg_name = args['vg_name']
    force = strtobool(args.get('force'))

    command = ['vgremove', vg_name]
    if force:
        # Useful to remove LVMs.
        command.extend(('-f', '-y'))
    else:
        command.append('-qq')

    result = run_command(command, check=False)
    code = result['returncode']
    if code:
        if force and is_vg_not_found_error(vg_name, result['stderr']):
            return '{}'
        raise_lvm_error(code, result['stderr'])

    return '{}'

@error_wrapped
def create_thin_pool(session, args):
    vg_name = args['vg_name']
    lv_name = args['lv_name']

    command = ['lvcreate', '-l', '100%FREE', '-T', '{}/{}'.format(vg_name, lv_name)]
    result = run_command(command, check=False)
    code = result['returncode']
    if code:
        raise_lvm_error(code, result['stderr'])

    return '{}'

_LOGGER = configure_logging('lvm')
if __name__ == "__main__":
    XenAPIPlugin.dispatch({
        'list_physical_volumes': list_physical_volumes,
        'list_volume_groups': list_volume_groups,
        'list_logical_volumes': list_logical_volumes,
        'create_physical_volume': create_physical_volume,
        'create_volume_group': create_volume_group,
        'destroy_volume_group': destroy_volume_group,
        'create_thin_pool': create_thin_pool
    })
