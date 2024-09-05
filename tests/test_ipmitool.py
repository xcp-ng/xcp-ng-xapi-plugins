import json
import mock
import pytest
import XenAPIPlugin
from xcpngutils import ProcessException

from ipmitool import is_ipmi_device_available, sensor_data, sensor_info, ipmi_lan

ipmitool_sdr_list = """
SEL              | Not Readable      | ns
Intrusion        | 0x00              | ok
Fan1A            | 4920 RPM          | ok
Fan2A            | 4920 RPM          | ok
Fan3A            | 4920 RPM          | ok
Fan4A            | 4680 RPM          | ok
Fan5A            | 4920 RPM          | ok
Fan6A            | 4920 RPM          | ok
Inlet Temp       | 24 degrees C      | ok
Exhaust Temp     | 35 degrees C      | ok
Temp             | 45 degrees C      | ok
Temp             | 42 degrees C      | ok
"""

ipmitool_sdr_list_expected = [
    {"name": "SEL", "value": "Not Readable", "event": "ns"},
    {"name": "Intrusion", "value": "0x00", "event": "ok"},
    {"name": "Fan1A", "value": "4920 RPM", "event": "ok"},
    {"name": "Fan2A", "value": "4920 RPM", "event": "ok"},
    {"name": "Fan3A", "value": "4920 RPM", "event": "ok"},
    {"name": "Fan4A", "value": "4680 RPM", "event": "ok"},
    {"name": "Fan5A", "value": "4920 RPM", "event": "ok"},
    {"name": "Fan6A", "value": "4920 RPM", "event": "ok"},
    {"name": "Inlet Temp", "value": "24 degrees C", "event": "ok"},
    {"name": "Exhaust Temp", "value": "35 degrees C", "event": "ok"},
    {"name": "Temp", "value": "45 degrees C", "event": "ok"},
    {"name": "Temp", "value": "42 degrees C", "event": "ok"},
]

ipmitool_sdr_fan1 = """
Sensor ID              : Fan1A (0x30)
 Entity ID             : 7.1 (System Board)
 Sensor Type (Threshold)  : Fan (0x04)
 Sensor Reading        : 4920 (+/- 120) RPM
 Status                : ok
 Nominal Reading       : 10080.000
 Normal Minimum        : 16680.000
 Normal Maximum        : 23640.000
 Lower critical        : 720.000
 Lower non-critical    : 840.000
 Positive Hysteresis   : 120.000
 Negative Hysteresis   : 120.000
 Minimum sensor range  : Unspecified
 Maximum sensor range  : Unspecified
 Event Message Control : Per-threshold
 Readable Thresholds   : lcr lnc
 Settable Thresholds   :
 Threshold Read Mask   : lcr lnc
 Assertion Events      :
 Assertions Enabled    : lnc- lcr-
 Deassertions Enabled  : lnc- lcr-
"""

ipmitool_sdr_fan1_expected = [{
    "name": "Fan1A",
    "info": [
        {"name": "Sensor ID", "value": "Fan1A (0x30)"},
        {"name": "Entity ID", "value": "7.1 (System Board)"},
        {"name": "Sensor Type (Threshold)", "value": "Fan (0x04)"},
        {"name": "Sensor Reading", "value": "4920 (+/- 120) RPM"},
        {"name": "Status", "value": "ok"},
        {"name": "Nominal Reading", "value": "10080.000"},
        {"name": "Normal Minimum", "value": "16680.000"},
        {"name": "Normal Maximum", "value": "23640.000"},
        {"name": "Lower critical", "value": "720.000"},
        {"name": "Lower non-critical", "value": "840.000"},
        {"name": "Positive Hysteresis", "value": "120.000"},
        {"name": "Negative Hysteresis", "value": "120.000"},
        {"name": "Minimum sensor range", "value": "Unspecified"},
        {"name": "Maximum sensor range", "value": "Unspecified"},
        {"name": "Event Message Control", "value": "Per-threshold"},
        {"name": "Readable Thresholds", "value": "lcr lnc"},
        {"name": "Settable Thresholds", "value": ""},
        {"name": "Threshold Read Mask", "value": "lcr lnc"},
        {"name": "Assertion Events", "value": ""},
        {"name": "Assertions Enabled", "value": "lnc- lcr-"},
        {"name": "Deassertions Enabled", "value": "lnc- lcr-"},
    ],
}]

