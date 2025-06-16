import mock
import pytest
import XenAPIPlugin

from sdncontroller import (
    Parser,
    add_rule,
    del_rule,
    dump_flows
)

from sdncontroller_test_cases.parser import (
    BRIDGE_PARAMS, BRIDGE_IDS,
    MAC_PARAMS, MAC_IDS,
    IPRANGE_PARAMS, IPRANGE_IDS,
    DIRECTION_PARAMS, DIRECTION_IDS,
    PROTOCOL_PARAMS, PROTOCOL_IDS,
    PORT_PARAMS, PORT_IDS,
    ALLOW_PARAMS, ALLOW_IDS,
    PRIORITY_PARAMS, PRIORITY_IDS
)

from sdncontroller_test_cases.functions import (
    ADD_RULE_PARAMS, ADD_RULE_IDS,
    DEL_RULE_PARAMS, DEL_RULE_IDS,
    DUMP_FLOWS_PARAMS, DUMP_FLOWS_IDS
)

def parser_test(method, params):
    exc = params['exception']
    if exc:
        with pytest.raises(exc['type']) as e:
            ret = method()
        assert e.value.params[0] == exc['code']
        assert e.value.params[1] == exc['text']
    else:
        ret = method()
        assert ret == params['result']

class TestSdnControllerParser:
    @pytest.fixture(params=BRIDGE_PARAMS, ids=BRIDGE_IDS)
    def bridge(self, request):
        return request.param

    def test_parse_bridge(self, bridge):
        p = Parser(bridge['input'])
        parser_test(p.parse_bridge, bridge)

    @pytest.fixture(params=MAC_PARAMS, ids=MAC_IDS)
    def mac(self, request):
        return request.param

    def test_parse_mac(self, mac):
        p = Parser(mac['input'])
        parser_test(p.parse_mac, mac)

    @pytest.fixture(params=IPRANGE_PARAMS, ids=IPRANGE_IDS)
    def iprange(self, request):
        return request.param

    def test_parse_iprange(self, iprange):
        p = Parser(iprange['input'])
        parser_test(p.parse_iprange, iprange)

    @pytest.fixture(params=DIRECTION_PARAMS, ids=DIRECTION_IDS)
    def direction(self, request):
        return request.param

    def test_parse_direction(self, direction):
        p = Parser(direction['input'])
        parser_test(p.parse_direction, direction)

    @pytest.fixture(params=PROTOCOL_PARAMS, ids=PROTOCOL_IDS)
    def protocol(self, request):
        return request.param

    def test_parse_protocol(self, protocol):
        p = Parser(protocol['input'])
        parser_test(p.parse_protocol, protocol)

    @pytest.fixture(params=PORT_PARAMS, ids=PORT_IDS)
    def port(self, request):
        return request.param

    def test_parse_port(self, port):
        p = Parser(port['input'])
        parser_test(p.parse_port, port)

    @pytest.fixture(params=ALLOW_PARAMS, ids=ALLOW_IDS)
    def allow(self, request):
        return request.param

    def test_parse_allow(self, allow):
        p = Parser(allow['input'])
        parser_test(p.parse_allow, allow)

    @pytest.fixture(params=PRIORITY_PARAMS, ids=PRIORITY_IDS)
    def priority(self, request):
        return request.param

    def test_parse_priority(self, priority):
        p = Parser(priority['input'])
        parser_test(p.parse_priority, priority)

@mock.patch("sdncontroller.run_command", autospec=True)
class TestSdnControllerFunctions:
    @pytest.fixture(params=ADD_RULE_PARAMS, ids=ADD_RULE_IDS)
    def rule_to_add(self, request):
        return request.param

    def test_add_rule(self, run_command, rule_to_add):
        run_command.return_value = rule_to_add['cmd']
        exc = rule_to_add['exception']
        if exc:
            with pytest.raises(exc['type']) as e:
                add_rule(None, rule_to_add['args'])
            assert e.value.params[0] == exc['code']
            assert e.value.params[1] == exc['text']
        else:
            add_rule(None, rule_to_add['args'])

    @pytest.fixture(params=DEL_RULE_PARAMS, ids=DEL_RULE_IDS)
    def rule_to_del(self, request):
        return request.param

    def test_del_rule(self, run_command, rule_to_del):
        run_command.return_value = rule_to_del['cmd']
        exc = rule_to_del['exception']
        if exc:
            with pytest.raises(exc['type']) as e:
                del_rule(None, rule_to_del['args'])
            assert e.value.params[0] == exc['code']
            assert e.value.params[1] == exc['text']
        else:
            del_rule(None, rule_to_del['args'])

    @pytest.fixture(params=DUMP_FLOWS_PARAMS, ids=DUMP_FLOWS_IDS)
    def bridge_to_dump(self, request):
        return request.param

    def test_dump_flow(self, run_command, bridge_to_dump):
        run_command.return_value = bridge_to_dump['cmd']
        exc = bridge_to_dump['exception']
        if exc:
            with pytest.raises(exc['type']) as e:
                dump_flows(None, bridge_to_dump['args'])
            assert e.value.params[0] == exc['code']
            assert e.value.params[1] == exc['text']
        else:
            dump_flows(None, bridge_to_dump['args'])
