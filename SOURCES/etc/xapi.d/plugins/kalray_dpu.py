#!/usr/bin/python3
"""XAPI plugin to manage Kalray DPU."""

import json
import XenAPIPlugin # pylint: disable=import-error

from kalray.acs.spdk.rpc.client import HTTPJSONRPCClient, JSONRPCException  # pylint: disable=import-error
from xcpngutils import error_wrapped

class KalrayCmd:
    """Describe a command to be ran on the Kalray DPU."""

    def __init__(self, rpc_name: str, updates: dict):
        self.server = 'localhost'
        self.port = 8080
        self.username = None
        self.password = None
        self.timeout = 60.0
        self.rpc_name = rpc_name
        self.rpc_params = {} # will be updated using add_rpc_params

        for k, v in updates.items():
            if hasattr(self, k):
                setattr(self, k, v)

        # Check that username & password are well set
        if self.username is None:
            raise XenAPIPlugin.Failure("-1", ["'username' is required"])
        if self.password is None:
            raise XenAPIPlugin.Failure("-1", ["'password' is required"])

    def add_rpc_params(self, key, value):
        """Adds a parameter that will be passed to the RPC."""
        self.rpc_params[key] = value

    def call_rpc(self):
        """Do the RPC call."""
        try:
            client = HTTPJSONRPCClient(
                self.server,
                self.port,
                self.timeout,
                self.username,
                self.password,
                log_level="ERROR")
            message = client.call(self.rpc_name, self.rpc_params)
        except JSONRPCException as exc:
            raise XenAPIPlugin.Failure("-1", [exc.message])

        return json.dumps(message)

@error_wrapped
def get_devices(_session, args):
    """Get the list of devices available on the Kalray DPU."""
    kc = KalrayCmd("bdev_get_bdevs", args)
    return kc.call_rpc()

@error_wrapped
def get_raids(_session, args):
    """Get the list of raids available on the Kalray DPU."""
    kc = KalrayCmd("bdev_raid_get_bdevs", args)
    kc.add_rpc_params("category", "all")
    return kc.call_rpc()

@error_wrapped
def get_lvs(_session, args):
    """Get the list of logical volume stores available on the Kalray DPU."""
    kc = KalrayCmd("bdev_lvol_get_lvstores", args)
    return kc.call_rpc()

@error_wrapped
def raid_create(_session, args):
    """Create a raid."""
    kc = KalrayCmd("bdev_raid_create", args)
    try:
        raid_name = args["raid_name"]
        raid_level = args["raid_level"]
        base_bdevs = args["base_bdevs"].split(',')
    except KeyError as msg:
        raise XenAPIPlugin.Failure("-1", [f"Key {msg} is missing"])

    # Check supported raids
    if raid_level not in ["raid0", "raid1", "raid10"]:
        raise XenAPIPlugin.Failure("-1", ["Only raid0, raid1 and raid10 are supported"])

    kc.add_rpc_params("name", raid_name)
    kc.add_rpc_params("raid_level", raid_level)
    kc.add_rpc_params("base_bdevs", base_bdevs)
    kc.add_rpc_params("strip_size_kb", 128)
    kc.add_rpc_params("persist", True)
    kc.add_rpc_params("split_dp", True)
    return kc.call_rpc()

@error_wrapped
def lvs_create(_session, args):
    """Create a logical volume store."""
    kc = KalrayCmd("bdev_lvol_create_lvstore", args)
    try:
        lvs_name = args["lvs_name"]
        bdev_name = args["bdev_name"]
    except KeyError as msg:
        raise XenAPIPlugin.Failure("-1", [f"Key {msg} is missing"])

    kc.add_rpc_params("lvs_name", lvs_name)
    kc.add_rpc_params("bdev_name", bdev_name)

    return kc.call_rpc()

@error_wrapped
def lvol_create(_session, args):
    """Create a new lvol on the Kalray DPU."""
    kc = KalrayCmd("bdev_lvol_create", args)

    try:
        lvol_name = args["lvol_name"]
        lvol_size = int(args["lvol_size_in_bytes"])
        lvs_name = args["lvs_name"]
    except KeyError as msg:
        raise XenAPIPlugin.Failure("-1", [f"Key {msg} is missing"])
    except ValueError as msg:
        raise XenAPIPlugin.Failure("-1", [f"Wrong size: {msg}"])

    kc.add_rpc_params("lvol_name", lvol_name)
    # size is deprecated but Kalray DPU uses an old version of SPDK that
    # does not provide the new 'size_in_mib' parameter.
    kc.add_rpc_params("size", lvol_size)
    kc.add_rpc_params("lvs_name", lvs_name)
    return kc.call_rpc()

@error_wrapped
def lvol_delete(_session, args):
    """Delete the lvol passed as parameter on the Kalray DPU if exists."""
    kc = KalrayCmd("bdev_lvol_delete", args)

    try:
        lvol_name = args["lvol_name"]
    except KeyError as msg:
        raise XenAPIPlugin.Failure("-1", [f"Key {msg} is missing"])

    kc.add_rpc_params("name", lvol_name)
    return kc.call_rpc()

if __name__ == "__main__":
    XenAPIPlugin.dispatch({
        "get_devices": get_devices,
        "get_raids": get_raids,
        "get_lvs": get_lvs,
        "raid_create": raid_create,
        "lvs_create": lvs_create,
        "lvol_create": lvol_create,
        "lvol_delete": lvol_delete,
    })
