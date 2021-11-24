from ConfigParser import ConfigParser
import errno
import fcntl
import json
import mock
import pytest
import time
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
# Lock: Try to execute a command with a lock already locked.
# ==============================================================================

# Must be mocked after usage of fixture `fs`, because this last one
# has a modified version of flock. ;)
def mocked_flock_locked(fd, flags):
    if flags & fcntl.LOCK_NB:
        raise IOError(errno.EWOULDBLOCK, '')
    time.sleep(2) # We don't want to wait a long time in case of failure in tests.
    raise Exception('Too long!')

def mocked_flock_wait_and_lock(fd, flags):
    assert not (flags & fcntl.LOCK_NB)
    time.sleep(0.5)

@mock.patch('xcpngutils.TimeoutException', autospec=True)
@mock.patch('updater.OperationLocker.timeout', new_callable=mock.PropertyMock)
@mock.patch('updater.run_command', autospec=True)
class TestExceptionLockedFile:
    def test_check_update_with_empty_locked_file(self, run_command, timeout, TimeoutException, fs):
        fs.create_file(pytest.plugins_lock_file)
        run_command.return_value = {}
        timeout.return_value = 0

        with mock.patch('fcntl.flock', wraps=mocked_flock_locked) as flock:
            with pytest.raises(XenAPIPlugin.Failure) as e:
                check_update(mock.MagicMock(), {})
            flock.assert_called_once_with(mock.ANY, fcntl.LOCK_EX | fcntl.LOCK_NB)
        TimeoutException.assert_not_called()

        assert timeout.call_args_list == [((0,),), ()]
        assert e.value.params[0] == '-1'
        assert e.value.params[1] == 'The updater plugin is busy (current operation: <UNKNOWN>)'

    def test_check_update_during_check_update(self, run_command, timeout, TimeoutException, fs):
        fs.create_file(pytest.plugins_lock_file, contents='check_update')
        run_command.return_value = {}
        timeout.return_value = 0

        with mock.patch('fcntl.flock', wraps=mocked_flock_locked) as flock:
            with pytest.raises(XenAPIPlugin.Failure) as e:
                check_update(mock.MagicMock(), {})
            flock.assert_called_once_with(mock.ANY, fcntl.LOCK_EX | fcntl.LOCK_NB)
        TimeoutException.assert_not_called()

        assert timeout.call_args_list == [((0,),), ()]
        assert e.value.params[0] == '-1'
        assert e.value.params[1] == 'The updater plugin is busy (current operation: check_update)'

    def test_update_during_check_update(self, run_command, timeout, TimeoutException, fs):
        fs.create_file(pytest.plugins_lock_file, contents='check_update')
        run_command.return_value = {}
        timeout.return_value = 1 # We don't want to wait a long time in the unit tests. ;)

        with mock.patch('fcntl.flock', wraps=mocked_flock_locked) as flock:
            with pytest.raises(XenAPIPlugin.Failure) as e:
                update(mock.MagicMock(), {})
            # Try a firstime without timeout and retry a second time with timer.
            assert flock.call_args_list == [((mock.ANY, fcntl.LOCK_EX | fcntl.LOCK_NB),), ((mock.ANY, fcntl.LOCK_EX),)]
        TimeoutException.assert_called_once()

        # Note: By default we use 10s of timeout on `update` command.
        # The forced value of 0.1 is not set using the timeout setter, only the default value of 10.
        # The remaining calls without value are just the timeout getter.
        assert timeout.call_args_list == [((10,),), (), (), ()]
        assert e.value.params[0] == '-1'
        assert e.value.params[1] == 'The updater plugin is busy (current operation: check_update)'

    def test_update_during_check_update_before_timeout(self, run_command, timeout, TimeoutException, fs):
        fs.create_file(pytest.plugins_lock_file, contents='check_update')
        run_command.return_value = {}
        timeout.return_value = 1

        with mock.patch('fcntl.flock', wraps=mocked_flock_wait_and_lock) as flock:
            update(mock.MagicMock(), {})
            assert flock.call_args_list == [
                ((mock.ANY, fcntl.LOCK_EX | fcntl.LOCK_NB),),
                ((mock.ANY, fcntl.LOCK_EX,),),
                ((mock.ANY, fcntl.LOCK_UN,),)
            ]
        TimeoutException.assert_not_called() # Success. \o/

        assert timeout.call_args_list == [((10,),), (), (), ()]

    def test_ckeck_update_during_update(self, run_command, timeout, TimeoutException, fs):
        fs.create_file(pytest.plugins_lock_file, contents='update')
        run_command.return_value = {}
        timeout.return_value = 0

        with mock.patch('fcntl.flock', wraps=mocked_flock_locked) as flock:
            with pytest.raises(XenAPIPlugin.Failure) as e:
                check_update(mock.MagicMock(), {})
            flock.assert_called_once_with(mock.ANY, fcntl.LOCK_EX | fcntl.LOCK_NB)
        TimeoutException.assert_not_called()

        assert timeout.call_args_list == [((0,),), ()]
        assert e.value.params[0] == '-1'
        assert e.value.params[1] == 'The updater plugin is busy (current operation: update)'

    def test_update_during_update(self, run_command, timeout, TimeoutException, fs):
        fs.create_file(pytest.plugins_lock_file, contents='update')
        run_command.return_value = {}
        timeout.return_value = 1

        # When an update is already in progress and if we try to run another update command,
        # we throw an exception before timeout. So there is only one lock test.
        with mock.patch('fcntl.flock', wraps=mocked_flock_locked) as flock:
            with pytest.raises(XenAPIPlugin.Failure) as e:
                update(mock.MagicMock(), {})
            flock.assert_called_once_with(mock.ANY, fcntl.LOCK_EX | fcntl.LOCK_NB)
        TimeoutException.assert_not_called()

        assert timeout.call_args_list == [((10,),), (), ()]
        assert e.value.params[0] == '-1'
        assert e.value.params[1] == 'Update already in progress'

