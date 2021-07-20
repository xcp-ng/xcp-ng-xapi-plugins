#!/usr/bin/env python2

import json
from subprocess import run
import mock
import pathlib
import pytest
import sys

import mocked_xen_api_plugin
import mocked_filelocker

sys.modules['XenAPIPlugin'] = mocked_xen_api_plugin
sys.modules['xcpngutils.filelocker'] = mocked_filelocker
sys.path.append(str(pathlib.Path(__file__).parent.resolve()) + '/../SOURCES/etc/xapi.d/plugins')

from netdata import is_netdata_installed, install_netdata, get_netdata_api_key

@mock.patch('netdata.run_command', autospec=True)
class TestIsIntalled:
    def test_is_netdata_installed(self, run_command):
        run_command.side_effect = ["0"]

        res = is_netdata_installed(None, None)
        assert json.loads(res)
        run_command.assert_called_once_with(['service', 'netdata', 'status'])

    def test_is_netdata_installed_not(self, run_command):
        run_command.side_effect = [Exception('Error!')]

        res = is_netdata_installed(None, None)
        assert not json.loads(res)
        run_command.assert_called_once_with(['service', 'netdata', 'status'])

@mock.patch('netdata.install_package', autospec=True)
class TestInstall:
    @mock.patch('builtins.open', mock.mock_open(read_data='1'))
    @mock.patch('netdata.run_command', autospec=True)
    def test_install_netdata(self, run_command, install_package):
        install_package.side_effect = [None]
        run_command.side_effect = [None]

        res = install_netdata(None, {'api_key': 'key', 'destination': 'dest'})
        assert json.loads(res)
        install_package.assert_called_once_with('netdata')
        run_command.assert_called_once_with(['service', 'netdata', 'restart'])

    @mock.patch('netdata.run_command', autospec=True)
    def test_install_netdata_error_at_install(self, run_command, install_package):
        install_package.side_effect = [Exception('Error!')]

        with pytest.raises(mocked_xen_api_plugin.Failure) as e:
            install_netdata(None, {'api_key': 'key', 'destination': 'dest'})
        install_package.assert_called_once_with('netdata')
        assert run_command.call_count == 0
        assert e.value.params[0] == '-1'
        assert e.value.params[1] == 'Error!'

    @mock.patch('builtins.open', mock.mock_open(read_data='1'))
    @mock.patch('netdata.run_command', autospec=True)
    def test_install_netdata_error_at_service(self, run_command, install_package):
        install_package.side_effect = [None]
        run_command.side_effect = [Exception('Error!')]

        with pytest.raises(mocked_xen_api_plugin.Failure) as e:
            install_netdata(None, {'api_key': 'key', 'destination': 'dest'})
        run_command.assert_called_once_with(['service', 'netdata', 'restart'])
        assert e.value.params[0] == '-1'
        assert e.value.params[1] == 'Error!'

class TestGetApiKey:
    @mock.patch('builtins.open', mock.mock_open(read_data='''
    # do not edit, managed by XCP-ng

    [stream]
        # Enable this on slaves, to have them send metrics.
        enabled = yes
        destination = tcp:192.168.1.131:19999
        api key = 040d724e-69e1-11eb-bad1-5a390a90bfd5
        timeout seconds = 60
        default port = 19999
        send charts matching = *
        buffer size bytes = 1048576
        reconnect delay seconds = 5
        initial clock resync iterations = 60
    '''))
    def test_get_netdata_api_key(self):
        res = get_netdata_api_key(None, None)
        assert res == "040d724e-69e1-11eb-bad1-5a390a90bfd5"

    def test_get_netdata_api_key_file_missing(self):
        res = get_netdata_api_key(None, None)
        assert res == ""

    @mock.patch('builtins.open', autospec=True)
    def test_get_netdata_api_key_error(self, open):
        open.side_effect = [Exception("Error!")]

        with pytest.raises(mocked_xen_api_plugin.Failure) as e:
            get_netdata_api_key(None, None)
        open.assert_called_once()
        assert e.value.params[0] == '-1'
        assert e.value.params[1] == 'Error!'
