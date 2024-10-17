import json
import mock

from ipmitool import sensor_data, sensor_info, ipmi_lan

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

ipmitool_sdr_fan1_expected = [
    {
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
    }
]

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


@mock.patch("ipmitool.run_command", autospec=True)
class TestIpmitool:
    def test_sensor_data(self, run_command):
        run_command.return_value = {"stdout": ipmitool_sdr_list}

        output = sensor_data(None, None)
        assert output == json.dumps(ipmitool_sdr_list_expected)

    def test_sensor_info(self, run_command):
        run_command.return_value = {"stdout": ipmitool_sdr_fan1}

        output = sensor_info(None, {"sensors": "Fan1A"})
        assert output == json.dumps(ipmitool_sdr_fan1_expected)

    def test_ipmi_lan(self, run_command):
        run_command.return_value = {"stdout": ipmitool_lan_print}

        output = ipmi_lan(None, None)
        assert output == json.dumps(ipmitool_lan_print_expected)
