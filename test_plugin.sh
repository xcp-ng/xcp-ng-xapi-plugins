#!/usr/bin/env bash

set -e

TEST_HOST=root@192.168.100.187

rsync -v  --exclude '.*' -r xcp-ng-updater/ ${TEST_HOST}:/
ssh ${TEST_HOST} xe host-call-plugin host-uuid=83e9bfc6-cfc3-4873-9f6b-b8df6d89e87a plugin=updater.py fn=check_update