#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import sys
import XenAPIPlugin

sys.path.append(".")
from xcpngutils import (
    configure_logging,
    run_command,
    error_wrapped,
    ProcessException,
    raise_plugin_error,
)


@error_wrapped
def _is_ipmi_available():
    # Try to run a simple command to check if ipmitool works
    # If the command raise an error saying that we cannot open the IPMI device it means
    # that IPMI is not available on the system. So we return False. If we don't know the
    # error we raise it again and it will need to be debugged...
    try:
        _ = run_command(["ipmitool", "chassis", "status"])
    except ProcessException as e:
        if "Could not open device" in e.stderr:
            return False
        raise e

    return True


def is_ipmi_device_available(_session, _args):
    return json.dumps(_is_ipmi_available())


@error_wrapped
def check_ipmi_availability(func):
    def wrapper(*args, **kwargs):
        if not _is_ipmi_available():
            raise_plugin_error(1, "IPMI not available")
        return func(*args, **kwargs)

    return wrapper


@check_ipmi_availability
def sensor_data(_session, _args):
    sensor_data = []
    output = run_command(["ipmitool", "sdr", "list"])

    for line in output["stdout"].splitlines():
        if not line:
            continue
        sensor_fields = line.split("|")
        sensor_data.append({
            "name": sensor_fields[0].strip(),
            "value": sensor_fields[1].strip(),
            "event": sensor_fields[2].strip(),
        })

    return json.dumps(sensor_data)


@check_ipmi_availability
def sensor_info(_session, args):
    sensors_info = []
    sensors = args.get("sensors")

    if not sensors:
        return "{}"

    for sensor in sensors.split(","):
        sensor = sensor.strip()
        info = []
        output = run_command(["ipmitool", "sdr", "get", sensor])

        # If there is an error while getting info about the sensor skip it
        # and report the error.
        if output["stderr"]:
            _LOGGER.error("{}".format(output["stderr"].rstrip()))
            continue

        for line in output["stdout"].splitlines():
            if ":" not in line:
                continue
            name, value = line.split(":", 1)
            info.append({
                "name": name.strip(),
                "value": value.strip(),
            })

        sensors_info.append({
            "name": sensor,
            "info": info,
        })

    return json.dumps(sensors_info)


@check_ipmi_availability
def ipmi_lan(_session, _args):
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
            lan_info.append({
                "name": name.strip(),
                "value": value.strip(),
            })

    return json.dumps(lan_info)


_LOGGER = configure_logging("ipmitool-xapi-plugin")
if __name__ == "__main__":
    XenAPIPlugin.dispatch({
        "is_ipmi_device_available": is_ipmi_device_available,
        "get_all_sensors": sensor_data,
        "get_sensor": sensor_info,
        "get_ipmi_lan": ipmi_lan,
    })