ipmitool_lan_print = """
Set in Progress         : Set Complete
Auth Type Support       : MD5
Auth Type Enable        : Callback : MD5
                        : User     : MD5
                        : Operator : MD5
                        : Admin    : MD5
                        : OEM      :
IP Address Source       : Static Address
IP Address              : 172.16.1.2
Subnet Mask             : 255.255.254.0
MAC Address             : f8:bc:12:12:13:14
SNMP Community String   : public
IP Header               : TTL=0x40 Flags=0x40 Precedence=0x00 TOS=0x10
BMC ARP Control         : ARP Responses Enabled, Gratuitous ARP Disabled
Gratituous ARP Intrvl   : 2.0 seconds
Default Gateway IP      : 172.16.210.1
Default Gateway MAC     : 00:00:00:00:00:00
Backup Gateway IP       : 0.0.0.0
Backup Gateway MAC      : 00:00:00:00:00:00
802.1q VLAN ID          : Disabled
802.1q VLAN Priority    : 0
RMCP+ Cipher Suites     : 0,1,2,3,4,5,6,7,8,9,10,11,12,13,14
Cipher Suite Priv Max   : Xaaaaaaaaaaaaaa
                        :     X=Cipher Suite Unused
                        :     c=CALLBACK
                        :     u=USER
                        :     o=OPERATOR
                        :     a=ADMIN
                        :     O=OEM
Bad Password Threshold  : Not Available
"""

ipmitool_lan_print_expected = [
    {"name": "IP Address Source", "value": "Static Address"},
    {"name": "IP Address", "value": "172.16.1.2"},
    {"name": "Subnet Mask", "value": "255.255.254.0"},
    {"name": "MAC Address", "value": "f8:bc:12:12:13:14"},
    {
        "name": "BMC ARP Control",
        "value": "ARP Responses Enabled, Gratuitous ARP Disabled",
    },
    {"name": "Default Gateway IP", "value": "172.16.210.1"},
    {"name": "802.1q VLAN ID", "value": "Disabled"},
    {"name": "802.1q VLAN Priority", "value": "0"},
    {"name": "RMCP+ Cipher Suites", "value": "0,1,2,3,4,5,6,7,8,9,10,11,12,13,14"},
]

SENSOR_DATA_CMD = ["ipmitool", "sdr", "list"]
SENSOR_INFO_CMD = ["ipmitool", "sdr", "get", "Fan1A"]
IPMI_LAN_CMD = ["ipmitool", "lan", "print"]

IPMITOOL_NORMAL_ERROR = (
    "Could not open device at /dev/ipmi0 or /dev/ipmi/0 or /dev/ipmidev/0: "
    "No such file or directory"
)
IPMITOOL_ABNORMAL_ERROR = "Unexpected Error!!!"

NORMAL_ERROR_MSG = "IPMI not available"
SENSOR_DATA_ABNORMAL_ERROR_MSG = "Command '{}' failed with code: 1".format(
    SENSOR_DATA_CMD
)
SENSOR_INFO_ABNORMAL_ERROR_MSG = "Command '{}' failed with code: 1".format(
    SENSOR_INFO_CMD
)
IPMI_LAN_ABNORMAL_ERROR_MSG = "Command '{}' failed with code: 1".format(IPMI_LAN_CMD)


