import pathlib
import sys

import mocked_configparser
import mocked_xen_api_plugin
import mocked_yum

sys.modules['ConfigParser'] = mocked_configparser
sys.modules['XenAPIPlugin'] = mocked_xen_api_plugin

# Mock yum globally, module is not necessarily present on the system.
sys.modules['yum'] = mocked_yum

sys.path.append(str(pathlib.Path(__file__).parent.resolve()) + '/../SOURCES/etc/xapi.d/plugins')

pytest_plugins = ("pyfakefs",)
