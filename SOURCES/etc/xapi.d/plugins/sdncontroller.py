#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import re

import XenAPIPlugin

from xcpngutils import configure_logging, error_wrapped, run_command, raise_plugin_error

OPENFLOW_PROTOCOL = "OpenFlow11"
OVS_OFCTL_CMD = "ovs-ofctl"
OVS_VSCTL_CMD = "ovs-vsctl"
VALID_PROTOCOLS = {"tcp", "udp", "icmp", "ip", "arp"}
PROTOCOLS_WITH_PORTS = {"tcp", "udp"}
OFPVID_NONE = "0xffff"

# error codes
E_PARSER = 1
E_PARAMS = 2
E_OVSCALL = 3
E_PORTS = 4

# rules names per direction
TO = 0
FROM = 1


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
            log_and_raise_error(
                E_PARSER, "'{}' is not a valid bridge name".format(bridge)
            )

        return bridge

    def parse_mac(self):
        MAC_REGEX = re.compile(r"^([0-9A-Fa-f]{2}:){5}([0-9A-Fa-f]{2})$")
        mac_addr = self.args.get("mac")

        if mac_addr is None:
            return None

        if (
            not MAC_REGEX.match(mac_addr)
            or MAC_REGEX.match(mac_addr).group(0) != mac_addr
        ):
            log_and_raise_error(E_PARSER, "'{}' is not a valid MAC".format(mac_addr))

        return mac_addr

    def parse_iprange(self):
        IPRANGE_REGEX = re.compile(
            r"^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}"
            r"(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(/\d{1,2})?$"
        )
        ip_range = self.args.get("ipRange")

        if ip_range is None:
            log_and_raise_error(E_PARSER, "ipRange parameter is missing")

        if not IPRANGE_REGEX.match(ip_range):
            log_and_raise_error(
                E_PARSER, "'{}' is not a valid IP range".format(ip_range)
            )

        return ip_range

    def parse_direction(self):
        direction = self.args.get("direction")

        if direction is None:
            log_and_raise_error(E_PARSER, "direction parameter is missing")

        dir = direction.lower().split("/")
        has_to = "to" in dir
        has_from = "from" in dir

        if not (has_to or has_from):
            log_and_raise_error(
                E_PARSER, "'{}' is not a valid direction".format(direction)
            )

        return (has_to, has_from)

    def parse_protocol(self):
        protocol = self.args.get("protocol")

        if protocol is None:
            log_and_raise_error(E_PARSER, "protocol parameter is missing")

        protocol = protocol.lower()

        if protocol not in VALID_PROTOCOLS:
            log_and_raise_error(
                E_PARSER, "'{}' is not a supported protocol".format(protocol)
            )

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
            log_and_raise_error(
                E_PARSER,
                "allow parameter should be true or false, not '{}'".format(allow),
            )

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
            log_and_raise_error(
                E_PARSER, "'{}' is not a valid priority".format(priority)
            )

    def read(self, key, parse_fn, dests=None):
        # parse_fn can return a single value or a tuple of values.
        # In this case we are expecting dests to match the expected
        # returned tuple
        val = parse_fn()

        if dests is not None:
            if not isinstance(val, tuple):
                log_and_raise_error(
                    E_PARSER,
                    "Internal error: parse {}: doesn't return a tuple while dests is set".format(
                        key
                    ),
                )

            if len(dests) != len(val):
                log_and_raise_error(
                    E_PARSER,
                    "Internal error: parse {}: dests is {} while {} was expected".format(
                        key, len(dests), len(val)
                    ),
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


def run_vsctl_cmd(args):
    vsctl_cmd = [OVS_VSCTL_CMD] + args
    cmd = run_command(vsctl_cmd, check=False)
    if cmd["returncode"] != 0:
        log_and_raise_error(
            E_OVSCALL,
            "Error running ovs-vsctl command: %s: %s"
            % (format(vsctl_cmd), cmd["stderr"]),
        )
    return cmd["stdout"]


def update_args_from_ovs(args):
    # get parent bridge to apply rules to
    args["parent-bridge"] = run_vsctl_cmd(["br-to-parent", args["bridge"]]).rstrip()

    # get ports names for our actual bridge, be it fake (vlan) or real (no vlan)
    ifs_in_bridge = run_vsctl_cmd(["list-ports", args["bridge"]]).split()
    ifs_in_parent_bridge = run_vsctl_cmd(["list-ports", args["parent-bridge"]]).split()

    # get vlanid if any
    vlanid = run_vsctl_cmd(["get", "port", args["bridge"], "tag"]).rstrip()
    if vlanid != "[]":
        args["vlanid"] = vlanid

    # get the list of all ports and filter them with the ports names to get all interfaces
    ports_j = json.loads(run_vsctl_cmd(["--format=json", "list", "port"]))
    ports = [dict(zip(ports_j["headings"], row)) for row in ports_j["data"]]
    interfaces = []
    parent_ifaces = []
    for port in ports:
        name = port["name"]
        if name in ifs_in_bridge:
            interfaces.append(port["interfaces"])
        if name in ifs_in_parent_bridge:
            parent_ifaces.append(port["interfaces"])
    if len(interfaces) == 0:
        return

    # get the list of all interfaces, filter with what we found previously and get their ofports number
    if_j = json.loads(run_vsctl_cmd(["--format=json", "list", "interface"]))
    ifs = [dict(zip(if_j["headings"], row)) for row in if_j["data"]]
    ofports = []
    for interface in ifs:
        # port 65534 is the internal port for the bridge, we don't want to use it
        if interface["_uuid"] in interfaces and interface["ofport"] != 65534:
            ofports.append(interface["ofport"])

    # second pass on interfaces, find uplinks ofports, that can be:
    # - physical port ethX
    # - physical ports ethX and Y of a bond
    # - the port of a tunnel
    uplinks = []
    for interface in ifs:
        if interface["_uuid"] not in parent_ifaces:
            continue
        name = interface["name"]
        # ignore irrelevant interfaces
        if name.startswith("vif") or name.startswith("xen") or name.startswith("tap"):
            continue
        if (
            interface["type"] == ""
            or interface["type"] == "gre"
            or interface["type"] == "vxlan"
        ):
            uplinks.append(interface["ofport"])
            if interface["ofport"] in ofports:
                ofports.remove(interface["ofport"])

    args["uplinks"] = uplinks
    args["ofports"] = ofports


def build_rules_strings(args):
    rules = []
    if args.get("has_to"):
        if args.get("mac"):
            rules.append(build_rule_string(TO, None, args))
        elif args.get("ofports"):
            for ofport in args["ofports"]:
                rules.append(build_rule_string(TO, ofport, args))
            for ofport in args["uplinks"]:
                rules.append(build_rule_string(TO, ofport, args, uplink=True))

    if args.get("has_from"):
        if args.get("mac"):
            rules.append(build_rule_string(FROM, None, args))
        elif args.get("ofports"):
            for ofport in args["ofports"]:
                rules.append(build_rule_string(FROM, ofport, args))
            for ofport in args["uplinks"]:
                rules.append(build_rule_string(FROM, ofport, args, uplink=True))
    return rules


def build_rule_string(direction, ofport, args, uplink=False):
    # To / From
    rule_parts = {
        "priority": ("priority", "priority"),
        "protocol": (None, None),
        "ofport": ("in_port", "in_port"),
        "mac": ("dl_src", "dl_dst"),
        "iprange": ("nw_dst", "nw_src"),
        "port": ("tp_dst", "tp_src"),
        "allow": ("actions", "actions"),
    }

    rule = ""
    vlanid = OFPVID_NONE
    if args.get("vlanid"):
        vlanid = args["vlanid"]

    if args.get("priority"):
        rule += "priority={}".format(args["priority"]) + ","
    rule += args["protocol"]
    if uplink:
        rule += ",dl_vlan={}".format(vlanid)
    if ofport:
        rule += "," + rule_parts["ofport"][direction] + "={}".format(ofport)
    if args.get("mac"):
        rule += "," + rule_parts["mac"][direction] + "={}".format(args["mac"])
    rule += "," + rule_parts["iprange"][direction] + "={}".format(args["iprange"])
    if args.get("port"):
        rule += "," + rule_parts["port"][direction] + "={}".format(args["port"])
    if "allow" in args:  # optional in case of del_rule
        rule += ",actions={}".format("normal" if args["allow"] else "drop")
    return rule


def run_ofctl_cmd(cmd, bridge, rule):
    ofctl_cmd = [OVS_OFCTL_CMD, "-O", OPENFLOW_PROTOCOL, cmd, bridge, rule]
    cmd = run_command(ofctl_cmd, check=False)
    if cmd["returncode"] != 0:
        log_and_raise_error(
            E_OVSCALL,
            "Error running ovs-ofctl command: %s: %s"
            % (format(ofctl_cmd), cmd["stderr"]),
        )
    _LOGGER.info("Applied rule: {}".format(ofctl_cmd))


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
        log_and_raise_error(
            E_PARSER, "add_rule: Failed to get parameters: {}".format(e.params[1])
        )

    if parser.errors:
        log_and_raise_error(
            E_PARSER, "add_rule: Failed to get parameters: {}".format(parser.errors)
        )

    rule_args = parser.values

    # sanity check
    if rule_args["protocol"] in PROTOCOLS_WITH_PORTS and not rule_args["port"]:
        log_and_raise_error(
            E_PARAMS, "add_rule: No port provided, tcp and udp requires one"
        )

    # update vlanid first, as bridge could be replaced by parent bridge
    update_args_from_ovs(rule_args)
    if rule_args["ofports"] is None:
        log_and_raise_error(
            E_PORTS, "No ports found for bridge: {}".format(rule_args["bridge"])
        )

    # We can now build the open flow rule
    rules = build_rules_strings(rule_args)
    _LOGGER.info("Built rules: {}".format(rules))

    if not rules:
        log_and_raise_error(E_PORTS, "add_rule: No rules were build")

    for rule in rules:
        run_ofctl_cmd("add-flow", rule_args["parent-bridge"], rule)

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
        log_and_raise_error(
            E_PARSER, "del_rule: Failed to get parameters: {}".format(e.params[1])
        )

    if parser.errors:
        log_and_raise_error(
            E_PARSER, "del_rule: Failed to get parameters: {}".format(parser.errors)
        )

    rule_args = parser.values
    _LOGGER.info("successfully parsed: {}".format(rule_args))

    # sanity check
    if rule_args["protocol"] in PROTOCOLS_WITH_PORTS and not rule_args["port"]:
        log_and_raise_error(
            E_PARAMS, "del_rule: No port provided, tcp and udp requires one"
        )

    update_args_from_ovs(rule_args)

    # We can now build the open flow rule
    rules = build_rules_strings(rule_args)
    _LOGGER.info("Built rules: {}".format(rules))

    for rule in rules:
        run_ofctl_cmd("del-flows", rule_args["parent-bridge"], rule)

    return json.dumps(True)


@error_wrapped
def dump_flows(_session, args):
    _LOGGER.info("Calling dump flows with args {}".format(args))

    parser = Parser(args)
    try:
        bridge = parser.parse_bridge()
    except XenAPIPlugin.Failure as e:
        log_and_raise_error(
            E_PARSER, "dump_flows: Failed to get parameters: {}".format(e.params[1])
        )

    ofctl_cmd = [OVS_OFCTL_CMD, "-O", OPENFLOW_PROTOCOL, "dump-flows", bridge]
    cmd = run_command(ofctl_cmd, check=False)
    if cmd["returncode"]:
        log_and_raise_error(
            E_OVSCALL,
            "Error dumping flows: %s: %s" % (format(ofctl_cmd), cmd["stderr"]),
        )
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
