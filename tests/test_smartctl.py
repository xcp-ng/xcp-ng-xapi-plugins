import json
import mock
import pytest
import XenAPIPlugin

from smartctl import get_information, get_health
from smartctl_outputs.smartctl_sda import INFO_SDA, HEALTH_SDA
from smartctl_outputs.smartctl_nvme1 import INFO_NVME1, HEALTH_NVME1
from smartctl_outputs.smartctl_megaraid0 import INFO_MEGARAID0, HEALTH_MEGARAID0
from smartctl_outputs.smartctl_megaraid1 import INFO_MEGARAID1, HEALTH_MEGARAID1
from smartctl_outputs.smartctl_expected_output import EXPECTED_INFO, EXPECTED_HEALTH

LIST_OF_DEVICES = [
    {"name": "/dev/sda", "type": "sat"},
    {"name": "/dev/nvme1", "type": "nvme"},
    {"name": "/dev/bus/0", "type": "megaraid,0"},
    {"name": "/dev/bus/0", "type": "megaraid,1"},
]

@mock.patch("smartctl.run_command", autospec=True)
@mock.patch("smartctl._list_devices", autospec=True)
class TestSmartctl:
    def test_smartctl_error(self, _list_devices, run_command, fs):
        _list_devices.side_effect = Exception("Error!")

        with pytest.raises(XenAPIPlugin.Failure) as e:
            get_health(None, None)
        assert e.value.params[0] == '-1'
        assert e.value.params[1] == 'Error!'

    def test_smartctl_information(self, _list_devices, run_command, fs):
        _list_devices.return_value = LIST_OF_DEVICES
        run_command.side_effect = [
            {"stdout": INFO_SDA},
            {"stdout": INFO_NVME1},
            {"stdout": INFO_MEGARAID0},
            {"stdout": INFO_MEGARAID1},
        ]

        res = get_information(None, None)
        assert json.loads(res) == json.loads(EXPECTED_INFO)

    def test_smartctl_health(self, _list_devices, run_command, fs):
        _list_devices.return_value = LIST_OF_DEVICES
        run_command.side_effect = [
            {"stdout": HEALTH_SDA},
            {"stdout": HEALTH_NVME1},
            {"stdout": HEALTH_MEGARAID0},
            {"stdout": HEALTH_MEGARAID1},
        ]

        res = get_health(None, None)
        assert json.loads(res) == json.loads(EXPECTED_HEALTH)
