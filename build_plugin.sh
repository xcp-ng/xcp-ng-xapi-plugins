#!/usr/bin/env bash

set -ex

BUILD_MACHINE=debian@192.168.100.158

rsync -v  --exclude '.*' -r . ${BUILD_MACHINE}:xcp-ng-updater
ssh ${BUILD_MACHINE} 'cd xcp-ng-updater; fpm -s dir --summary "XPC-ng updater xapi plugin" --url https://github.com/xcp-ng/xcp-ng-updater --license "GNU AFFERO GENERAL PUBLIC LICENSE" --vendor VATES -t rpm -n xcp-ng-updater -f -p xcp-ng-updater_VERSION.rpm -C SOURCES .'
ssh ${BUILD_MACHINE} 'cd xcp-ng-updater; rpm -qpli xcp-ng-updater_1.0.rpm'
rsync -v ${BUILD_MACHINE}:xcp-ng-updater/xcp-ng-updater_1.0.rpm .