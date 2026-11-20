import pathlib
import sys

import mocked_xen_api_plugin
import mocked_yum
import pytest


def pytest_configure():
    pytest.plugins_lock_file = '/var/lib/xcp-ng-xapi-plugins/pytest.lock'

# Not installed.
sys.modules['XenAPIPlugin'] = mocked_xen_api_plugin

# Mock yum globally, module is not necessarily present on the system.
sys.modules['yum'] = mocked_yum

sys.path.append(str(pathlib.Path(__file__).parent.resolve()) + '/../SOURCES/etc/xapi.d/plugins')

pytest_plugins = ("pyfakefs",)
