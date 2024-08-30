# XCP-ng xapi plugins

This repo hosts all the extra plugins installed in a XCP-ng host in `/etc/xapi.d/plugins`.

## Return format

A plugin should respect this return format:
- Success: return a string (can be empty) or a JSON string representing the result of the command given to the plugin
- Error: raise a `XenAPIPlugin.Failure` describing the error, to do that: either raise the `XenAPIPlugin.Failure` exception directly or use `error_wrapped` from `xcpngutils`

## XCP-ng ZFS pool list

A xapi plugin to discover ZFS pools present on the host.

### `list_zfs_pools`:
```
$ xe host-call-plugin host-uuid=<uuid> plugin=zfs.py fn=list_zfs_pools
{"tank": {"setuid": "on", "relatime": "off", "referenced": "24K", "written": "24K", "zoned": "off", "primarycache": "all", "logbias": "latency", "creation": "Mon May 27 17:24 2019", "sync": "standard", "snapdev": "hidden", "dedup": "off", "sharenfs": "off", "usedbyrefreservation": "0B", "sharesmb": "off", "createtxg": "1", "canmount": "on", "mountpoint": "/tank", "casesensitivity": "sensitive", "utf8only": "off", "xattr": "on", "dnodesize": "legacy", "mlslabel": "none", "objsetid": "54", "defcontext": "none", "rootcontext": "none", "mounted": "yes", "compression": "off", "overlay": "off", "logicalused": "126K", "usedbysnapshots": "0B", "filesystem_count": "none", "copies": "1", "snapshot_limit": "none", "aclinherit": "restricted", "compressratio": "1.00x", "readonly": "off", "version": "5", "normalization": "none", "filesystem_limit": "none", "type": "filesystem", "secondarycache": "all", "refreservation": "none", "available": "17.4G", "used": "364K", "exec": "on", "refquota": "none", "refcompressratio": "1.00x", "quota": "none", "keylocation": "none", "snapshot_count": "none", "fscontext": "none", "vscan": "off", "reservation": "none", "atime": "on", "recordsize": "128K", "usedbychildren": "340K", "usedbydataset": "24K", "guid": "656061077639704004", "pbkdf2iters": "0", "checksum": "on", "special_small_blocks": "0", "redundant_metadata": "all", "volmode": "default", "devices": "on", "keyformat": "none", "logicalreferenced": "12K", "acltype": "off", "nbmand": "off", "context": "none", "encryption": "off", "snapdir": "hidden"}}

```
(the most pertinent parameter is `mountpoint`)

## XCP-ng LVM

A xapi plugin to list, create and destroy PVs, VGs and LVMs on a host.

### Helpers to list groups and volumes

#### `list_physical_volumes`:
```
$ xe host-call-plugin host-uuid=<uuid> plugin=lvm.py fn=list_physical_volumes
{"/dev/nvme0n1": {"attributes": "a--", "capacity": 1000203091968, "free": 0, "vg_name": "local_group", "format": "lvm2"}}
```

#### `list_volume_groups`:
```
$ # `vg_name` arg is optional, it's used to limit the results.
$ xe host-call-plugin host-uuid=<uuid> plugin=lvm.py fn=list_volume_groups args:vg_name=<group>
{"local_group": {"capacity": 1000203091968, "sn_count": 0, "free": 0, "pv_count": 1, "lv_count": 4, "attributes": "wz--n-"}}
```

#### `list_logical_volumes`:
```
$ # Like for `list_volume_groups`, `vg_name` arg is optional.
$ xe host-call-plugin host-uuid=<uuid> plugin=lvm.py fn=list_logical_volumes args:vg_name=<group>
{"thin_device": {"attributes": "twi-aotz--", "capacity": 999951433728, "pool": "", "vg_name": "local_group"}, "xcp-persistent-redo-log_00000": {"attributes": "Vwi-aotz--", "capacity": 272629760, "pool": "thin_device", "vg_name": "local_group"}, "xcp-persistent-ha-statefile_00000": {"attributes": "Vwi-aotz--", "capacity": 8388608, "pool": "thin_device", "vg_name": "local_group"}, "xcp-persistent-database_00000": {"attributes": "Vwi-aotz--", "capacity": 1077936128, "pool": "thin_device", "vg_name": "local_group"}}
```

