# Plugin functions test cases, passed to fixture decorator
# PARAMS are in lists of test cases
# IDS are just a description of the test for pytest, manual matching is needed
import XenAPIPlugin

ADD_RULE_PARAMS = [
    { # no args
        'args': {},
        'exception': {
            'type': XenAPIPlugin.Failure,
            'code': '1',
            'text': "add_rule: Failed to get parameters: bridge parameter is missing"
        },
        'cmd': {
            'returncode': 0,
            'stdout': '',
            'stderr': ''
        },
    },
    { # ip drop
        'args': {
            'bridge': 'xenbr0',
            'direction': 'to',
            'protocol': 'ip',
            'iprange': '1.1.1.1',
            'allow': 'false',
        },
        'exception': None,
        'cmd': {
            'returncode': 0,
            'stdout': '',
            'stderr': ''
        },
    },
    { # subnet tcp 4242 allow
        'args': {
            'bridge': 'xenbr0',
            'direction': 'to',
            'protocol': 'tcp',
            'port': '4242',
            'iprange': '1.1.1.1/24',
            'allow': 'false',
        },
        'exception': None,
        'cmd': {
            'returncode': 0,
            'stdout': '',
            'stderr': ''
        },
    },
    { # tcp no port
        'args': {
            'bridge': 'xenbr0',
            'direction': 'to',
            'protocol': 'tcp',
            'iprange': '1.1.1.1/24',
            'allow': 'false',
        },
        'exception': {
            'type': XenAPIPlugin.Failure,
            'code': '2',
            'text': "add_rule: No port provided, tcp and udp requires one"
        },
        'cmd': {
            'returncode': 0,
            'stdout': '',
            'stderr': ''
        },
    },
    { # failed ovs call
        'args': {
            'bridge': 'xenbr0',
            'direction': 'to',
            'protocol': 'ip',
            'iprange': '1.1.1.1/24',
            'allow': 'false',
        },
        'exception': {
            'type': XenAPIPlugin.Failure,
            'code': '4',
            'text': "Error adding rule: ['ovs-ofctl', '-O', 'OpenFlow11', 'add-flow', 'xenbr0', "
            "'ip,nw_dst=1.1.1.1/24,actions=drop']: fake error"
        },
        'cmd': {
            'returncode': 1,
            'stdout': '',
            'stderr': 'fake error'
        },
    },
]
ADD_RULE_IDS = ["no args", "ip drop", "subnet tcp 4242 allow", "tcp no port",
                "failed ovs call"]


DEL_RULE_PARAMS = [
    {
        'args': {},
        'exception': {
            'type': XenAPIPlugin.Failure,
            'code': '1',
            'text': "del_rule: Failed to get parameters: bridge parameter is missing"
        },
        'cmd': {
            'returncode': 0,
            'stdout': '',
            'stderr': ''
        },
    },
    { # ip drop
        'args': {
            'bridge': 'xenbr0',
            'direction': 'to',
            'protocol': 'ip',
            'iprange': '1.1.1.1',
        },
        'exception': None,
        'cmd': {
            'returncode': 0,
            'stdout': '',
            'stderr': ''
        },
    },
    { # tcp no port
        'args': {
            'bridge': 'xenbr0',
            'direction': 'to',
            'protocol': 'tcp',
            'iprange': '1.1.1.1/24',
            'allow': 'false',
        },
        'exception': {
            'type': XenAPIPlugin.Failure,
            'code': '2',
            'text': "del_rule: No port provided, tcp and udp requires one"
        },
        'cmd': {
            'returncode': 0,
            'stdout': '',
            'stderr': ''
        },
    },
    { # failed ovs call
        'args': {
            'bridge': 'xenbr0',
            'direction': 'to',
            'protocol': 'ip',
            'iprange': '1.1.1.1/24',
        },
        'exception': {
            'type': XenAPIPlugin.Failure,
            'code': '4',
            'text': "Error deleting rule: ['ovs-ofctl', '-O', 'OpenFlow11', 'del-flows', 'xenbr0', "
            "'ip,nw_dst=1.1.1.1/24']: fake error"
        },
        'cmd': {
            'returncode': 1,
            'stdout': '',
            'stderr': 'fake error'
        },
    }
]
DEL_RULE_IDS = ["no args", "ip drop", "tcp no port", "failed ovs call"]


DUMP_FLOWS_PARAMS = [
    { # no args
        'args': {},
        'exception': {
            'type': XenAPIPlugin.Failure,
            'code': '1',
            'text': "dump_flows: Failed to get parameters: bridge parameter is missing"
        },
        'cmd': {
            'returncode': 0,
            'stdout': '',
            'stderr': ''
        },
    },
    { # invalid bridge
        'args': {'bridge': ''},
        'exception': {
            'type': XenAPIPlugin.Failure,
            'code': '1',
            'text': "dump_flows: Failed to get parameters: '' is not a valid bridge name"
        },
        'cmd': {
            'returncode': 0,
            'stdout': '',
            'stderr': ''
        },
    },
    { # xenbr0
        'args': {'bridge': 'xenbr0'},
        'exception': None,
        'cmd': {
            'returncode': 0,
            'stdout': '"OFPST_FLOW reply (OF1.1) (xid=0x2):\n cookie=0x0, duration=10553.194s, table=0, '
            'n_packets=221808, n_bytes=84062096, priority=0 actions=NORMAL\n"',
            'stderr': ''
        },
    },
    { # non-exsting bridge
        'args': {'bridge': 'xapi42'},
        'exception': {
            'type': XenAPIPlugin.Failure,
            'code': '4',
            'text': "Error dumping flows: ['ovs-ofctl', '-O', 'OpenFlow11', 'dump-flows', 'xapi42']: "
            "ovs-ofctl: xapi42 is not a bridge or a socket\n"
        },
        'cmd': {
            'returncode': 1,
            'stdout': '',
            'stderr': 'ovs-ofctl: xapi42 is not a bridge or a socket\n'
        },
    },
]
DUMP_FLOWS_IDS = ["no args", "invalid bridge", "xenbr0", "non-exsting bridge"]
