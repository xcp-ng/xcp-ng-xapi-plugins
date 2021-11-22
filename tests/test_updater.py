import json
import mock
import pytest
import XenAPIPlugin

from updater import check_update, get_proxies, set_proxies, update, DEFAULT_REPOS

class TestCheckUpdate:
    def test_check_update(self, fs):
        expected = ' \
            [{"name": "Dummy Package", "version": "0.0.0", "release": "Dummy released", \
            "description": "Lorem ipsum...", "changelog": null, "url": "http://www.example.com/", "size": "0", \
            "license": "GPLv2 and LGPLv2+ and BSD"}]'
        res = check_update(None, {})
        assert json.loads(expected) == json.loads(res)

    @mock.patch('updater.yum.YumBase.doPackageLists', autospec=True)
    def test_check_update_error(self, doPackageLists, fs):
        doPackageLists.side_effect = [Exception("Error!")]

        with pytest.raises(XenAPIPlugin.Failure) as e:
            check_update(None, {})
        doPackageLists.assert_called_once()
        assert e.value.params[0] == '-1'
        assert e.value.params[1] == 'Error!'

@mock.patch('updater.run_command', autospec=True)
class TestUpdate:
    def test_update(self, run_command, fs):
        run_command.side_effect = [0]

        update(mock.MagicMock(), {})
        run_command.assert_called_once_with(
            ['yum', 'update', '--disablerepo="*"', '--enablerepo=' + ','.join(DEFAULT_REPOS), '-y']
        )

    def test_update_with_packages(self, run_command, fs):
        run_command.side_effect = [0]

        packages = 'toto tata titi'
        update(mock.MagicMock(), {'packages': packages})
        run_command.assert_called_once_with(
            ['yum', 'update', '--disablerepo="*"', '--enablerepo=' + ','.join(DEFAULT_REPOS), '-y', packages]
        )

    def test_update_error(self, run_command, fs):
        run_command.side_effect = [Exception("Error!")]

        with pytest.raises(XenAPIPlugin.Failure) as e:
            update(mock.MagicMock(), {})
        run_command.assert_called_once_with(
            ['yum', 'update', '--disablerepo="*"', '--enablerepo=' + ','.join(DEFAULT_REPOS), '-y']
        )
        assert e.value.params[0] == '-1'
        assert e.value.params[1] == 'Error!'

    def test_update_with_additional_repos(self, run_command, fs):
        run_command.side_effect = [0]

        repos = DEFAULT_REPOS + ('totoro', 'lalala')
        update(mock.MagicMock(), {'repos': 'totoro, lalala'})
        run_command.assert_called_once_with(
            ['yum', 'update', '--disablerepo="*"', '--enablerepo=' + ','.join(repos), '-y']
        )

    def test_update_with_additional_repos_and_packages(self, run_command, fs):
        run_command.side_effect = [0]

        repos = DEFAULT_REPOS + ('riri', 'fifi', 'loulou')
        packages = 'donald hortense'
        update(mock.MagicMock(), {'repos': 'riri, fifi, loulou', 'packages': packages})
        run_command.assert_called_once_with(
            ['yum', 'update', '--disablerepo="*"', '--enablerepo=' + ','.join(repos), '-y', packages]
        )

class TestGetProxies:
    def test_get_proxies(self, fs):
        expected = ' \
            {"repo_yum": "http://user:password@proxy.example.com:3128", "repo_yum_2": "_none_", "repo_yum_3": "_none_"}'
        res = get_proxies(None, None)
        assert json.loads(expected) == json.loads(res)

    @mock.patch('mocked_configparser.ConfigParser.read', autospec=True)
    def test_get_proxies_error(self, read, fs):
        read.side_effect = [Exception("Error!")]

        with pytest.raises(XenAPIPlugin.Failure) as e:
            get_proxies(None, None)
        read.assert_called_once()
        assert e.value.params[0] == '-1'
        assert e.value.params[1] == 'Error!'

class TestSetProxies:
    def test_set_proxies(self, fs):
        fs.create_dir('/etc/yum.repos.d')

        proxies = ' \
            {"repo_yum": "http://user:password@proxy.example.com:3128", "repo_yum_2": "_none_", "repo_yum_3": "_none_"}'
        res = set_proxies(None, {"proxies": proxies})
        assert res == ""

    @mock.patch('mocked_configparser.ConfigParser.write', autospec=True)
    def test_set_proxies_error(self, write, fs):
        fs.create_dir('/etc/yum.repos.d')

        write.side_effect = [Exception('Error!')]

        proxies = ' \
            {"repo_yum": "http://user:password@proxy.example.com:3128", "repo_yum_2": "_none_", "repo_yum_3": "_none_"}'
        with pytest.raises(XenAPIPlugin.Failure) as e:
            set_proxies(None, {"proxies": proxies})
        write.assert_called_once()
        assert e.value.params[0] == '-1'
        assert e.value.params[1] == 'Error!'
