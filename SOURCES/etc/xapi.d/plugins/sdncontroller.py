#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import re

import XenAPIPlugin

from xcpngutils import configure_logging, error_wrapped, run_command, raise_plugin_error

OPENFLOW_PROTOCOL = "OpenFlow11"
OVS_OFCTL_CMD = "ovs-ofctl"
VALID_PROTOCOLS = {"tcp", "udp", "icmp", "ip", "arp"}
PROTOCOLS_WITH_PORTS = {"tcp", "udp"}

# error codes
E_PARSER = 1
E_PARAMS = 2
E_BUILDER = 3
E_OVSCALL = 4

def log_and_raise_error(code, desc):
    _LOGGER.error(desc)
    raise_plugin_error(code, desc)

# All functions starting with `parse_` are helper functions compatible with the `Parser` class.
# Each should accept `args` as input and return either (result, None) on success,
# or (None, error_message) on failure.
class Parser:
    def __init__(self, args):
        self.args = args
        self.values = {}
        self.errors = []

    def parse_bridge(self):
        BRIDGE_REGEX = re.compile(r"\b\w+\d+\b")
        bridge = self.args.get("bridge")

        if bridge is None:
            log_and_raise_error(E_PARSER, "bridge parameter is missing")

        if not BRIDGE_REGEX.match(bridge):
            log_and_raise_error(E_PARSER, "'{}' is not a valid bridge name".format(bridge))

        return bridge

    def parse_mac(self):
        MAC_REGEX = re.compile(r"^([0-9A-Fa-f]{2}:){5}([0-9A-Fa-f]{2})$")
        mac_addr = self.args.get("mac")

        if mac_addr is None:
            return None

        if not MAC_REGEX.match(mac_addr) or MAC_REGEX.match(mac_addr).group(0) != mac_addr:
            log_and_raise_error(E_PARSER, "'{}' is not a valid MAC".format(mac_addr))

        return mac_addr

    def parse_iprange(self):
        IPRANGE_REGEX = re.compile(
            r"^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}"
            r"(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(/\d{1,2})?$"
        )
        ip_range = self.args.get("iprange")

        if ip_range is None:
            log_and_raise_error(E_PARSER, "ip range parameter is missing")

        if not IPRANGE_REGEX.match(ip_range):
            log_and_raise_error(E_PARSER, "'{}' is not a valid IP range".format(ip_range))

        return ip_range

    def parse_direction(self):
        direction = self.args.get("direction")

        if direction is None:
            log_and_raise_error(E_PARSER, "direction parameter is missing")

        dir = direction.lower().split("/")
        has_to = "to" in dir
        has_from = "from" in dir

        if not (has_to or has_from):
            log_and_raise_error(E_PARSER, "'{}' is not a valid direction".format(direction))

        return (has_to, has_from)

    def parse_protocol(self):
        protocol = self.args.get("protocol")

        if protocol is None:
            log_and_raise_error(E_PARSER, "protocol parameter is missing")

        protocol = protocol.lower()

        if protocol not in VALID_PROTOCOLS:
            log_and_raise_error(E_PARSER, "'{}' is not a supported protocol".format(protocol))

        return protocol

    def parse_port(self):
        port = self.args.get("port")
        if port is None:
            return None

        try:
            p = int(port)
            if not (0 <= p <= 65535):
                raise ValueError
            return port
        except ValueError:
            log_and_raise_error(E_PARSER, "'{}' is not a valid port".format(port))

    def parse_allow(self):
        allow = self.args.get("allow")
        if allow is None:
            log_and_raise_error(E_PARSER, "allow parameter is missing")

        if allow.lower() not in ["true", "false"]:
            log_and_raise_error(E_PARSER, "allow parameter should be true or false, not '{}'".format(allow))

        if allow.lower() == "true":
            return True

        return False

    def parse_priority(self):
        priority = self.args.get("priority")
        if priority is None:
            return None

        try:
            p = int(priority)
            if not (0 <= p <= 65535):
                raise ValueError
            return priority
        except ValueError:
            log_and_raise_error(E_PARSER, "'{}' is not a valid priority".format(priority))

    def read(self, key, parse_fn, dests=None):
        # parse_fn can return a single value or a tuple of values.
        # In this case we are expecting dests to match the expected
        # returned tuple
        val = parse_fn()

        if dests is not None:
            if not isinstance(val, tuple):
                log_and_raise_error(
                    E_PARSER,
                    "Internal error: parse {}: doesn't return a tuple while dests is set".format(key)
                )

            if len(dests) != len(val):
                log_and_raise_error(
                    E_PARSER,
                    "Internal error: parse {}: dests is {} while {} was expected".format(key, len(dests), len(val))
                )

            for d, v in zip(dests, val):
                self.values[d] = v

            return

        self.values[key] = val

def json_error(name, desc):
    return json.dumps(
        {
            "returncode": 1,
            "command": name,
            "stderr": "".join(desc),
            "stdout": "",
        }
    )

