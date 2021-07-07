# XCP-ng xapi plugins

## XCP-ng ZFS pool list

A xapi plugin to discover ZFS pools present on the host.

### Example
```
$ xe host-call-plugin host-uuid=${HOST_UNDER_TEST_UUID} plugin=zfs.py fn=list_zfs_pools
{"tank": {"setuid": "on", "relatime": "off", "referenced": "24K", "written": "24K", "zoned": "off", "primarycache": "all", "logbias": "latency", "creation": "Mon May 27 17:24 2019", "sync": "standard", "snapdev": "hidden", "dedup": "off", "sharenfs": "off", "usedbyrefreservation": "0B", "sharesmb": "off", "createtxg": "1", "canmount": "on", "mountpoint": "/tank", "casesensitivity": "sensitive", "utf8only": "off", "xattr": "on", "dnodesize": "legacy", "mlslabel": "none", "objsetid": "54", "defcontext": "none", "rootcontext": "none", "mounted": "yes", "compression": "off", "overlay": "off", "logicalused": "126K", "usedbysnapshots": "0B", "filesystem_count": "none", "copies": "1", "snapshot_limit": "none", "aclinherit": "restricted", "compressratio": "1.00x", "readonly": "off", "version": "5", "normalization": "none", "filesystem_limit": "none", "type": "filesystem", "secondarycache": "all", "refreservation": "none", "available": "17.4G", "used": "364K", "exec": "on", "refquota": "none", "refcompressratio": "1.00x", "quota": "none", "keylocation": "none", "snapshot_count": "none", "fscontext": "none", "vscan": "off", "reservation": "none", "atime": "on", "recordsize": "128K", "usedbychildren": "340K", "usedbydataset": "24K", "guid": "656061077639704004", "pbkdf2iters": "0", "checksum": "on", "special_small_blocks": "0", "redundant_metadata": "all", "volmode": "default", "devices": "on", "keyformat": "none", "logicalreferenced": "12K", "acltype": "off", "nbmand": "off", "context": "none", "encryption": "off", "snapdir": "hidden"}}

```
(the most pertinent parameter is `mountpoint`)

## XCP-ng RAID status check
### Example
```
$ xe host-call-plugin host-uuid=${HOST_UNDER_TEST_UUID} plugin=raid.py fn=check_raid_pool
{"status": true, "result": {"raid": {"Working Devices": "2", "Raid Devices": "2", "Raid Level": "raid1", "Creation Time": "Wed Jul 17 13:29:42 2019", "Used Dev Size": "52428672 (50.00 GiB 53.69 GB)", "UUID": "1766eb6e:85762159:4c98b42e:2da92c97", "Array Size": "52428672 (50.00 GiB 53.69 GB)", "Failed Devices": "0", "State": "clean", "Version": "1.0", "Events": "44", "Persistence": "Superblock is persistent", "Spare Devices": "0", "Name": "localhost:127", "Active Devices": "2", "Total Devices": "2", "Update Time": "Tue Jul 30 01:58:48 2019"}, "volumes": [["0", "8", "0", "0", "active sync", "/dev/sda"], ["1", "8", "16", "1", "active sync", "/dev/sdb"]]}}
```


## XCP-ng updater

A xapi plugin to invoke yum commands on the hosts.

### Examples

Checking for updates:

```
$ xe host-call-plugin host-uuid=${HOST_UNDER_TEST_UUID} plugin=updater.py fn=check_update

{"result": [{"release": "4.2", "fullName": "xen-dom0-libs-4.7.5-4.2.x86_64", "version": "4.7.5", "arch": "x86_64", "name": "xen-dom0-libs"}, {"release": "4.2", "fullName": "xen-dom0-tools-4.7.5-4.2.x86_64", "version": "4.7.5", "arch": "x86_64", "name": "xen-dom0-tools"}, {"release": "4.2", "fullName": "xen-tools-4.7.5-4.2.x86_64", "version": "4.7.5", "arch": "x86_64", "name": "xen-tools"}, {"release": "22.xs1", "fullName": "2:microcode_ctl-2.1-22.xs1.x86_64", "version": "2.1", "arch": "x86_64", "name": "microcode_ctl"}, {"release": "4.2", "fullName": "xen-hypervisor-4.7.5-4.2.x86_64", "version": "4.7.5", "arch": "x86_64", "name": "xen-hypervisor"}, {"release": "4.2", "fullName": "xen-libs-4.7.5-4.2.x86_64", "version": "4.7.5", "arch": "x86_64", "name": "xen-libs"}]}
```

 Start the updates:


```
$ xe host-call-plugin host-uuid=${HOST_UNDER_TEST_UUID} plugin=updater.py fn=update
```

### Proxy configuration

#### `get_proxies()`:

```
$ xe host-call-plugin host-uuid=${HOST_UNDER_TEST_UUID} plugin=updater.py fn=get_proxies
{"xcp-ng-base": "http://192.168.100.82:3142", "xcp-ng-updates": "_none_", "xcp-ng-extras": "_none_", "xcp-ng-extras_testing": "_none_", "xcp-ng-updates_testing": "http://192.168.100.82:3142"}

```
The answer is a JSON dict section -> proxy. The dict is empty if the file couldn't be read.


#### `set_proxies(proxies)`:

```
$ echo $JSON_PROXY
{"xcp-ng-base": "http://192.168.100.82:3142", "xcp-ng-updates": "_none_", "xcp-ng-extras": "_none_", "xcp-ng-extras_testing": "_none_", "xcp-ng-updates_testing": "http://192.168.100.82:3142"}
$ xe host-call-plugin host-uuid=${HOST_UNDER_TEST_UUID} plugin=updater.py fn=set_proxies args:proxies="'$JSON_PROXY'"
{"status": true}
```
The `proxies` parameter is a JSON dict section-> proxy for the list of sections whose proxy we want to alter.

The returned value should be the JSON value `{"status": true}` or `{"status": false, "error": "<message>"}`.
