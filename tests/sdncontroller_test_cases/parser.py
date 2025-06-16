# Parser functions test cases, passed to fixture decorator
# PARAMS are in lists of test cases
# IDS are just a description of the test for pytest, manual matching is needed
import XenAPIPlugin

BRIDGE_PARAMS = [
    {
        'input': {'bridge': 'xenbr0'},
        'result': 'xenbr0',
        'exception': None
    },
    {
        'input': {'bridge': 'xapi0'},
        'result': 'xapi0',
        'exception': None
    },
    {
        'input': {'bridge': ''},
        'result': None,
        'exception': {
            'type': XenAPIPlugin.Failure,
            'code': '1',
            'text': "'' is not a valid bridge name"
        },
    },
    {
        'input': {'bridge': 'test'},
        'result': None,
        'exception': {
            'type': XenAPIPlugin.Failure,
            'code': '1',
            'text': "'test' is not a valid bridge name"
        },
    },
    {
        'input': {'bridge': 'xenbr 0'},
        'result': None,
        'exception': {
            'type': XenAPIPlugin.Failure,
            'code': '1',
            'text': "'xenbr 0' is not a valid bridge name"
        },
    },
    {
        'input': {},
        'result': None,
        'exception': {
            'type': XenAPIPlugin.Failure,
            'code': '1',
            'text': "bridge parameter is missing"
        }
    }
]
BRIDGE_IDS = ["xenbr0", "xapi0", "empty string", "no number", "with space", "no parameters"]


MAC_PARAMS = [
    {
        'input': {'mac': '72:7a:c0:ae:1b:a5'},
        'result': '72:7a:c0:ae:1b:a5',
        'exception': None
    },
    {
        'input': {'mac': '72:7A:C0:AE:1B:A5'},
        'result': '72:7A:C0:AE:1B:A5',
        'exception': None
    },
    {
        'input': {'mac': '72:7z:C0:AE:1B:A5'},
        'result': None,
        'exception': {
            'type': XenAPIPlugin.Failure,
            'code': '1',
            'text': "'72:7z:C0:AE:1B:A5' is not a valid MAC"
        },
    },
    {
        'input': {'mac': ''},
        'result': None,
        'exception': {
            'type': XenAPIPlugin.Failure,
            'code': '1',
            'text': "'' is not a valid MAC"
        },
    },
    {
        'input': {},
        'result': None,
        'exception': None
    }
]
MAC_IDS = ["mac", "MAC", "non hexa mac", "empty mac", "no parameters"]


IPRANGE_PARAMS = [
    {
        'input': {'iprange': '1.1.1.1'},
        'result': '1.1.1.1',
        'exception': None
    },
    {
        'input': {'iprange': '1.1.1.0/24'},
        'result': '1.1.1.0/24',
        'exception': None
    },
    {
        'input': {'iprange': '256.256.256.256'},
        'result': None,
        'exception': {
            'type': XenAPIPlugin.Failure,
            'code': '1',
            'text': "'256.256.256.256' is not a valid IP range"
        },
    },
    {
        'input': {'iprange': ''},
        'result': None,
        'exception': {
            'type': XenAPIPlugin.Failure,
            'code': '1',
            'text': "'' is not a valid IP range",
        },
    },
    {
        'input': {},
        'result': None,
        'exception': {
            'type': XenAPIPlugin.Failure,
            'code': '1',
            'text': "ip range parameter is missing",
        }
    }
]
IPRANGE_IDS = ["ip addr", "ip subnet", "invalid ip", "empty ip", "no parameters"]


DIRECTION_PARAMS = [
    {
        'input': {'direction': 'to'},
        'result': (True, False),
        'exception': None
    },
    {
        'input': {'direction': 'TO'},
        'result': (True, False),
        'exception': None
    },
    {
        'input': {'direction': 'from'},
        'result': (False, True),
        'exception': None
    },
    {
        'input': {'direction': 'FROM'},
        'result': (False, True),
        'exception': None
    },
    {
        'input': {'direction': 'to/from'},
        'result': (True, True),
        'exception': None
    },
    {
        'input': {'direction': 'TO/from'},
        'result': (True, True),
        'exception': None
    },
    {
        'input': {'direction': 'to/FROM'},
        'result': (True, True),
        'exception': None
    },
    {
        'input': {'direction': 'from/to'},
        'result': (True, True),
        'exception': None
    },
    {
        'input': {'direction': ''},
        'result': (None, None),
        'exception': {
            'type': XenAPIPlugin.Failure,
            'code': '1',
            'text': "'' is not a valid direction"
        }
    },
    {
        'input': {'direction': 'aoeui'},
        'result': (None, None),
        'exception': {
            'type': XenAPIPlugin.Failure,
            'code': '1',
            'text': "'aoeui' is not a valid direction"
        }
    },
    {
        'input': {},
        'result': (None, None),
        'exception': {
            'type': XenAPIPlugin.Failure,
            'code': '1',
            'text': "direction parameter is missing"
        }
    }
]

DIRECTION_IDS = ["to", "TO", "from", "FROM", "to/from", "TO/from", "to/FROM", "from/to",
                 "empty direction", "invalid direction", "no parameters"]


