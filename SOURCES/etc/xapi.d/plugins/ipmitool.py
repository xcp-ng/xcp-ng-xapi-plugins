#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import sys
import XenAPIPlugin

sys.path.append(".")
from xcpngutils import configure_logging, run_command, error_wrapped


@error_wrapped
def sensor_data(session, args):
    sensor_data = []
    output = run_command(["ipmitool", "sdr", "list"])

    for line in output["stdout"].splitlines():
        if not line:
            continue
        sensor_fields = line.split("|")
        sensor_data.append(
            {
                "name": sensor_fields[0].strip(),
                "value": sensor_fields[1].strip(),
                "event": sensor_fields[2].strip(),
            }
        )

    return json.dumps(sensor_data)


@error_wrapped
def sensor_info(session, args):
    sensors_info = []
    sensors = args.get("sensors")

    if not sensors:
        return "{}"

    for sensor in sensors.split(","):
        sensor = sensor.strip()
        info = []
        output = run_command(["ipmitool", "sdr", "get", sensor])

        for line in output["stdout"].splitlines():
            if ":" not in line:
                continue
            name, value = line.split(":", 1)
            info.append(
                {
                    "name": name.strip(),
                    "value": value.strip(),
                }
            )

        sensors_info.append(
            {
                "name": sensor,
                "info": info,
            }
        )

    return json.dumps(sensors_info)


@error_wrapped
def ipmi_lan(session, args):
    lan_info = []
    wanted = [
        "IP Address",
        "Subnet Mask",
        "MAC Address",
        "BMC ARP Control",
        "Default Gateway IP",
        "802.1q VLAN",
        "RMCP+ Cipher Suites",
    ]
    output = run_command(["ipmitool", "lan", "print"])

    for line in output["stdout"].splitlines():
        if any(word in line for word in wanted):
            name, value = line.split(":", 1)
            lan_info.append(
                {
                    "name": name.strip(),
                    "value": value.strip(),
                }
            )

    return json.dumps(lan_info)


_LOGGER = configure_logging("ipmitool-xapi-plugin")
if __name__ == "__main__":
    XenAPIPlugin.dispatch(
        {
            "get_all_sensors": sensor_data,
            "get_sensor": sensor_info,
            "get_ipmi_lan": ipmi_lan,
        }
    )
