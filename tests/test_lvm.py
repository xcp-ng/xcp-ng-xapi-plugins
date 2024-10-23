import json
import mock
import pytest
import XenAPIPlugin

from lvm import (
    list_physical_volumes,
    list_volume_groups,
    list_logical_volumes,
    create_physical_volume,
    create_volume_group,
    destroy_volume_group,
    create_thin_pool,
)

TESTED_VG_NAME = "linstor_group"
TESTED_DEVICES = "/dev/sdb,/dev/sdc"
TESTED_DEVICE_ARRAY = TESTED_DEVICES.split(",")


@mock.patch("lvm.run_command", autospec=True)
class TestLvmCommands:
    def test_list_physical_volumes(self, run_command):
        run_command.return_value = {
            "stdout": """/dev/sda3  VG_XenStorage-27d94f56-50e0-ed03-fbd3-196796492eb6 lvm2 a--   62797119488 62792925184
            /dev/sdb   linstor_group                                      lvm2 a--  107369988096           0""",  # noqa: E501
            "stderr": """/dev/drbd1000: open failed: Wrong medium type""",
            "returncode": 0,
        }
        volumes = json.loads(list_physical_volumes(None, None))

        expected_volumes = {
            "/dev/sdb": {
                "attributes": "a--",
                "capacity": 107369988096,
                "free": 0,
                "vg_name": "linstor_group",
                "format": "lvm2",
            },
            "/dev/sda3": {
                "attributes": "a--",
                "capacity": 62797119488,
                "free": 62792925184,
                "vg_name": "VG_XenStorage-27d94f56-50e0-ed03-fbd3-196796492eb6",
                "format": "lvm2",
            },
        }

        assert volumes == expected_volumes

    def test_list_volume_groups(self, run_command):
        run_command.return_value = {
            "stdout": """VG_XenStorage-27d94f56-50e0-ed03-fbd3-196796492eb6   1   1   0 wz--n-  62797119488 62792925184
            linstor_group                                                     1   2   0 wz--n- 107369988096           0""",  # noqa: E501
            "stderr": """/dev/drbd1000: open failed: Wrong medium type""",
            "returncode": 0,
        }
        groups = json.loads(list_volume_groups(None, {}))

        expected_groups = {
            "VG_XenStorage-27d94f56-50e0-ed03-fbd3-196796492eb6": {
                "capacity": 62797119488,
                "sn_count": 0,
                "free": 62792925184,
                "pv_count": 1,
                "lv_count": 1,
                "attributes": "wz--n-",
            },
            "linstor_group": {
                "capacity": 107369988096,
                "sn_count": 0,
                "free": 0,
                "pv_count": 1,
                "lv_count": 2,
                "attributes": "wz--n-",
            },
        }

        assert groups == expected_groups

    # Not really a valid test because the result of the VG command is a mock (run_command).
    # The filtering is executed by the `vgs` binary using `vg_name`, it's not our
    # function that filters the VGs.
    # It's better than nothing: we can check the `vgs` command is executed with the `vg_name` in the param list.
    def test_list_volume_groups_with_filter(self, run_command):
        run_command.return_value = {
            "stdout": "linstor_group   1   5   0 wz--n- 107369988096     0",
            "returncode": 0,
        }
        groups = json.loads(list_volume_groups(None, {"vg_name": TESTED_VG_NAME}))

        assert run_command.call_count == 1
        run_command.assert_called_with(
            ["vgs", "--noheadings", "--units", "B", "--nosuffix", TESTED_VG_NAME],
            check=False,
        )

        expected_groups = {
            "linstor_group": {
                "capacity": 107369988096,
                "sn_count": 0,
                "free": 0,
                "pv_count": 1,
                "lv_count": 5,
                "attributes": "wz--n-",
            }
        }

        assert groups == expected_groups

    def test_list_logical_volumes(self, run_command):
        run_command.return_value = {
            "stdout": """MGT:VG_XenStorage-27d94f56-50e0-ed03-fbd3-196796492eb6:-wi-a-----:4194304:
            thin_device:linstor_group:twi---tz--:107160272896:
            xcp-persistent-database_00000:linstor_group:Vwi-aotz--:1077936128:thin_device""",
            "returncode": 0,
        }
        volumes = json.loads(list_logical_volumes(None, {}))

        expected_volumes = {
            "xcp-persistent-database_00000": {
                "attributes": "Vwi-aotz--",
                "capacity": 1077936128,
                "pool": "thin_device",
                "vg_name": "linstor_group",
            },
            "thin_device": {
                "attributes": "twi---tz--",
                "capacity": 107160272896,
                "pool": "",
                "vg_name": "linstor_group",
            },
            "MGT": {
                "attributes": "-wi-a-----",
                "capacity": 4194304,
                "pool": "",
                "vg_name": "VG_XenStorage-27d94f56-50e0-ed03-fbd3-196796492eb6",
            },
        }

        assert volumes == expected_volumes

    # Same comment as: test_list_volume_groups_with_filter.
    def test_list_logical_volumes_with_filter(self, run_command):
        run_command.return_value = {
            "stdout": """thin_device:linstor_group:twi---tz--:107160272896:
            xcp-persistent-database_00000:linstor_group:Vwi-aotz--:1077936128:thin_device""",
            "returncode": 0,
        }
        volumes = json.loads(list_logical_volumes(None, {"vg_name": TESTED_VG_NAME}))

        assert run_command.call_count == 1
        run_command.assert_called_with([
            "lvs",
            "--noheadings",
            "--units",
            "B",
            "--nosuffix",
            "--separator",
            ":",
            "-olv_name,vg_name,lv_attr,lv_size,pool_lv",
            TESTED_VG_NAME,
        ])

        expected_volumes = {
            "xcp-persistent-database_00000": {
                "attributes": "Vwi-aotz--",
                "capacity": 1077936128,
                "pool": "thin_device",
                "vg_name": "linstor_group",
            },
            "thin_device": {
                "attributes": "twi---tz--",
                "capacity": 107160272896,
                "pool": "",
                "vg_name": "linstor_group",
            },
        }

        assert volumes == expected_volumes

    def test_create_physical_volume(self, run_command):
        run_command.return_value = {"returncode": 0}
        assert create_physical_volume(None, {"devices": TESTED_DEVICES}) == "{}"
        run_command.assert_called_with(
            ["pvcreate"] + TESTED_DEVICE_ARRAY + ["-qq"], check=False
        )

    def test_create_physical_volume_with_force(self, run_command):
        run_command.return_value = {"returncode": 0}
        assert (
            create_physical_volume(None, {"devices": TESTED_DEVICES, "force": "1"})
            == "{}"
        )
        run_command.assert_called_with(
            ["pvcreate"] + TESTED_DEVICE_ARRAY + ["-ff", "-y"], check=False
        )

    def test_create_physical_volume_and_ignore_fs(self, run_command):
        run_command.return_value = {"returncode": 0}
        assert (
            create_physical_volume(
                None, {"devices": TESTED_DEVICES, "ignore_existing_filesystems": "1"}
            )
            == "{}"
        )
        run_command.assert_called_with(
            ["pvcreate"] + TESTED_DEVICE_ARRAY + ["-f", "-y"], check=False
        )

    def test_create_volume_group(self, run_command):
        run_command.return_value = {"returncode": 0}
        assert (
            create_volume_group(
                None, {"devices": TESTED_DEVICES, "vg_name": TESTED_VG_NAME}
            )
            == "{}"
        )
        run_command.assert_called_with(
            ["vgcreate", TESTED_VG_NAME] + TESTED_DEVICE_ARRAY, check=False
        )

    def test_create_volume_group_with_force(self, run_command):
        run_command.return_value = {"returncode": 0}
        assert (
            create_volume_group(
                None,
                {"devices": TESTED_DEVICES, "vg_name": TESTED_VG_NAME, "force": "1"},
            )
            == "{}"
        )
        run_command.assert_called_with(
            ["vgcreate", TESTED_VG_NAME] + TESTED_DEVICE_ARRAY + ["-f"], check=False
        )

    def test_destroy_volume_group(self, run_command):
        run_command.return_value = {"returncode": 0}
        assert destroy_volume_group(None, {"vg_name": TESTED_VG_NAME}) == "{}"
        run_command.assert_called_with(["vgremove", TESTED_VG_NAME, "-qq"], check=False)

    def test_destroy_volume_group_with_force(self, run_command):
        run_command.return_value = {"returncode": 0}
        assert (
            destroy_volume_group(None, {"vg_name": TESTED_VG_NAME, "force": "1"})
            == "{}"
        )
        run_command.assert_called_with(
            ["vgremove", TESTED_VG_NAME, "-f", "-y"], check=False
        )

    def test_create_thin_pool(self, run_command):
        volume_name = "logvolume"

        run_command.return_value = {"returncode": 0}
        assert (
            create_thin_pool(None, {"vg_name": TESTED_VG_NAME, "lv_name": volume_name})
            == "{}"
        )
        run_command.assert_called_with(
            [
                "lvcreate",
                "-l",
                "100%FREE",
                "-T",
                "{}/{}".format(TESTED_VG_NAME, volume_name),
            ],
            check=False,
        )
