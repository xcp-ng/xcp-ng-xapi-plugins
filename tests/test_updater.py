#!/usr/bin/env python2

import json
import mock
import pathlib
import pytest
import sys

import mocked_configparser
import mocked_xen_api_plugin
import mocked_filelocker
import mocked_yum

sys.modules['ConfigParser'] = mocked_configparser
sys.modules['XenAPIPlugin'] = mocked_xen_api_plugin
sys.modules['xcpngutils.filelocker'] = mocked_filelocker
sys.modules['yum'] = mocked_yum
sys.path.append(str(pathlib.Path(__file__).parent.resolve()) + '/../SOURCES/etc/xapi.d/plugins')

from updater import check_update, get_proxies, set_proxies, update, REPOS

class TestCheckUpdate:
    def test_check_update(self):
        expected = ' \
            [{"name": "Dummy Package", "version": "0.0.0", "release": "Dummy released", \
            "description": "Lorem ipsum...", "changelog": null, "url": "http://www.example.com/", "size": "0", \
            "license": "GPLv2 and LGPLv2+ and BSD"}]'
        res = check_update(None, None)
        assert json.loads(expected) == json.loads(res)

    @mock.patch('mocked_yum.YumBase.doPackageLists', autospec=True)
    def test_check_update_error(self, doPackageLists):
        doPackageLists.side_effect = [Exception("Error!")]

        with pytest.raises(mocked_xen_api_plugin.Failure) as e:
            check_update(None, None)
        doPackageLists.assert_called_once()
        assert e.value.params[0] == '-1'
        assert e.value.params[1] == 'Error!'

@mock.patch('updater.run_command', autospec=True)
class TestUpdate:
    def test_update(self, run_command):
        run_command.side_effect = [0]

        update(mock.MagicMock(), {})
        run_command.assert_called_once_with(
            ['yum', 'update', '--disablerepo="*"', '--enablerepo=' + ','.join(REPOS), '-y']
        )

    def test_update_with_packages(self, run_command):
        run_command.side_effect = [0]

        packages = 'toto tata titi'
        update(mock.MagicMock(), {'packages': packages})
        run_command.assert_called_once_with(
            ['yum', 'update', '--disablerepo="*"', '--enablerepo=' + ','.join(REPOS), '-y', packages]
        )

    def test_update_error(self, run_command):
        run_command.side_effect = [Exception("Error!")]

        with pytest.raises(mocked_xen_api_plugin.Failure) as e:
            update(mock.MagicMock(), {})
        run_command.assert_called_once_with(
            ['yum', 'update', '--disablerepo="*"', '--enablerepo=' + ','.join(REPOS), '-y']
        )
        assert e.value.params[0] == '-1'
        assert e.value.params[1] == 'Error!'

class TestGetProxies:
    def test_get_proxies(self):
        expected = ' \
            {"repo_yum": "http://user:password@proxy.example.com:3128", "repo_yum_2": "_none_", "repo_yum_3": "_none_"}'
        res = get_proxies(None, None)
        assert json.loads(expected) == json.loads(res)

    @mock.patch('mocked_configparser.ConfigParser.read', autospec=True)
    def test_get_proxies_error(self, read):
        read.side_effect = [Exception("Error!")]

        with pytest.raises(mocked_xen_api_plugin.Failure) as e:
            get_proxies(None, None)
        read.assert_called_once()
        assert e.value.params[0] == '-1'
        assert e.value.params[1] == 'Error!'

class TestSetProxies:
    @mock.patch('builtins.open', mock.mock_open())
    def test_set_proxies(self):
        proxies = ' \
            {"repo_yum": "http://user:password@proxy.example.com:3128", "repo_yum_2": "_none_", "repo_yum_3": "_none_"}'
        res = set_proxies(None, {"proxies": proxies})
        assert res == ""

    @mock.patch('builtins.open', autospec=True)
    def test_set_proxies_error(self, open):
        open.side_effect = [Exception('Error!')]

        proxies = ' \
            {"repo_yum": "http://user:password@proxy.example.com:3128", "repo_yum_2": "_none_", "repo_yum_3": "_none_"}'
        with pytest.raises(mocked_xen_api_plugin.Failure) as e:
            set_proxies(None, {"proxies": proxies})
        open.assert_called_once()
        assert e.value.params[0] == '-1'
        assert e.value.params[1] == 'Error!'
