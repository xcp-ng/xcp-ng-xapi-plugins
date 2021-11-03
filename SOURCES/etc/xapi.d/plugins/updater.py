#!/usr/bin/env python
# -*- coding: utf-8 -*-

from functools import wraps
import ConfigParser
import json
import sys
import yum

import XenAPIPlugin

sys.path.append('.')
from xcpngutils import configure_logging, run_command, error_wrapped
from xcpngutils.filelocker import FileLocker


DEFAULT_REPOS = ('xcp-ng-base', 'xcp-ng-updates')


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
        op = self.current_operation
        if not op:
            op = '<UNKNOWN>'
        raise OperationException('The updater plugin is busy (current operation: {})'.format(op))

    def _lock(self):
        # Current op must be initialized here because if timeout is reached,
        # callbacks like `_raise_busy` are called and the attribute must be defined.
        self.current_operation = None

        try:
            super(OperationLocker, self)._lock()
        except Exception:
            # Failed to take the lock, try to report why.
            try:
                with open(self.filename) as f:
                    self.current_operation = f.readline().rstrip('\n')
            except Exception:
                # Couldn't open or read the file, might have been deleted, just raise busy without any explanation.
                self._raise_busy()
            self_is_update = self.operation == 'update'
            if self_is_update and self.operation == self.current_operation:
                raise OperationException('Update already in progress')
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
            pid_kwargs['operation'] = func.__name__
            with OperationLocker(*pid_args, **pid_kwargs):
                return func(*args, **kwargs)
        return decorator
    return wrapper


def display_package(p):
    if len(p.changelog):
        changelog = {'date': p.changelog[0][0], 'author': p.changelog[0][1], 'description': p.changelog[0][2]}
    else:
        changelog = None
    return {'name': p.name, 'version': p.version, 'release': p.release, 'description': p.summary,
            'changelog': changelog, 'url': p.url, 'size': p.size, 'license': p.license}

def build_repo_list(additional_repos):
    repos = list(DEFAULT_REPOS)
    if additional_repos:
        repos += [x.strip() for x in additional_repos.split(',')]
    return repos

@error_wrapped
@operationlock()
def check_update(session, args):
    repos = build_repo_list(args.get('repos'))
    yum_instance = yum.YumBase()
    yum_instance.preconf.debuglevel = 0
    yum_instance.preconf.plugins = True
    yum_instance.repos.disableRepo('*')
    yum_instance.repos.enableRepo(','.join(repos))
    packages = yum_instance.doPackageLists(pkgnarrow='updates')
    del yum_instance.ts
    yum_instance.initActionTs()  # make a new, blank ts to populate
    yum_instance.populateTs(keepold=0)
    yum_instance.ts.check()  # required for ordering
    yum_instance.ts.order()
    # Python 2&3 compatible code
    return json.dumps(list(map(display_package, packages)))

@error_wrapped
@operationlock(timeout=10)
def update(session, args):
    repos = build_repo_list(args.get('repos'))
    task = None
    res = None
    error = None
    try:
        host = session.xenapi.session.get_this_host(session.handle)
        host_name = session.xenapi.host.get_name_label(host)
        host_uuid = session.xenapi.host.get_uuid(host)
        task = session.xenapi.task.create('Update host %s (%s)' % (host_name, host_uuid), '')
        packages = args.get('packages')
        command = ['yum', 'update', '--disablerepo="*"', '--enablerepo=' + ','.join(repos), '-y']
        if packages:
            command.append(packages)
        res = run_command(command)
        session.xenapi.task.set_status(task, 'success')
    except Exception as e:
        error = e
    finally:
        if task:
            session.xenapi.task.destroy(task)
        if error:
            raise error
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
    # find a way to handle ".rpmnew" files that may have been created
    # by the upgrade (stands true for any update actually)
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
@error_wrapped
@operationlock()
def get_proxies(session, args):
    config = ConfigParser.ConfigParser({'proxy': '_none_'})
    config.read(CONFIGURATION_FILE)
    new_dict = dict((section, config.get(section, 'proxy', '_none_')) for section in config.sections())
    return json.dumps(new_dict)


# expects a JSON dict in a 'proxies' argument. The dict should be of the form {repo_id: proxy} with the special proxy
# '_none_' used for removal.
# example: {"xcp-ng-base": "http://192.168.100.82:3142"}
# returns a JSON empty string or raise a XenAPIFailure in case of error
@error_wrapped
@operationlock()
def set_proxies(session, args):
    # '{"xcp-ng-base": "http://192.168.100.82:3142"}'
    # '{"xcp-ng-base": "_none_"}'
    special_url_prefix = 'http://HTTPS///'
    https_url_prefix = 'https://'
    proxies = json.loads(args['proxies'])
    config = ConfigParser.ConfigParser()
    if CONFIGURATION_FILE not in config.read(CONFIGURATION_FILE):
        raise Exception('could not read file %s' % CONFIGURATION_FILE)

    for section in proxies:
        if not config.has_section(section):
            raise Exception("Can't find section '%s' in config file" % section)

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
            raise Exception('Unexpected URL "%s" for proxy "%s" in section "%s"' % (url, proxies[section], section))

    with open(CONFIGURATION_FILE, 'wb') as configfile:
        config.write(configfile)
    return ''

_LOGGER = configure_logging('updater')
if __name__ == "__main__":
    XenAPIPlugin.dispatch({
        'check_update': check_update,
        'update': update,
        'get_proxies': get_proxies,
        'set_proxies': set_proxies
    })