PROTOCOL_PARAMS = [
    {
        'input': {'protocol': 'ip'},
        'result': 'ip',
        'exception': None
    },
    {
        'input': {'protocol': 'IP'},
        'result': 'ip',
        'exception': None
    },
    {
        'input': {'protocol': 'tcp'},
        'result': 'tcp',
        'exception': None
    },
    {
        'input': {'protocol': 'TCP'},
        'result': 'tcp',
        'exception': None
    },
    {
        'input': {'protocol': 'udp'},
        'result': 'udp',
        'exception': None
    },
    {
        'input': {'protocol': 'UDP'},
        'result': 'udp',
        'exception': None
    },
    {
        'input': {'protocol': 'arp'},
        'result': 'arp',
        'exception': None
    },
    {
        'input': {'protocol': 'ARP'},
        'result': 'arp',
        'exception': None
    },
    {
        'input': {'protocol': 'icmp'},
        'result': 'icmp',
        'exception': None
    },
    {
        'input': {'protocol': 'ICMP'},
        'result': 'icmp',
        'exception': None
    },
    {
        'input': {'protocol': ''},
        'result': None,
        'exception': {
            'type': XenAPIPlugin.Failure,
            'code': '1',
            'text': "'' is not a supported protocol",
        }
    },
    {
        'input': {'protocol': 'aoeui'},
        'result': None,
        'exception': {
            'type': XenAPIPlugin.Failure,
            'code': '1',
            'text': "'aoeui' is not a supported protocol",
        }
    },
    {
        'input': {},
        'result': None,
        'exception': {
            'type': XenAPIPlugin.Failure,
            'code': '1',
            'text': "protocol parameter is missing",
        }
    }
]
PROTOCOL_IDS = ["ip", "IP", "tcp", "TCP", "udp", "UDP", "arp", "ARP", "icmp",
                "ICMP", "empty string", "invalid protocol", "no parameters"]


PORT_PARAMS = [
    {
        'input': {'port': '4242'},
        'result': '4242',
        'exception': None
    },
    {
        'input': {'port': '0'},
        'result': '0',
        'exception': None
    },
    {
        'input': {'port': '65535'},
        'result': '65535',
        'exception': None
    },
    {
        'input': {'port': '65536'},
        'result': None,
        'exception': {
            'type': XenAPIPlugin.Failure,
            'code': '1',
            'text': "'65536' is not a valid port",
        }
    },
    {
        'input': {'port': '92142'},
        'result': None,
        'exception': {
            'type': XenAPIPlugin.Failure,
            'code': '1',
            'text': "'92142' is not a valid port",
        }
    },
    {
        'input': {'port': 'foo'},
        'result': None,
        'exception': {
            'type': XenAPIPlugin.Failure,
            'code': '1',
            'text': "'foo' is not a valid port",
        }
    },
    {
        'input': {'port': ''},
        'result': None,
        'exception': {
            'type': XenAPIPlugin.Failure,
            'code': '1',
            'text': "'' is not a valid port",
        }
    },
    {
        'input': {},
        'result': None,
        'exception': None
    }
]
PORT_IDS = ["4242", "0", "65535", "65536", "92142", "string", "empty string", "no parameters"]


ALLOW_PARAMS = [
    {
        'input': {'allow': 'true'},
        'result': True,
        'exception': None
    },
    {
        'input': {'allow': 'True'},
        'result': True,
        'exception': None
    },
    {
        'input': {'allow': 'TRUE'},
        'result': True,
        'exception': None
    },
    {
        'input': {'allow': 'false'},
        'result': False,
        'exception': None
    },
    {
        'input': {'allow': 'False'},
        'result': False,
        'exception': None
    },
    {
        'input': {'allow': 'FALSE'},
        'result': False,
        'exception': None
    },
    {
        'input': {'allow': 'bar'},
        'result': None,
        'exception': {
            'type': XenAPIPlugin.Failure,
            'code': '1',
            'text': "allow parameter should be true or false, not 'bar'",
        }
    },
    {
        'input': {'allow': ''},
        'result': None,
        'exception': {
            'type': XenAPIPlugin.Failure,
            'code': '1',
            'text': "allow parameter should be true or false, not ''",
        }
    },
    {
        'input': {},
        'result': None,
        'exception': {
            'type': XenAPIPlugin.Failure,
            'code': '1',
            'text': "allow parameter is missing",
        }
    }
]
ALLOW_IDS = ["true", "True", "TRUE", "false", "False", "FALSE", "bar", "empty string", "no parameters"]


PRIORITY_PARAMS = [
    {
        'input': {'priority': '100'},
        'result': '100',
        'exception': None
    },
    {
        'input': {'priority': '0'},
        'result': '0',
        'exception': None
    },
    {
        'input': {'priority': '65535'},
        'result': '65535',
        'exception': None
    },
    {
        'input': {'priority': '65536'},
        'result': None,
        'exception': {
            'type': XenAPIPlugin.Failure,
            'code': '1',
            'text': "'65536' is not a valid priority",
        }
    },
    {
        'input': {'priority': 'aoeui'},
        'result': None,
        'exception': {
            'type': XenAPIPlugin.Failure,
            'code': '1',
            'text': "'aoeui' is not a valid priority",
        }
    },
    {
        'input': {'priority': ''},
        'result': None,
        'exception': {
            'type': XenAPIPlugin.Failure,
            'code': '1',
            'text': "'' is not a valid priority",
        }
    },
    {
        'input': {},
        'result': None,
        'exception': None,
    }
]
PRIORITY_IDS = ["100", "0", "65535", "65536", "aoeui", "empty string", "no parameters"]
