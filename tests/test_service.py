import mock
import pytest
import XenAPIPlugin

from service import start_service, stop_service, restart_service, try_restart_service

@mock.patch("service.run_command", autospec=True)
class TestService:
    SERVICE = 'linstor-satellite'

    def _test_command(self, cmd, cmd_name, run_command):
        cmd(mock.MagicMock(), {'service': self.SERVICE})
        run_command.assert_called_once_with(['systemctl', cmd_name, self.SERVICE])

    def _test_command_without_service(self, cmd):
        with pytest.raises(XenAPIPlugin.Failure) as e:
            cmd(mock.MagicMock(), {})
        assert e.value.params[0] == '-1'
        assert e.value.params[1] == 'Missing or empty argument `service`'

    def test_start(self, run_command):
        self._test_command(start_service, 'start', run_command)

    def test_stop(self, run_command):
        self._test_command(stop_service, 'stop', run_command)

    def test_restart(self, run_command):
        self._test_command(restart_service, 'restart', run_command)

    def test_try_restart(self, run_command):
        self._test_command(try_restart_service, 'try-restart', run_command)

    def test_start_without_service(self, run_command):
        self._test_command_without_service(start_service)

    def test_stop_without_service(self, run_command):
        self._test_command_without_service(stop_service)

    def test_restart_without_service(self, run_command):
        self._test_command_without_service(restart_service)

    def test_try_restart_without_service(self, run_command):
        self._test_command_without_service(try_restart_service)