# ==============================================================================
# Lockfile with content but not locked.
# ==============================================================================

@mock.patch('updater.run_command', autospec=True)
class TestNotLockedLockFile:
    def test_check_update_during_check_update(self, run_command, fs):
        fs.create_file(pytest.plugins_lock_file, contents='check_update')
        run_command.return_value = {}

        expected = ' \
            [{"name": "Dummy Package", "version": "0.0.0", "release": "Dummy released", \
            "description": "Lorem ipsum...", "changelog": null, "url": "http://www.example.com/", "size": "0", \
            "license": "GPLv2 and LGPLv2+ and BSD"}]'
        res = check_update(None, {})
        assert json.loads(expected) == json.loads(res)

    def test_update_during_check_update(self, run_command, fs):
        fs.create_file(pytest.plugins_lock_file, contents='check_update')

        run_command.return_value = {}

        update(mock.MagicMock(), {})
        run_command.assert_called_once_with(
            ['yum', 'update', '--disablerepo="*"', '--enablerepo=' + ','.join(DEFAULT_REPOS), '-y']
        )

    def test_ckeck_update_during_update(self, run_command, fs):
        fs.create_file(pytest.plugins_lock_file, contents='update')
        run_command.return_value = {}

        expected = ' \
            [{"name": "Dummy Package", "version": "0.0.0", "release": "Dummy released", \
            "description": "Lorem ipsum...", "changelog": null, "url": "http://www.example.com/", "size": "0", \
            "license": "GPLv2 and LGPLv2+ and BSD"}]'
        res = check_update(None, {})
        assert json.loads(expected) == json.loads(res)

    def test_update_during_update(self, run_command, fs):
        fs.create_file(pytest.plugins_lock_file, contents='update')

        run_command.return_value = {}

        update(mock.MagicMock(), {})
        run_command.assert_called_once_with(
            ['yum', 'update', '--disablerepo="*"', '--enablerepo=' + ','.join(DEFAULT_REPOS), '-y']
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
