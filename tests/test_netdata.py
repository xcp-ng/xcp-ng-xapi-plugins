#!/usr/bin/env python2

import errno
import json
import mock
import pytest
import XenAPIPlugin

from netdata import is_netdata_installed, install_netdata, get_netdata_api_key

@mock.patch('netdata.run_command', autospec=True)
class TestIsIntalled:
    def test_is_netdata_installed(self, run_command, fs):
        run_command.side_effect = ["0"]

        res = is_netdata_installed(None, None)
        assert json.loads(res)
        run_command.assert_called_once_with(['service', 'netdata', 'status'])

    def test_is_netdata_installed_not(self, run_command, fs):
        run_command.side_effect = [Exception('Error!')]

        res = is_netdata_installed(None, None)
        assert not json.loads(res)
        run_command.assert_called_once_with(['service', 'netdata', 'status'])

@mock.patch('netdata.install_package', autospec=True)
@mock.patch('netdata.run_command', autospec=True)
class TestInstall:
    def test_install_netdata(self, run_command, install_package, fs):
        fs.create_dir('/etc/netdata')

        install_package.side_effect = [None]
        run_command.side_effect = [None]

        res = install_netdata(None, {'api_key': 'key', 'destination': 'dest'})
        assert json.loads(res)
        install_package.assert_called_once_with('netdata')
        run_command.assert_called_once_with(['service', 'netdata', 'restart'])

    def test_install_netdata_error_at_install(self, run_command, install_package, fs):
        install_package.side_effect = [Exception('Error!')]

        with pytest.raises(XenAPIPlugin.Failure) as e:
            install_netdata(None, {'api_key': 'key', 'destination': 'dest'})
        install_package.assert_called_once_with('netdata')
        assert run_command.call_count == 0
        assert e.value.params[0] == '-1'
        assert e.value.params[1] == 'Error!'

    def test_install_netdata_error_at_service(self, run_command, install_package, fs):
        fs.create_file('/etc/netdata/stream.conf')

        install_package.side_effect = [None]
        run_command.side_effect = [Exception('Error!')]

        with pytest.raises(XenAPIPlugin.Failure) as e:
            install_netdata(None, {'api_key': 'key', 'destination': 'dest'})
        run_command.assert_called_once_with(['service', 'netdata', 'restart'])
        assert e.value.params[0] == '-1'
        assert e.value.params[1] == 'Error!'

class TestGetApiKey:
    def test_get_netdata_api_key(self, fs):
        fs.create_file('/etc/netdata/stream.conf', contents='''
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
        ''')
        res = get_netdata_api_key(None, None)
        assert res == "040d724e-69e1-11eb-bad1-5a390a90bfd5"

    def test_get_netdata_api_key_file_missing(self, fs):
        res = get_netdata_api_key(None, None)
        assert res == ""

    def test_get_netdata_api_key_open_error(self, fs):
        fs.create_file('/etc/netdata/stream.conf', st_mode=0)
        with pytest.raises(XenAPIPlugin.Failure) as e:
            get_netdata_api_key(None, None)
        assert e.value.params[0] == str(errno.EACCES)