@mock.patch("ipmitool.run_command", autospec=True)
class TestIpmitool:
    #####################################################
    # Testing is_ipmi_device_available
    #
    def test_ipmi_device_available(self, run_command):
        # If the command returns then IPMI is available
        run_command.return_value = {"stdout": ""}

        output = is_ipmi_device_available(None, None)
        assert output == json.dumps(True)

    def test_ipmi_device_not_available(self, run_command):
        # If the command failed with a known error the IPMI is not available
        run_command.side_effect = ProcessException(
            1,
            "",
            "",
            IPMITOOL_NORMAL_ERROR,
        )

        output = is_ipmi_device_available(None, None)
        assert output == json.dumps(False)

    def test_ipmi_device_not_available_failed(self, run_command):
        # If the command failed with an unknown error a XenAPIPlugin Failure should be
        # raised
        run_command.side_effect = ProcessException(
            1,
            "",
            "",
            IPMITOOL_ABNORMAL_ERROR,
        )

        with pytest.raises(XenAPIPlugin.Failure) as e:
            _ = is_ipmi_device_available(None, None)

        assert e.value.params[0] == "1"

    #####################################################
    # Testing sensor_data
    #
    def test_sensor_data_success(self, run_command):
        run_command.return_value = {"stdout": ipmitool_sdr_list}

        output = sensor_data(None, None)
        assert output == json.dumps(ipmitool_sdr_list_expected)

    def test_sensor_data_normal_error(self, run_command):
        run_command.side_effect = ProcessException(
            1,
            SENSOR_DATA_CMD,
            "",
            IPMITOOL_NORMAL_ERROR,
        )

        with pytest.raises(XenAPIPlugin.Failure) as e:
            _ = sensor_data(None, None)

        assert e.value.params[0] == "1"
        assert e.value.params[1] == NORMAL_ERROR_MSG

    def test_sensor_data_abnormal_error(self, run_command):
        run_command.side_effect = ProcessException(
            1,
            SENSOR_DATA_CMD,
            "",
            IPMITOOL_ABNORMAL_ERROR,
        )

        # We are expecting the exception to be raised again
        with pytest.raises(XenAPIPlugin.Failure) as e:
            _ = sensor_data(None, None)

        assert e.value.params[0] == "1"
        assert e.value.params[1] == SENSOR_DATA_ABNORMAL_ERROR_MSG

    #####################################################
    # Testing sensor_info
    #
    def test_sensor_info(self, run_command):
        run_command.return_value = {"stdout": ipmitool_sdr_fan1, "stderr": ""}

        output = sensor_info(None, {"sensors": "Fan1A"})
        assert output == json.dumps(ipmitool_sdr_fan1_expected)

    def test_sensor_info_wrong_sensor(self, run_command):
        run_command.return_value = {
            "stdout": ipmitool_sdr_fan1,
            "stderr": "Unable to find sensor",
        }

        # When we try to get info about a sensor and an error occurs we just skip the sensor
        # NOTE: An error log is also generated
        with mock.patch("ipmitool._LOGGER") as mock_logger:
            mock_logger.error = mock.Mock()

            output = sensor_info(None, {"sensors": "Fan1A"})
            assert output == json.dumps([])
            mock_logger.error.assert_called_once_with("Unable to find sensor")

    def test_sensor_info_normal_error(self, run_command):
        run_command.side_effect = ProcessException(
            1,
            SENSOR_INFO_CMD,
            "",
            IPMITOOL_NORMAL_ERROR,
        )

        with pytest.raises(XenAPIPlugin.Failure) as e:
            _ = sensor_info(None, {"sensors": "Fan1A"})

        assert e.value.params[0] == "1"
        assert e.value.params[1] == NORMAL_ERROR_MSG

    def test_sensor_info_abnormal_error(self, run_command):
        run_command.side_effect = ProcessException(
            1,
            SENSOR_INFO_CMD,
            "",
            IPMITOOL_ABNORMAL_ERROR,
        )

        # We are expecting the exception to be raised again
        with pytest.raises(XenAPIPlugin.Failure) as e:
            _ = sensor_info(None, {"sensors": "Fan1A"})

        assert e.value.params[0] == "1"
        assert e.value.params[1] == SENSOR_INFO_ABNORMAL_ERROR_MSG

    #####################################################
    # Testing ipmi_lan
    #
    def test_ipmi_lan(self, run_command):
        run_command.return_value = {"stdout": ipmitool_lan_print}

        output = ipmi_lan(None, None)
        assert output == json.dumps(ipmitool_lan_print_expected)

    def test_ipmi_lan_normal_error(self, run_command):
        run_command.side_effect = ProcessException(
            1,
            IPMI_LAN_CMD,
            "",
            IPMITOOL_NORMAL_ERROR,
        )

        with pytest.raises(XenAPIPlugin.Failure) as e:
            _ = ipmi_lan(None, None)

        assert e.value.params[0] == "1"
        assert e.value.params[1] == NORMAL_ERROR_MSG

    def test_ipmi_lan_abnormal_error(self, run_command):
        run_command.side_effect = ProcessException(
            1,
            IPMI_LAN_CMD,
            "",
            IPMITOOL_ABNORMAL_ERROR,
        )

        # We are expecting the exception to be raised again
        with pytest.raises(XenAPIPlugin.Failure) as e:
            _ = ipmi_lan(None, {"sensors": "Fan1A"})

        assert e.value.params[0] == "1"
        assert e.value.params[1] == IPMI_LAN_ABNORMAL_ERROR_MSG
