import json
import mock
import pathlib
import pytest
import sys

import mocked_xen_api_plugin

sys.modules['XenAPIPlugin'] = mocked_xen_api_plugin
sys.path.append(str(pathlib.Path(__file__).parent.resolve()) + '/../SOURCES/etc/xapi.d/plugins')

from hyperthreading import get_hyperthreading
@mock.patch('hyperthreading.run_command', autospec=True)
class TestGetHyperthreading:
    def test_hyperthreading(self, run_command):
        run_command.side_effect = [{"stdout": "1"}, {"stdout": "2"}, {"stdout": "0"}, {"stdout": "-1"}]

        res = get_hyperthreading(None, None)
        assert not json.loads(res)

        res = get_hyperthreading(None, None)
        assert json.loads(res)

        res = get_hyperthreading(None, None)
        assert not json.loads(res)

        res = get_hyperthreading(None, None)
        assert not json.loads(res)

        assert run_command.call_count == 4
        run_command.assert_called_with(['xl', 'info', 'threads_per_core'])

    def test_hyperthreading_error(self, run_command):
        run_command.side_effect = [Exception('Error!')]

        with pytest.raises(mocked_xen_api_plugin.Failure) as e:
            get_hyperthreading(None, None)
        run_command.assert_called_with(['xl', 'info', 'threads_per_core'])
        assert e.value.params[0] == '-1'
        assert e.value.params[1] == 'Error!'
