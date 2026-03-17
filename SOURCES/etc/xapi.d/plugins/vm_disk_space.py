#!/usr/bin/python3
# -*- coding: utf-8 -*-

import json

import xcp.environ
import XenAPIPlugin

from xcpngutils import error_wrapped
from xcpngutils.xenstore import xs_join, xs_open, xs_read, xs_transaction


def extent_get(xs, tx, extent_path):
    extent_key = xs_read(xs, tx, extent_path)
    extent = {"": extent_key}
    for prop in ["diskid", "length", "offset", "target"]:
        number = xs_read(xs, tx, xs_join(extent_path, prop))
        if number is not None:
            try:
                extent[prop] = int(number)
            except ValueError:
                pass
    return extent


def volume_list_extents(xs, tx, extents_path, extent_ids):
    for extent_id in extent_ids:
        extent_path = xs_join(extents_path, extent_id)
        yield extent_get(xs, tx, extent_path)


def volume_list_mountpoints(xs, tx, mountpoints_path, mountpoint_ids):
    for mountpoint_id in mountpoint_ids:
        mountpoint = xs_read(xs, tx, xs_join(mountpoints_path, mountpoint_id))
        if mountpoint is not None:
            yield mountpoint


def volume_get(xs, tx, volume_path):
    volume = {}

    for prop in ["driveletter", "filesystem", "name", "volume_name"]:
        value = xs_read(xs, tx, xs_join(volume_path, prop))
        if value is not None:
            volume[prop] = value

    for prop in ["free", "size"]:
        number = xs_read(xs, tx, xs_join(volume_path, prop))
        if number is not None:
            try:
                volume[prop] = int(number)
            except ValueError:
                pass

    extents_path = xs_join(volume_path, "extents")
    extent_ids = xs.ls(tx, extents_path)
    if extent_ids is not None:
        volume["extents"] = list(volume_list_extents(xs, tx, extents_path, extent_ids))

    mountpoints_path = xs_join(volume_path, "mount_points")
    mountpoint_ids = xs.ls(tx, mountpoints_path)
    if mountpoint_ids is not None:
        volume["mount_points"] = list(
            volume_list_mountpoints(xs, tx, mountpoints_path, mountpoint_ids)
        )

    return volume


def vm_list_volumes(xs, tx, volumes_path):
    for volume_id in xs.ls(tx, volumes_path) or []:
        volume_path = xs_join(volumes_path, volume_id)
        yield volume_get(xs, tx, volume_path)


def _vm_get_disk_space(session, xs, this_host_uuid, vm_uuid):
    vm_ref = session.xenapi.VM.get_by_uuid(vm_uuid)

    resident_host_ref = session.xenapi.VM.get_resident_on(vm_ref)
    resident_host_uuid = session.xenapi.host.get_uuid(resident_host_ref)
    if resident_host_uuid != this_host_uuid:
        raise Exception("VM not resident on this host")
    domid = int(session.xenapi.VM.get_domid(vm_ref))

    with xs_transaction(xs) as tx:
        dom_path = xs.get_domain_path(domid)
        volumes_path = xs_join(dom_path, "data/volumes")
        return list(vm_list_volumes(xs, tx, volumes_path))


@error_wrapped
def vm_get_disk_space(session, args):
    this_host_uuid = xcp.environ.readInventory()["INSTALLATION_UUID"]
    vm_uuids = args["vm_uuids"].split(",")
    with xs_open() as xs:
        return json.dumps(
            dict(
                (vm_uuid, _vm_get_disk_space(session, xs, this_host_uuid, vm_uuid))
                for vm_uuid in vm_uuids
            )
        )


if __name__ == "__main__":
    XenAPIPlugin.dispatch({"vm_get_disk_space": vm_get_disk_space})
