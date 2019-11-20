#!/usr/bin/env python
# -*- coding: utf-8 -*-

# this is a XCP-ng plugin. It goes to /etc/xapi.d/plugins/ with the exec bit set.
# it expects to have the XCP-ng python xapi plugins library installed. (https://github.com/xcp-ng/xcp-ng-xapi-plugins)

import sys

import XenAPIPlugin

sys.path.append('.')
from xcpngutils import configure_logging, error_wrapped, install_package, run_command
from xcpngutils.filelocker import FileLocker

packages = ['https://nextcloud.vates.fr/index.php/s/PabagxbHY3zAeqK/download?path=%2F&files=glusterfs-7.0rc3-0.1.gita92e9e8.el7.x86_64.rpm',
            'https://nextcloud.vates.fr/index.php/s/PabagxbHY3zAeqK/download?path=%2F&files=glusterfs-api-7.0rc3-0.1.gita92e9e8.el7.x86_64.rpm',
            'https://nextcloud.vates.fr/index.php/s/PabagxbHY3zAeqK/download?path=%2F&files=glusterfs-cli-7.0rc3-0.1.gita92e9e8.el7.x86_64.rpm',
            'https://nextcloud.vates.fr/index.php/s/PabagxbHY3zAeqK/download?path=%2F&files=glusterfs-client-xlators-7.0rc3-0.1.gita92e9e8.el7.x86_64.rpm',
            'https://nextcloud.vates.fr/index.php/s/PabagxbHY3zAeqK/download?path=%2F&files=glusterfs-extra-xlators-7.0rc3-0.1.gita92e9e8.el7.x86_64.rpm',
            'https://nextcloud.vates.fr/index.php/s/PabagxbHY3zAeqK/download?path=%2F&files=glusterfs-fuse-7.0rc3-0.1.gita92e9e8.el7.x86_64.rpm',
            'https://nextcloud.vates.fr/index.php/s/PabagxbHY3zAeqK/download?path=%2F&files=glusterfs-libs-7.0rc3-0.1.gita92e9e8.el7.x86_64.rpm',
            'https://nextcloud.vates.fr/index.php/s/PabagxbHY3zAeqK/download?path=%2F&files=glusterfs-server-7.0rc3-0.1.gita92e9e8.el7.x86_64.rpm',
            'https://nextcloud.vates.fr/index.php/s/PabagxbHY3zAeqK/download?path=%2F&files=python2-gluster-7.0rc3-0.1.gita92e9e8.el7.x86_64.rpm',
            'https://nextcloud.vates.fr/index.php/s/PabagxbHY3zAeqK/download?path=%2F&files=userspace-rcu-0.7.16-1.el7.x86_64.rpm']


def install_packages(session, args):
    print "hello"
    result = run_command(['yum', 'install', '-y', 'attr'])
    print result
    result = run_command(['rpm', '-i'] + packages)
    print result
    return True


_LOGGER = configure_logging('xosan2')
if __name__ == "__main__":
    XenAPIPlugin.dispatch({
        'install_packages': install_packages
    })
