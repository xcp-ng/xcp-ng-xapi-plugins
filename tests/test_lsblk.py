import json
import mock
import pytest
import XenAPIPlugin

from lsblk import list_block_devices

@mock.patch('lsblk.run_command', autospec=True)
class TestListBlockDevices:
    def test_lsblk(self, run_command):
        run_command.side_effect = [
            {"stdout": b'''NAME="sdb" KNAME="sdb" PKNAME="" SIZE="64424509440" TYPE="disk" RO="0" MOUNTPOINT=""
NAME="sda" KNAME="sda" PKNAME="" SIZE="64424509440" TYPE="disk" RO="0" MOUNTPOINT=""
NAME="sda4" KNAME="sda4" PKNAME="sda" SIZE="536870912" TYPE="part" RO="0" MOUNTPOINT=""
NAME="sda2" KNAME="sda2" PKNAME="sda" SIZE="19327352832" TYPE="part" RO="0" MOUNTPOINT=""
NAME="sda5" KNAME="sda5" PKNAME="sda" SIZE="4294967296" TYPE="part" RO="0" MOUNTPOINT="/var/log"
NAME="sda3" KNAME="sda3" PKNAME="sda" SIZE="19863158272" TYPE="part" RO="0" MOUNTPOINT=""
NAME="XSLocalEXT--1fad55d2--4f07--8145--c78a--297b173e06b0-1fad55d2--4f07--8145--c78a--297b173e06b0" KNAME="dm-0" \
PKNAME="sda3" SIZE="19847446528" TYPE="lvm" RO="0" MOUNTPOINT="/run/sr-mount/1fad55d2-4f07-8145-c78a-297b173e06b0"
NAME="sda1" KNAME="sda1" PKNAME="sda" SIZE="19327352832" TYPE="part" RO="0" MOUNTPOINT="/"
NAME="sda6" KNAME="sda6" PKNAME="sda" SIZE="1073741824" TYPE="part" RO="0" MOUNTPOINT="[SWAP]"'''}]

        expected = ' \
{"blockdevices": [{"kname": "sdb", "name": "sdb", "pkname": "", "mountpoint": "", "ro": "0", "type": \
"disk", "size": "64424509440"}, {"kname": "sda", "name": "sda", "pkname": "", "mountpoint": "", "ro": "0", "type": \
"disk", "children": [{"kname": "sda4", "name": "sda4", "pkname": "sda", "mountpoint": "", "ro": "0", "type": "part", \
"size": "536870912"}, {"kname": "sda2", "name": "sda2", "pkname": "sda", "mountpoint": "", "ro": "0", "type": "part", \
"size": "19327352832"}, {"kname": "sda5", "name": "sda5", "pkname": "sda", "mountpoint": "/var/log", "ro": "0", \
"type": "part", "size": "4294967296"}, {"kname": "sda3", "name": "sda3", "pkname": "sda", "mountpoint": "", "ro": "0", \
"type": "part", "children": [{"kname": "dm-0", "name": \
"XSLocalEXT--1fad55d2--4f07--8145--c78a--297b173e06b0-1fad55d2--4f07--8145--c78a--297b173e06b0", "pkname": "sda3", \
"mountpoint": "/run/sr-mount/1fad55d2-4f07-8145-c78a-297b173e06b0", "ro": "0", "type": "lvm", "size": "19847446528"}], \
"size": "19863158272"}, {"kname": "sda1", "name": "sda1", "pkname": "sda", "mountpoint": "/", "ro": "0", "type": \
"part", "size": "19327352832"}, {"kname": "sda6", "name": "sda6", "pkname": "sda", "mountpoint": "[SWAP]", "ro": "0", \
"type": "part", "size": "1073741824"}], "size": "64424509440"}]}'
        res = list_block_devices(None, None)

        assert json.loads(res) == json.loads(expected)
        run_command.assert_called_once_with(["lsblk", "-P", "-b", "-o", "NAME,KNAME,PKNAME,SIZE,TYPE,RO,MOUNTPOINT"])

    def test_lsblk_error(self, run_command):
        run_command.side_effect = [Exception('Error!')]

        with pytest.raises(XenAPIPlugin.Failure) as e:
            list_block_devices(None, None)
        run_command.assert_called_once_with(
            ["lsblk", "-P", "-b", "-o", "NAME,KNAME,PKNAME,SIZE,TYPE,RO,MOUNTPOINT"]
        )
        assert e.value.params[0] == '-1'
        assert e.value.params[1] == 'Error!'
