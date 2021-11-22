import pathlib
import pytest
import sys

import mocked_configparser
import mocked_xen_api_plugin
import mocked_yum

def pytest_configure():
    pytest.plugins_lock_file = '/var/lib/xcp-ng-xapi-plugins/pytest.lock'

# Not installed.
sys.modules['XenAPIPlugin'] = mocked_xen_api_plugin

# Not installed and must be mocked in specific tests.
sys.modules['ConfigParser'] = mocked_configparser

# Mock yum globally, module is not necessarily present on the system.
sys.modules['yum'] = mocked_yum

sys.path.append(str(pathlib.Path(__file__).parent.resolve()) + '/../SOURCES/etc/xapi.d/plugins')

pytest_plugins = ("pyfakefs",)
