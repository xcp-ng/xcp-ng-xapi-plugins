#!/usr/bin/env bash

set -ex

BUILD_MACHINE=debian@192.168.100.158

VERSION=1.1
ARTIFACT=xcp-ng-updater_${VERSION}.rpm

rsync -v  --exclude '.*' -r . ${BUILD_MACHINE}:xcp-ng-updater
ssh ${BUILD_MACHINE} "cd xcp-ng-updater; fpm -s dir -v ${VERSION} --description 'XPC-ng updater xapi plugin' --url https://github.com/xcp-ng/xcp-ng-updater --license 'GNU AFFERO GENERAL PUBLIC LICENSE' --vendor VATES -t rpm -n xcp-ng-updater -f -p ${ARTIFACT} -C SOURCES ."
ssh ${BUILD_MACHINE} "cd xcp-ng-updater; rpm -qpli ${ARTIFACT}"
rsync -v ${BUILD_MACHINE}:xcp-ng-updater/${ARTIFACT} .