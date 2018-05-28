#!/usr/bin/env bash

set -ex

MASTER_HOST=root@192.168.100.11
SNAPSHOT_UUID=7ae9921d-d0db-c87c-ea7c-b3450fe8eeeb
VM_HOST_UNDER_TEST_UUID=13ec74c2-9b57-a327-962f-1ebd9702eec4
HOST_UNDER_TEST_UUID=05c61e28-11cf-4131-b645-a0be7637c044
XCP_HOST_UNDER_TEST_IP=192.168.100.151
XCP_HOST_UNDER_TEST=root@${XCP_HOST_UNDER_TEST_IP}

VERSION=1.1
ARTIFACT=xcp-ng-updater_${VERSION}.rpm

ssh ${MASTER_HOST} xe snapshot-revert snapshot-uuid=${SNAPSHOT_UUID}
ssh ${MASTER_HOST} xe vm-start vm=${VM_HOST_UNDER_TEST_UUID}
until ping -c1 ${XCP_HOST_UNDER_TEST_IP} &>/dev/null; do :; done
sleep 20
rsync -v  --exclude '.*' -r ${ARTIFACT} ${XCP_HOST_UNDER_TEST}:
ssh ${XCP_HOST_UNDER_TEST} yum install -y ${ARTIFACT}
sleep 10
ssh ${XCP_HOST_UNDER_TEST} xe host-call-plugin host-uuid=${HOST_UNDER_TEST_UUID} plugin=updater.py fn=check_update
ssh ${XCP_HOST_UNDER_TEST} xe host-call-plugin host-uuid=${HOST_UNDER_TEST_UUID} plugin=updater.py fn=update