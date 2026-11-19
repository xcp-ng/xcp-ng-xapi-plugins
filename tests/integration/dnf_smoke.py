"""
Run the updater plugin against the real dnf of an EL10 system.

Must run as root in a disposable EL10 container with outdated packages
(it updates and installs packages).
"""
import json
import os
import pathlib
import subprocess
import sys
from unittest import mock

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / 'tests'), str(ROOT / 'SOURCES/etc/xapi.d/plugins')]

import mocked_xen_api_plugin
sys.modules['XenAPIPlugin'] = mocked_xen_api_plugin
os.makedirs('/var/lib/xcp-ng-xapi-plugins', exist_ok=True)
import updater

REPOS = 'baseos,appstream'


def check_update():
    return json.loads(updater.check_update(None, {'repos': REPOS}))


def cli_check_update():
    out = subprocess.run(['dnf', '-q', 'check-update', '--disablerepo=*', '--enablerepo=' + REPOS],
                         capture_output=True, text=True).stdout
    res = set()
    for line in out.splitlines():
        fields = line.split()
        if len(fields) == 3:
            version, release = fields[1].split(':')[-1].rsplit('-', 1)
            res.add((fields[0].rsplit('.', 1)[0], version, release))
    return res


packages = check_update()
names = [p['name'] for p in packages]
print('check_update: {} packages'.format(len(packages)))
assert packages, 'no update found, the image is expected to be outdated'
assert len(names) == len(set(names)), 'some packages are listed more than once'
assert all(p['changelog'] for p in packages), 'some packages have no changelog'
assert all(isinstance(p['changelog']['date'], int) for p in packages)
assert {(p['name'], p['version'], p['release']) for p in packages} == cli_check_update(), \
    'check_update differs from `dnf check-update`'

target = 'tzdata' if 'tzdata' in names else names[0]
session = mock.MagicMock()
assert json.loads(updater.update(session, {'repos': REPOS, 'packages': target}))['returncode'] == 0
assert target not in [p['name'] for p in check_update()], '{} still needs an update'.format(target)
assert json.loads(updater.install(session, {'repos': REPOS, 'packages': 'which'}))['returncode'] == 0
installed = json.loads(updater.query_installed(session, {'packages': 'which ' + target}))
assert all(installed.values()), installed
print('OK')
