#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import re

import XenAPIPlugin

from xcpngutils import run_command, error_wrapped

LSBLK_COLUMNS = "NAME,KNAME,PKNAME,SIZE,TYPE,RO,MOUNTPOINT"

def _run(cmd):
    """Small helper to run a [cmd, ...] and get its decoded and stripped output."""
    return run_command(cmd)["stdout"].decode("utf-8").strip()

def udev_export_db():
    """Check udev database to extract a dict of {device_name: [list, of, symlinks], ...}."""
    return {
        re.search(r'N: (.*)', device).group(1):
        sorted("/dev/" + path for path in re.findall(r'S: (disk/.*)', device))
        for device in _run(["udevadm", "info", "--export-db"]).split("\n\n")
        if "S: disk/" in device and "N: " in device
    }

@error_wrapped
def list_block_devices(session, args):
    results = []
    blockdevices = {}
    symlinks = udev_export_db()
    for output in _run(["lsblk", "-P", "-b", "-o", LSBLK_COLUMNS]).splitlines():
        device = {
            key.lower(): value.strip('"')
            for key, value in re.findall(r'(\S+)=(".*?"|\S+)', output)
        }
        device["device-id-paths"] = symlinks.get(device["kname"], [])
        if device["pkname"]:
            blockdevices[device["pkname"]].setdefault("children", []).append(device)
        else:
            results.append(device)
        blockdevices[device["kname"]] = device
    return json.dumps({'blockdevices': results})

if __name__ == "__main__":
    XenAPIPlugin.dispatch({"list_block_devices": list_block_devices})