### Creation of groups

#### `create_physical_volume`:
```
$ # A device comma-separated list of devices is necessary.
$ # If a FS already exists, it can be ignored using a boolean arg: `ignore_existing_filesystems`.
$ # Also it's possible to ignore FS and other PV errors using the boolean arg: `force`.
$ xe host-call-plugin host-uuid=<uuid> plugin=lvm.py fn=create_physical_volume args:devices=<device_list>
{}
```

#### `create_volume_group`:
```
$ # Note: the `force` arg can be used to recreate the VG.
$ xe host-call-plugin host-uuid=<uuid> plugin=lvm.py fn=create_volume_group args:vg_name=<group> devices=<device_list>
{}
```

#### `create_thin_pool`:
```
$ # This method is used to create a logical thin volume in a VG using 100% of the free space.
$ xe host-call-plugin host-uuid=<uuid> plugin=lvm.py fn=create_thin_pool args:vg_name=<group> lv_name=<logical_name>
{}
```

### Destruction

#### `destroy_volume_group`:
```
$ # Note: the `force` arg can be used to remove existing volumes.
$ xe host-call-plugin host-uuid=<uuid> plugin=lvm.py fn=destroy_volume_group args:vg_name=<group>
{}
```

## XCP-ng RAID status check

A xapi plugin to get the current state of the raid devices on the host.
### `check_raid_pool`:
```
$ xe host-call-plugin host-uuid=<uuid> plugin=raid.py fn=check_raid_pool
{"raid": {"Working Devices": "2", "Raid Devices": "2", "Raid Level": "raid1", "Creation Time": "Wed Jul 17 13:29:42 2019", "Used Dev Size": "52428672 (50.00 GiB 53.69 GB)", "UUID": "1766eb6e:85762159:4c98b42e:2da92c97", "Array Size": "52428672 (50.00 GiB 53.69 GB)", "Failed Devices": "0", "State": "clean", "Version": "1.0", "Events": "44", "Persistence": "Superblock is persistent", "Spare Devices": "0", "Name": "localhost:127", "Active Devices": "2", "Total Devices": "2", "Update Time": "Tue Jul 30 01:58:48 2019"}, "volumes": [["0", "8", "0", "0", "active sync", "/dev/sda"], ["1", "8", "16", "1", "active sync", "/dev/sdb"]]}
```

## XCP-ng updater

A xapi plugin to invoke yum commands on the host.

### Update management
#### `check_update`:
Return an array of the packages to update on the host.
```
$ xe host-call-plugin host-uuid=<uuid> plugin=updater.py fn=check_update

{"result": [{"release": "4.2", "fullName": "xen-dom0-libs-4.7.5-4.2.x86_64", "version": "4.7.5", "arch": "x86_64", "name": "xen-dom0-libs"}, {"release": "4.2", "fullName": "xen-dom0-tools-4.7.5-4.2.x86_64", "version": "4.7.5", "arch": "x86_64", "name": "xen-dom0-tools"}, {"release": "4.2", "fullName": "xen-tools-4.7.5-4.2.x86_64", "version": "4.7.5", "arch": "x86_64", "name": "xen-tools"}, {"release": "22.xs1", "fullName": "2:microcode_ctl-2.1-22.xs1.x86_64", "version": "2.1", "arch": "x86_64", "name": "microcode_ctl"}, {"release": "4.2", "fullName": "xen-hypervisor-4.7.5-4.2.x86_64", "version": "4.7.5", "arch": "x86_64", "name": "xen-hypervisor"}, {"release": "4.2", "fullName": "xen-libs-4.7.5-4.2.x86_64", "version": "4.7.5", "arch": "x86_64", "name": "xen-libs"}]}
```

