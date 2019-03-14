# XCP-ng updater

A xapi plugin to invoke yum commands on the hosts.

## Examples

Checking for updates:

```
$ xe host-call-plugin host-uuid=${HOST_UNDER_TEST_UUID} plugin=updater.py fn=check_update

{"result": [{"release": "4.2", "fullName": "xen-dom0-libs-4.7.5-4.2.x86_64", "version": "4.7.5", "arch": "x86_64", "name": "xen-dom0-libs"}, {"release": "4.2", "fullName": "xen-dom0-tools-4.7.5-4.2.x86_64", "version": "4.7.5", "arch": "x86_64", "name": "xen-dom0-tools"}, {"release": "4.2", "fullName": "xen-tools-4.7.5-4.2.x86_64", "version": "4.7.5", "arch": "x86_64", "name": "xen-tools"}, {"release": "22.xs1", "fullName": "2:microcode_ctl-2.1-22.xs1.x86_64", "version": "2.1", "arch": "x86_64", "name": "microcode_ctl"}, {"release": "4.2", "fullName": "xen-hypervisor-4.7.5-4.2.x86_64", "version": "4.7.5", "arch": "x86_64", "name": "xen-hypervisor"}, {"release": "4.2", "fullName": "xen-libs-4.7.5-4.2.x86_64", "version": "4.7.5", "arch": "x86_64", "name": "xen-libs"}]}
```
 
 Start the updates:


```
$ xe host-call-plugin host-uuid=${HOST_UNDER_TEST_UUID} plugin=updater.py fn=update
```

## Proxy configuration

### `get_proxies()`:

```
$ xe host-call-plugin host-uuid=${HOST_UNDER_TEST_UUID} plugin=updater.py fn=get_proxies
{"xcp-ng-base": "http://192.168.100.82:3142", "xcp-ng-updates": "_none_", "xcp-ng-extras": "_none_", "xcp-ng-extras_testing": "_none_", "xcp-ng-updates_testing": "http://192.168.100.82:3142"}

```
The answer is a JSON dict section -> proxy. The dict is empty if the file couldn't be read.
 

### `set_proxies(proxies)`:

```
$ echo $JSON_PROXY
{"xcp-ng-base": "http://192.168.100.82:3142", "xcp-ng-updates": "_none_", "xcp-ng-extras": "_none_", "xcp-ng-extras_testing": "_none_", "xcp-ng-updates_testing": "http://192.168.100.82:3142"}
$ xe host-call-plugin host-uuid=${HOST_UNDER_TEST_UUID} plugin=updater.py fn=set_proxies args:proxies="'$JSON_PROXY'"
{"status": true}
```
The `proxies` parameter is a JSON dict section-> proxy for the list of sections whose proxy we want to alter.

The returned value should be the JSON value `{"status": true}` or `{"status": false, "error": "<message>"}`.
