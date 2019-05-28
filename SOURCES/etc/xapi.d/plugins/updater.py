#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
import sys
import traceback
import XenAPIPlugin
import yum
import ConfigParser
import json

sys.path.append('.')
from vatesutils import configure_logging


def display_package(p):
    if len(p.changelog):
        changelog = {'date': p.changelog[0][0], 'author': p.changelog[0][1], 'description': p.changelog[0][2]}
    else:
        changelog = None
    return {'name': p.name, 'version': p.version, 'release': p.release, 'description': p.summary,
            'changelog': changelog, 'url': p.url, 'size': p.size, 'license': p.license}


def run_command(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    result = {'exit': process.returncode, 'stdout': stdout, 'stderr': stderr, 'command': command}
    _LOGGER.info(result)
    return result


def check_update(session, args):
    yum_instance = yum.YumBase()
    yum_instance.preconf.debuglevel = 0
    yum_instance.preconf.plugins = True
    packages = yum_instance.doPackageLists(pkgnarrow='updates')
    del yum_instance.ts
    yum_instance.initActionTs()  # make a new, blank ts to populate
    yum_instance.populateTs(keepold=0)
    yum_instance.ts.check()  # required for ordering
    yum_instance.ts.order()
    return json.dumps(map(display_package, packages))


def update(session, args):
    packages = args.get('packages')
    command = ['yum', 'update', '-y']
    if packages:
        command.append(packages)
    return json.dumps(run_command(command))


def check_upgrade(session, args):
    # TODO:
    # check new version exists
    # show release notes to user
    # check for available space

    pass


def upgrade():
    # TODO
    # check checksum of repo file (and probably in the future check its signature)
    # find a way to handle ".rpmnew" files that may have been created by the upgrade (stands true for any update actually)
    # Warning about .rpmsave
    # check for available space
    # edit yum configuration
    # yum clean metadata
    # upgrade
    # report/diagnostic
    pass


CONFIGURATION_FILE = '/etc/yum.repos.d/xcp-ng.repo'


# returns a JSON dict {repo_id: proxy}
def get_proxies(session, args):
    config = ConfigParser.ConfigParser({'proxy': '_none_'})
    config.read(CONFIGURATION_FILE)
    new_dict = dict((section, config.get(section, 'proxy', '_none_')) for section in config.sections())
    return json.dumps(new_dict)


# expects a JSON dict in a 'proxies' argument. The dict should be of the form {repo_id: proxy} with the special proxy
# '_none_' used for removal.
# example: {"xcp-ng-base": "http://192.168.100.82:3142"}
# returns a JSON dict like that: {"status": true} or like that: {"status": false, "error": "Unexpected URL \"https://updates.xcp-ng.org/7/7.6/updates/x86_64/\" for proxy \"_none_\" in section \"xcp-ng-updates\""}

def set_proxies(session, args):
    # '{"xcp-ng-base": "http://192.168.100.82:3142"}'
    # '{"xcp-ng-base": "_none_"}'
    try :
        special_url_prefix = 'http://HTTPS///'
        https_url_prefix = 'https://'
        proxies = json.loads(args['proxies'])
        config = ConfigParser.ConfigParser()
        if CONFIGURATION_FILE not in config.read(CONFIGURATION_FILE):
            return json.dumps({'status': False, 'error': 'could not read file %s' % CONFIGURATION_FILE})
        for section in proxies:
            if config.has_section(section):
                # idempotence
                if proxies[section] == '_none_' and not config.has_option(section, 'proxy'):
                    continue
                if config.has_option(section, 'proxy') and config.get(section, 'proxy') == proxies[section]:
                    continue
                config.set(section, 'proxy', proxies[section])
                url = config.get(section, 'baseurl')
                if proxies[section] == '_none_' and url.startswith(special_url_prefix):
                    config.set(section, 'baseurl', https_url_prefix + url[len(special_url_prefix):])
                elif proxies[section] != '_none_' and url.startswith(https_url_prefix):
                    config.set(section, 'baseurl', special_url_prefix + url[len(https_url_prefix):])
                else:
                    return json.dumps({'status': False,
                                       'error': 'Unexpected URL "%s" for proxy "%s" in section "%s"' % (
                                           url, proxies[section], section)})
            else:
                return json.dumps({'status': False, 'error': 'Can\'t find section "%s" in config file' % section})
        with open(CONFIGURATION_FILE, 'wb') as configfile:
            config.write(configfile)
        return json.dumps({'status': True})
    except :
        return json.dumps({'status': False, 'error': traceback.format_exc()})


_LOGGER = configure_logging('updater')
if __name__ == "__main__":
    XenAPIPlugin.dispatch({
        'check_update': check_update,
        'update': update,
        'get_proxies': get_proxies,
        'set_proxies': set_proxies
    })
