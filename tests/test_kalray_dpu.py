from kalray_dpu import (
    get_devices,
    get_raids,
    get_lvs,
    raid_create,
    lvs_create,
    lvol_create,
    lvol_delete)

def test_get_devices():
    args = {
        "username": "user",
        "password": "pass",
    }
    get_devices(None, args)

def test_get_raids():
    args = {
        "username": "user",
        "password": "pass",
    }
    get_raids(None, args)

def test_get_lvs():
    args = {
        "username": "user",
        "password": "pass",
    }
    get_lvs(None, args)

def test_raid_create():
    args = {
        "username": "user",
        "password": "pass",
        "raid_name": "raid_test",
        "raid_level": "raid0",
        "base_bdevs": "bdev0,bdev1",
        "strip_size_kb": 128,
        "persist": True,
        "slip_dp": True,
    }
    raid_create(None, args)

def test_lvs_create():
    args = {
        "username": "user",
        "password": "pass",
        "lvs_name": "lvs_test",
        "bdev_name": "raid_test",
    }
    lvs_create(None, args)

def test_lvol_create():
    args = {
        "username": "user",
        "password": "pass",
        "lvol_name": "lvol_test",
        "lvol_size_in_bytes": 1234,
        "lvs_name": "lvs_test",
    }
    lvol_create(None, args)

def test_lvol_delete():
    args = {
        "username": "user",
        "password": "pass",
        "lvol_name": "lvol_test",
    }
    lvol_delete(None, args)
