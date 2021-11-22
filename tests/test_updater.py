from ConfigParser import ConfigParser
import json
import mock
import pytest
import XenAPIPlugin

from updater import check_update, get_proxies, set_proxies, update, DEFAULT_REPOS

# ==============================================================================
# Update.
# ==============================================================================

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
        doPackageLists.side_effect = Exception('Error!')

        with pytest.raises(XenAPIPlugin.Failure) as e:
            check_update(None, {})
        doPackageLists.assert_called_once()
        assert e.value.params[0] == '-1'
        assert e.value.params[1] == 'Error!'

@mock.patch('updater.run_command', autospec=True)
class TestUpdate:
    def test_update(self, run_command, fs):
        run_command.return_value = {}

        update(mock.MagicMock(), {})
        run_command.assert_called_once_with(
            ['yum', 'update', '--disablerepo="*"', '--enablerepo=' + ','.join(DEFAULT_REPOS), '-y']
        )

    def test_update_with_packages(self, run_command, fs):
        run_command.return_value = {}

        packages = 'toto tata titi'
        update(mock.MagicMock(), {'packages': packages})
        run_command.assert_called_once_with(
            ['yum', 'update', '--disablerepo="*"', '--enablerepo=' + ','.join(DEFAULT_REPOS), '-y', packages]
        )

    def test_update_error(self, run_command, fs):
        run_command.side_effect = Exception('Error!')

        with pytest.raises(XenAPIPlugin.Failure) as e:
            update(mock.MagicMock(), {})
        run_command.assert_called_once_with(
            ['yum', 'update', '--disablerepo="*"', '--enablerepo=' + ','.join(DEFAULT_REPOS), '-y']
        )
        assert e.value.params[0] == '-1'
        assert e.value.params[1] == 'Error!'

    def test_update_with_additional_repos(self, run_command, fs):
        run_command.return_value = {}

        repos = DEFAULT_REPOS + ('totoro', 'lalala')
        update(mock.MagicMock(), {'repos': 'totoro, lalala'})
        run_command.assert_called_once_with(
            ['yum', 'update', '--disablerepo="*"', '--enablerepo=' + ','.join(repos), '-y']
        )

    def test_update_with_additional_repos_and_packages(self, run_command, fs):
        run_command.return_value = {}

        repos = DEFAULT_REPOS + ('riri', 'fifi', 'loulou')
        packages = 'donald hortense'
        update(mock.MagicMock(), {'repos': 'riri, fifi, loulou', 'packages': packages})
        run_command.assert_called_once_with(
            ['yum', 'update', '--disablerepo="*"', '--enablerepo=' + ','.join(repos), '-y', packages]
        )

# ==============================================================================
# Proxies.
# ==============================================================================

class MockedUpdaterConfigParser(ConfigParser):
    def __init__(self, defaults={}):
        self._defaults = defaults
        self._sections = {}

    def sections(self):
        return ['repo_yum', 'repo_yum_2', 'repo_yum_3']

    def read(self, filepath):
        self._sections = {
            'repo_yum': {
                'name': 'yum_repo',
                'baseurl': 'http://yumrepo.example.com/os',
                'enabled': '1',
                'gpgcheck': '0',
                'proxy': 'http://user:password@proxy.example.com:3128'
            },
            'repo_yum_2': {
                'name': 'yum_repo_2',
                'baseurl': 'http://yumrepo.example.com/os',
                'enabled': '1',
                'gpgcheck': '0',
                'proxy': '_none_'
            },
            'repo_yum_3': {
                'name': 'yum_repo_3',
                'baseurl': 'http://yumrepo.example.com/os',
                'enabled': '1',
                'gpgcheck': '0'
            }
        }
        return [filepath]

    def write(self, filepath):
        return 0

CONFIG_PROXIES = '{"repo_yum": "http://user:password@proxy.example.com:3128", "repo_yum_2": "_none_", "repo_yum_3": "_none_"}' # noqa: E501

@mock.patch('ConfigParser.ConfigParser', new_callable=lambda: MockedUpdaterConfigParser)
class TestGetProxies:
    def test_get_proxies(self, ConfigParser, fs):
        res = get_proxies(None, None)
        assert json.loads(CONFIG_PROXIES) == json.loads(res)

    def test_get_proxies_error(self, ConfigParser, fs):
        with mock.patch.object(ConfigParser, 'read') as read:
            read.side_effect = Exception('Error!')

            with pytest.raises(XenAPIPlugin.Failure) as e:
                get_proxies(None, None)
            read.assert_called_once()
            assert e.value.params[0] == '-1'
            assert e.value.params[1] == 'Error!'

@mock.patch('ConfigParser.ConfigParser', new_callable=lambda: MockedUpdaterConfigParser)
class TestSetProxies:
    def test_set_proxies(self, ConfigParser, fs):
        fs.create_dir('/etc/yum.repos.d')

        res = set_proxies(None, {"proxies": CONFIG_PROXIES})
        assert res == ""

    def test_set_proxies_error(self, ConfigParser, fs):
        fs.create_dir('/etc/yum.repos.d')

        with mock.patch.object(ConfigParser, 'write') as write:
            write.side_effect = Exception('Error!')
            with pytest.raises(XenAPIPlugin.Failure) as e:
                set_proxies(None, {"proxies": CONFIG_PROXIES})
            write.assert_called_once()
            assert e.value.params[0] == '-1'
            assert e.value.params[1] == 'Error!'