def build_rules_string(args):
    rules = []

    #  tcp,dl_dst=26:bf:26:f0:4f:50,nw_src=192.168.38.0/24,tp_src=22 actions=NORMA
    if args["has_from"]:
        rule = ""
        if "priority" in args and args["priority"]:
            rule += "priority=" + args["priority"] + ","
        rule += args["protocol"].lower()
        if "mac" in args and args["mac"]:
            rule += ",dl_dst=" + args["mac"]
        rule += ",nw_src=" + args["iprange"]
        if "protocol" in args and args["protocol"] in PROTOCOLS_WITH_PORTS:
            rule += ",tp_src=" + args["port"]
        if "allow" in args:
            rule += ",actions=" + ("normal" if args["allow"] else "drop")
        rules += [rule]

    # tcp,in_port=3,dl_src=26:bf:26:f0:4f:50,nw_dst=192.168.38.0/24,tp_dst=2
    if args["has_to"]:
        rule = ""
        if "priority" in args and args["priority"]:
            rule += "priority=" + args["priority"] + ","
        rule += args["protocol"].lower()
        if "mac" in args and args["mac"]:
            rule += ",dl_src=" + args["mac"]
        rule += ",nw_dst=" + args["iprange"]
        if "protocol" in args and args["protocol"] in PROTOCOLS_WITH_PORTS:
            rule += ",tp_dst=" + args["port"]
        if "allow" in args:
            rule += ",actions=" + ("normal" if args["allow"] else "drop")
        rules += [rule]

    return rules

@error_wrapped
def add_rule(_session, args):
    _LOGGER.info("Calling add rule with args {}".format(args))

    try:
        parser = Parser(args)
        parser.read("bridge", parser.parse_bridge)
        parser.read("mac", parser.parse_mac)
        parser.read("direction", parser.parse_direction, dests=["has_to", "has_from"])
        parser.read("protocol", parser.parse_protocol)
        parser.read("iprange", parser.parse_iprange)
        parser.read("port", parser.parse_port)
        parser.read("allow", parser.parse_allow)
        parser.read("priority", parser.parse_priority)
    except XenAPIPlugin.Failure as e:
        log_and_raise_error(E_PARSER, "add_rule: Failed to get parameters: {}".format(e.params[1]))

    if parser.errors:
        log_and_raise_error(E_PARSER, "add_rule: Failed to get parameters: {}".format(parser.errors))

    rule_args = parser.values
    _LOGGER.info("successfully parsed: {}".format(rule_args))

    # sanity check
    if rule_args["protocol"] in PROTOCOLS_WITH_PORTS and not rule_args["port"]:
        log_and_raise_error(E_PARAMS, "add_rule: No port provided, tcp and udp requires one")

    ofctl_cmd = [OVS_OFCTL_CMD, "-O", OPENFLOW_PROTOCOL, "add-flow", rule_args["bridge"]]

    # We can now build the open flow rule
    rules = build_rules_string(rule_args)

    if not rules:
        log_and_raise_error(E_BUILDER, "add_rule: No rules were build")

    for rule in rules:
        cmd = run_command(ofctl_cmd + [rule], check=False)
        if cmd['returncode'] != 0:
            log_and_raise_error(E_OVSCALL, "Error adding rule: %s: %s" % (format(ofctl_cmd + [rule]), cmd['stderr']))
        _LOGGER.info("Added rule: {}".format(ofctl_cmd + [rule]))

    return json.dumps(True)


@error_wrapped
def del_rule(_session, args):
    _LOGGER.info("Calling delete rule with args {}".format(args))

    try:
        parser = Parser(args)
        parser.read("bridge", parser.parse_bridge)
        parser.read("mac", parser.parse_mac)
        parser.read("destination", parser.parse_direction, dests=["has_to", "has_from"])
        parser.read("protocol", parser.parse_protocol)
        parser.read("iprange", parser.parse_iprange)
        parser.read("port", parser.parse_port)
    except XenAPIPlugin.Failure as e:
        log_and_raise_error(E_PARSER, "del_rule: Failed to get parameters: {}".format(e.params[1]))

    if parser.errors:
        log_and_raise_error(E_PARSER, "del_rule: Failed to get parameters: {}".format(parser.errors))

    rule_args = parser.values
    _LOGGER.info("successfully parsed: {}".format(rule_args))

    # sanity check
    if rule_args["protocol"] in PROTOCOLS_WITH_PORTS and not rule_args["port"]:
        log_and_raise_error(E_PARAMS, "del_rule: No port provided, tcp and udp requires one")

    ofctl_cmd = [OVS_OFCTL_CMD, "-O", OPENFLOW_PROTOCOL, "del-flows", rule_args["bridge"]]

    # We can now build the open flow rule
    rules = build_rules_string(rule_args)

    for rule in rules:
        cmd = run_command(ofctl_cmd + [rule], check=False)
        if cmd['returncode']:
            log_and_raise_error(E_OVSCALL, "Error deleting rule: %s: %s" % (format(ofctl_cmd + [rule]), cmd['stderr']))
        _LOGGER.info("Deleted rule: {}".format(ofctl_cmd + [rule]))
    return json.dumps(True)


@error_wrapped
def dump_flows(_session, args):
    _LOGGER.info("Calling dump flows with args {}".format(args))

    parser = Parser(args)
    try:
        bridge = parser.parse_bridge()
    except XenAPIPlugin.Failure as e:
        log_and_raise_error(E_PARSER, "dump_flows: Failed to get parameters: {}".format(e.params[1]))

    ofctl_cmd = [OVS_OFCTL_CMD, "-O", OPENFLOW_PROTOCOL, "dump-flows", bridge]
    cmd = run_command(ofctl_cmd, check=False)
    if cmd['returncode']:
        log_and_raise_error(E_OVSCALL, "Error dumping flows: %s: %s" % (format(ofctl_cmd), cmd['stderr']))
    return json.dumps(cmd)


_LOGGER = configure_logging("sdn-controller")
if __name__ == "__main__":
    XenAPIPlugin.dispatch(
        {
            "add-rule": add_rule,
            "del-rule": del_rule,
            "dump-flows": dump_flows,
        }
    )