#### `update`:
Update the host.
```
$ xe host-call-plugin host-uuid=<uuid> plugin=updater.py fn=update
```

#### `query_installed`:
Return a JSON object of the installed packages given in arguments with an empty value string for not installed ones.
```
$ xe host-call-plugin host-uuid=<uuid> plugin=updater.py fn=query_installed args:packages=sm,sm-rawhba,invalid
{"sm-rawhba": "sm-rawhba-2.30.8-2.3.0.linstor.1.xcpng8.2.x86_64", "invalid": "", "sm": "sm-2.30.8-10.1.0.linstor.1.xcpng8.2.x86_64"}
```

### Proxy configuration

#### `get_proxies()`:
```
$ xe host-call-plugin host-uuid=<uuid> plugin=updater.py fn=get_proxies
{"xcp-ng-base": "http://192.168.100.82:3142", "xcp-ng-updates": "_none_", "xcp-ng-extras": "_none_", "xcp-ng-extras_testing": "_none_", "xcp-ng-updates_testing": "http://192.168.100.82:3142"}

```
The answer is a JSON dict section -> proxy. The dict is empty if the file couldn't be read.


#### `set_proxies(proxies)`:
```
$ echo $JSON_PROXY
{"xcp-ng-base": "http://192.168.100.82:3142", "xcp-ng-updates": "_none_", "xcp-ng-extras": "_none_", "xcp-ng-extras_testing": "_none_", "xcp-ng-updates_testing": "http://192.168.100.82:3142"}
$ xe host-call-plugin host-uuid=<uuid> plugin=updater.py fn=set_proxies args:proxies="'$JSON_PROXY'"
```
The `proxies` parameter is a JSON dict section-> proxy for the list of sections whose proxy we want to alter.

The returned value should be an empty string in case of success.

## LSBLK parser

A xapi plugin to get the lsblk output on the host.

### `list_block_devices`:
```
$ xe host-call-plugin host-uuid=<uuid> plugin=lsblk.py fn=list_block_devices
{
  "blockdevices": [{"kname": "sdb", "name": "sdb", "pkname": "", "mountpoint": "", "ro": "0", "type": "disk", "size": "64424509440"}, {"kname": "sda", "name": "sda", "pkname": "", "mountpoint": "", "ro": "0", "type": "disk", "children": [{"kname": "sda4", "name": "sda4", "pkname": "sda", "mountpoint": "", "ro": "0", "type": "part", "size": "536870912"}, {"kname": "sda2", "name": "sda2", "pkname": "sda", "mountpoint": "", "ro": "0", "type": "part", "size": "19327352832"}, {"kname": "sda5", "name": "sda5", "pkname": "sda", "mountpoint": "/var/log", "ro": "0", "type": "part", "size": "4294967296"}, {"kname": "sda3", "name": "sda3", "pkname": "sda", "mountpoint": "", "ro": "0", "type": "part", "children": [{"kname": "dm-0", "name": "XSLocalEXT--1fad55d2--4f07--8145--c78a--297b173e06b0-1fad55d2--4f07--8145--c78a--297b173e06b0", "pkname": "sda3", "mountpoint": "/run/sr-mount/1fad55d2-4f07-8145-c78a-297b173e06b0", "ro": "0", "type": "lvm", "size": "19847446528"}], "size": "19863158272"}, {"kname": "sda1", "name": "sda1", "pkname": "sda", "mountpoint": "/", "ro": "0", "type": "part", "size": "19327352832"}, {"kname": "sda6", "name": "sda6", "pkname": "sda", "mountpoint": "[SWAP]", "ro": "0", "type": "part", "size": "1073741824"}], "size": "64424509440"}]
}
```
- `blockdevices` is a json representation of the blockdevices.
- `stdout` is the raw output.

## Smartctl parser

