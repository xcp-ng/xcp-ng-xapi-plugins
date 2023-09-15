import json
import mock
import pytest
import XenAPIPlugin

from smartctl import get_information, get_health

SMARTCTL_HEALTH = """{
  "json_format_version": [
    1,
    0
  ],
  "smartctl": {
    "version": [
      7,
      0
    ],
    "svn_revision": "4883",
    "platform_info": "x86_64-linux-4.19.0+1",
    "build_info": "(local build)",
    "argv": [
      "smartctl",
      "-j",
      "-H",
      "/dev/sda"
    ],
    "exit_status": 0
  },
  "device": {
    "name": "/dev/sda",
    "info_name": "/dev/sda [SAT]",
    "type": "sat",
    "protocol": "ATA"
  },
  "smart_status": {
    "passed": true
  }
}"""

SMARTCTL_HEALTH_EXPECTED = """{
  "/dev/sda": "PASSED"
}"""

SMARTCTL_INFO = """{
  "json_format_version": [
    1,
    0
  ],
  "smartctl": {
    "version": [
      7,
      0
    ],
    "svn_revision": "4883",
    "platform_info": "x86_64-linux-4.19.0+1",
    "build_info": "(local build)",
    "argv": [
      "smartctl",
      "-j",
      "-a",
      "/dev/sda"
    ],
    "exit_status": 0
  }
}"""

SMARTCTL_INFO_EXPECTED = """{
  "/dev/sda": {
    "json_format_version": [1, 0],
    "smartctl": {
      "argv": ["smartctl", "-j", "-a", "/dev/sda"],
      "build_info": "(local build)",
      "exit_status": 0,
      "platform_info": "x86_64-linux-4.19.0+1",
      "svn_revision": "4883",
      "version": [7, 0]
    }
  }
}"""

@mock.patch("smartctl.run_command", autospec=True)
@mock.patch("smartctl._list_disks", autospec=True)
class TestSmartctl:
     def test_smartctl_error(self, _list_disks, run_command, fs):
        _list_disks.side_effect = Exception("Error!")

        with pytest.raises(XenAPIPlugin.Failure) as e:
            get_health(None, None)
        assert e.value.params[0] == '-1'
        assert e.value.params[1] == 'Error!'
        
    def test_smartctl_information(self, _list_disks, run_command, fs):
        _list_disks.return_value = ["/dev/sda"]
        run_command.return_value = {"stdout": SMARTCTL_INFO}

        res = get_information(None, None)
        assert json.loads(res) == json.loads(SMARTCTL_INFO_EXPECTED)

    def test_smartctl_health(self, _list_disks, run_command, fs):
        _list_disks.return_value = ["/dev/sda"]
        run_command.return_value = {"stdout": SMARTCTL_HEALTH}

        res = get_health(None, None)
        assert json.loads(res) == json.loads(SMARTCTL_HEALTH_EXPECTED)
