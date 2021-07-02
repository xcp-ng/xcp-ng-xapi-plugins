#!/usr/bin/env python
# -*- coding: utf-8 -*-

from functools import wraps
import ConfigParser
import json
import os
import subprocess
import sys
import traceback
import XenAPI
import XenAPIPlugin
import yum

sys.path.append('.')
from xcpngutils import configure_logging, run_command
from xcpngutils.filelocker import FileLocker


REPOS = ('xcp-ng-base', 'xcp-ng-updates')


class OperationException(Exception):
    pass

class OperationLocker(FileLocker):
    __slots__ = ('operation', 'current_operation')

    def __init__(self, operation, timeout=0):
        super(OperationLocker, self).__init__(
            timeout=timeout,
            auto_remove=False,
            dir='/var/lib/xcp-ng-xapi-plugins/'
        )
        self.operation = operation

    def _raise_busy(self):
        raise OperationException('The updater plugin is busy (current operation: {})'.format(self.current_operation))

    def _prelock(self):
        # 1. Read the current operation from lockfile before timeout or direct lock call.
        self.current_operation = None
        try:
            self.file.seek(0)
            self.current_operation = self.file.readline().rstrip('\n')
        except:
            pass

        # 2. If there is no current operation, it's ok we can try to lock the file.
        if not self.current_operation:
            return

        # 3. At this point a current operation is running, so:
        # - If the operation to execute is not 'update', a busy exception is thrown.
        # - If the next op is 'update' and the current op is the same, an 'already in progress' exception is thrown.
        # - More precisely, there is only a unique valid case to pass this point => The next op is 'update' and
        #   the previous op is different.
        self_is_update = self.operation == 'update'
        if self_is_update and self.operation == self.current_operation:
            raise OperationException('Update already in progress')
        elif not self_is_update:
            self._raise_busy()

    def _timeout_reached(self):
        self._raise_busy()

    def _locked(self):
        self.file.seek(0)
        self.file.truncate()
        self.file.write('{}\n'.format(self.operation))
        self.file.flush()

    def _unlocked(self):
        self.file.seek(0)
        self.file.truncate()
        self.file.flush()

def operationlock(*pid_args, **pid_kwargs):
    def wrapper(func):
        @wraps(func)
        def decorator(*args, **kwargs):
            try:
                pid_kwargs['operation'] = func.__name__
                with OperationLocker(*pid_args, **pid_kwargs):
                    return func(*args, **kwargs)
            except Exception as e:
                return json.dumps({'error': str(e)})
        return decorator
    return wrapper


def display_package(p):
    if len(p.changelog):
        changelog = {'date': p.changelog[0][0], 'author': p.changelog[0][1], 'description': p.changelog[0][2]}
    else:
        changelog = None
    return {'name': p.name, 'version': p.version, 'release': p.release, 'description': p.summary,
            'changelog': changelog, 'url': p.url, 'size': p.size, 'license': p.license}


@operationlock()
def check_update(session, args):
    yum_instance = yum.YumBase()
    yum_instance.preconf.debuglevel = 0
    yum_instance.preconf.plugins = True
    yum_instance.repos.disableRepo('*')
    yum_instance.repos.enableRepo(','.join(REPOS))
    packages = yum_instance.doPackageLists(pkgnarrow='updates')
    del yum_instance.ts
    yum_instance.initActionTs()  # make a new, blank ts to populate
    yum_instance.populateTs(keepold=0)
    yum_instance.ts.check()  # required for ordering
    yum_instance.ts.order()
    return json.dumps(map(display_package, packages))


@operationlock(timeout=10)
def update(session, args):
    packages = args.get('packages')
    task = None
    res = None
    try:
        host = session.xenapi.session.get_this_host(session.handle)
        host_name = session.xenapi.host.get_name_label(host)
        host_uuid = session.xenapi.host.get_uuid(host)
        task = session.xenapi.task.create('Update host %s (%s)' % (host_name, host_uuid), '')
        packages = args.get('packages')
        command = ['yum', 'update', '--disablerepo="*"', '--enablerepo=' + ','.join(REPOS), '-y']
        if packages:
            command.append(packages)
        res = run_command(command)
        session.xenapi.task.set_status(task, 'success')
    except XenAPI.Failure as e:
        res = {'error': e.details}
    except Exception as e:
        res = {'error': str(e)}
    finally:
        if task:
            session.xenapi.task.destroy(task)
        return json.dumps(res)


def check_upgrade(session, args):
    # TODO:
    # check new version exists
    # show release notes to user
    # check for available space
    # protect it with operationlock

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
    # protect it with operationlock

    pass


CONFIGURATION_FILE = '/etc/yum.repos.d/xcp-ng.repo'


# returns a JSON dict {repo_id: proxy}
@operationlock()
def get_proxies(session, args):
    config = ConfigParser.ConfigParser({'proxy': '_none_'})
    config.read(CONFIGURATION_FILE)
    new_dict = dict((section, config.get(section, 'proxy', '_none_')) for section in config.sections())
    return json.dumps(new_dict)


# expects a JSON dict in a 'proxies' argument. The dict should be of the form {repo_id: proxy} with the special proxy
# '_none_' used for removal.
# example: {"xcp-ng-base": "http://192.168.100.82:3142"}
# returns a JSON dict like that: {"status": true} or like that: {"status": false, "error": "Unexpected URL \"https://updates.xcp-ng.org/7/7.6/updates/x86_64/\" for proxy \"_none_\" in section \"xcp-ng-updates\""}

@operationlock()
def set_proxies(session, args):
    # '{"xcp-ng-base": "http://192.168.100.82:3142"}'
    # '{"xcp-ng-base": "_none_"}'
    try:
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
    except:
        return json.dumps({'status': False, 'error': traceback.format_exc()})


_LOGGER = configure_logging('updater')
if __name__ == "__main__":
    XenAPIPlugin.dispatch({
        'check_update': check_update,
        'update': update,
        'get_proxies': get_proxies,
        'set_proxies': set_proxies
    })