A xapi plugin to get information and health of physical disks on the host
### `information`:
```
xe host-call-plugin host-uuid=<uuid> plugin=smartctl.py fn=information
{"/dev/sdf": {"power_on_time": {"hours": 9336}, "ata_version": {"minor_value": 94, "string": "ACS-4 T13/BSR INCITS 529 revision 5", "major_value": 2556}, "form_factor": {"ata_value": 3, "name": "2.5 inches"}, "firmware_version": "SVQ02B6Q", "wwn": {"oui": 9528, "naa": 5, "id": 65536604056}, "smart_status": {"passed": true}, "smartctl": {"build_info": "(local build)", "exit_status": 0, "argv": ["smartctl", "-j", "-a", "/dev/sdf"], "version": [7, 0], "svn_revision": "4883", "platform_info": "x86_64-linux-4.19.0+1"}, "temperature": {"current": 35}, "rotation_rate": 0, "interface_speed": {"current": {"sata_value": 3, "units_per_second": 60, "string": "6.0 Gb/s", "bits_per_unit": 100000000}, [...] }
```

### `health`:
```
xe host-call-plugin host-uuid=<uuid>  plugin=smartctl.py fn=health
{"/dev/sdf": "PASSED", "/dev/sdg": "PASSED", "/dev/sdd": "PASSED", "/dev/sde": "PASSED", "/dev/sdb": "PASSED", "/dev/sdc": "PASSED", "/dev/sda": "PASSED"}
```

## IPMI-sensors parser
A xapi plugin to get information about the host via the BMC
### `get_info`:
```
xe host-call-plugin host-uuid=<uuid>  plugin=2crsi-sensors.py fn="get_info"
[{"Name": "Outlet_Temp", "Event": "'OK'", "Units": "C", "Reading": "32.00", "Type": "Temperature"}, {"Name": "CPU0_Temp", "Event": "'OK'", "Units": "C", "Reading": "63.00", "Type": "Temperature"}, {"Name": "CPU1_Temp", "Event": "'OK'", "Units": "C", "Reading": "59.00", "Type": "Temperature"}, {"Name": "CPU0_DIMM_T", "Event": "'OK'", "Units": "C", "Reading": "38.00", "Type": "Temperature"}, {"Name": "CPU1_DIMM_T", "Event": "'OK'", "Units": "C", "Reading": "37.00", "Type": "Temperature"}, {"Name": "PSU_Inlet_Temp", "Event": "'OK'", "Units": "C", "Reading": "36.00", "Type": "Temperature"}, {"Name": "CPU0_VR_Temp", "Event": "'OK'", "Units": "C", "Reading": "43.00", "Type": "Temperature"}, {"Name": "CPU1_VR_Temp", "Event": "'OK'", "Units": "C", "Reading": "43.00", "Type": "Temperature"}, {"Name": "OCP_NIC_Temp", "Event": "'OK'", "Units": "C", "Reading": "60.00", "Type": "Temperature"} [...] }
```

### `get_ip`:
```
xe host-call-plugin host-uuid=<uuid>  plugin=2crsi-sensors.py fn="get_ip"
10.10.1.191
```

## Netdata

A xapi plugin to install and get api keys of netdata on the host.

### `is_netdata_installed`:
Returns whether or not the netdata packages are installed:
```
$ xe host-call-plugin host-uuid=<uuid> plugin=netdata.py fn=is_netdata_installed
true
```

### `install_netdata`:
Install the netdata packages on the host, returns "true" in case of success.
```
$ xe host-call-plugin host-uuid=<uuid> plugin=netdata.py fn=install_netdata
true
```

### `get_netdata_api_key`:
Return the net data api key on the host, return an empty string if netdata is not configured.
```
$ xe host-call-plugin host-uuid=<uuid> plugin=netdata.py fn=get_netdata_api_key
<key>
```

## Hyperthreading

A xapi plugin to find out if hyperthreading is enabled on the host.

### `get_hyperthreading`:
Return whether hyperthreading is enabled on the host.
```
$ xe host-call-plugin host-uuid=<uuid> plugin=hyperthreading.py fn=get_hyperthreading
true
```

## Tests

To run the plugins' unit tests you'll need to install `pytest`, `pyfakefs` and `mock`.

To run all tests you can run:
```py
pytest tests/
```
