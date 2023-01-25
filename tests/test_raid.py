import json
import mock
import pytest
import subprocess
import XenAPIPlugin

from raid import check_raid_pool

MDADM_DETAIL_CMD = ['mdadm', '--detail', '/dev/md127']

@mock.patch('raid.run_command', autospec=True)
class TestCheckRaidPool:
    def test_raid(self, run_command, fs):
        run_command.return_value = {"stdout": """/dev/md127:
            Version : 1.0
        Creation Time : Wed May 26 14:31:03 2021
            Raid Level : raid1
            Array Size : 62914432 (60.00 GiB 64.42 GB)
        Used Dev Size : 62914432 (60.00 GiB 64.42 GB)
        Raid Devices : 2
        Total Devices : 1
        Persistence : Superblock is persistent

        Update Time : Wed Jul 21 11:18:58 2021
                State : clean, degraded
        Active Devices : 1
    Working Devices : 1
        Failed Devices : 0
        Spare Devices : 0

    Consistency Policy : resync

                Name : localhost:127
                UUID : d42790a9:d65c0409:102ec755:53215d89
                Events : 1076

        Number   Major   Minor   RaidDevice State
        2       8        0        0      active sync   /dev/sda
        -       0        0        1      removed"""}

        expected = ' \
{"raid": {"Consistency Policy": "resync", "Working Devices": "1", "Raid Devices": \
"2", "Raid Level": "raid1", "Creation Time": "Wed May 26 14:31:03 2021", "Used Dev Size": \
"62914432 (60.00 GiB 64.42 GB)", "UUID": "d42790a9:d65c0409:102ec755:53215d89", "Array Size": \
"62914432 (60.00 GiB 64.42 GB)", "Failed Devices": "0", "State": "clean, degraded", "Version": "1.0", "Events": \
"1076", "Persistence": "Superblock is persistent", "Spare Devices": "0", "Name": "localhost:127", "Active Devices": \
"1", "Total Devices": "1", "Update Time": "Wed Jul 21 11:18:58 2021"}, "volumes": [["2", "8", "0", "0", "active sync", \
"/dev/sda"], ["-", "0", "0", "1", "removed"]]}'

        res = check_raid_pool(None, None)
        assert json.loads(res) == json.loads(expected)
        run_command.assert_called_once_with(MDADM_DETAIL_CMD)

    def test_raid_error(self, run_command, fs):
        run_command.side_effect = Exception('Error!')

        with pytest.raises(XenAPIPlugin.Failure) as e:
            check_raid_pool(None, None)
        run_command.assert_called_once_with(MDADM_DETAIL_CMD)
        assert e.value.params[0] == '-1'
        assert e.value.params[1] == 'Error!'

    def test_raid_missing(self, run_command, fs):
        run_command.side_effect = subprocess.CalledProcessError(1, MDADM_DETAIL_CMD, None)
        res = check_raid_pool(None, None)
        assert json.loads(res) == json.loads("{}")
        run_command.assert_called_once_with(MDADM_DETAIL_CMD)

    # TODO:
    # @mock.patch('xcpngutils.run_command', autospec=True)
    # def test_raid_busy(run_command):
