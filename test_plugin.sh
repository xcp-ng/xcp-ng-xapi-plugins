#!/usr/bin/env bash

set -ex

MASTER_HOST=root@192.168.100.11
XCP_HOST_UNDER_TEST=root@192.168.100.187
SNAPSHOT_UUID=581cdbe3-5fc1-695c-d2ba-c73cbf4ea24f
VM_HOST_UNDER_TEST_UUID=58b2d434-b3d3-d607-dde9-7a0f69201c08
HOST_UNDER_TEST_UUID=83e9bfc6-cfc3-4873-9f6b-b8df6d89e87a

ssh ${MASTER_HOST} xe snapshot-revert snapshot-uuid=${SNAPSHOT_UUID}
ssh ${MASTER_HOST} xe vm-start vm=${VM_HOST_UNDER_TEST_UUID}
until ping -c1 192.168.100.187 &>/dev/null; do :; done
sleep 20
rsync -v  --exclude '.*' -r xcp-ng-updater_1.0.rpm ${XCP_HOST_UNDER_TEST}:
ssh ${XCP_HOST_UNDER_TEST} rpm -i xcp-ng-updater_1.0.rpm
sleep 10
ssh ${XCP_HOST_UNDER_TEST} xe host-call-plugin host-uuid=${HOST_UNDER_TEST_UUID} plugin=updater.py fn=check_update
ssh ${XCP_HOST_UNDER_TEST} xe host-call-plugin host-uuid=${HOST_UNDER_TEST_UUID} plugin=updater.py fn=update