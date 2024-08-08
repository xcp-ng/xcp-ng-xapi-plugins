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

## XCP-ng Kalray DPU

A xapi plugin to get information about raids, logical volume store (LVS) and
devices that are present on the Kalray DPU. It also allow the management of
logical volumes (LV): creation and deletion. Parameters depends of the name of
the command some are always available:
  - *username*: username to use to connect to DPU (required)
  - *password*: password to connect to DPU (required)
  - *server*: IP of the server for configuring the DPU (default: localhost)
  - *port*: Port to use (default: 8080)
  - *timeout*: timeout in second (default: 60.0)

### Command details

- Currently the Kalray DPU is still in developpement and there are some
restrictions:
    - To be able to expose virtual functions the Kalray poller expects
    specific names for the logical volume store and for the volume. It
    depends of the configuration used in `/etc/kalray/0000:XX:00.1.conf`.
    - By default the logical volume store name **must be** `lvs`.
    - By default the volume must start with `volume_`.
    - With the current DPU only four virtual functions (and so only four NVMe
    disks) can be created and so you can only use the following name:
        - `volume_09`
        - `volume_10`
        - `volume_11`
        - `volume_12`
    - Only volumes can be deleted.

#### Block devices

##### Get the list of devices on the Kalray DPU
```
$ xe host-call-plugin host-uuid=<uuid> plugin=kalray_dpu.py fn=get_devices \
    args:username=<username> args:password=<password>
[{"name": "HotInNvmeWDS500AFY0-22050C800415n1", "aliases": [], "product_name": "NVMe disk", "block_size": 512, "num_blocks": 976773168, "uuid": "e8238fa6-bf53-0001-001b-448b45afa6a7", "assigned_rate_limits": {"rw_ios_per_sec": 0, "rw_mbytes_per_sec": 0, "r_mbytes_per_sec": 0, "w_mbytes_per_sec": 0}, "claimed": false, "zoned": false, "supported_io_types": {"read": true, "write": true, "unmap": true, "write_zeroes": true, "flush": true, "reset": true, "nvme_admin": true, "nvme_io": true}, "driver_specific": {"nvme": [{"pci_address": "0000:00:00.0", "trid": {"trtype": "PCIe", "traddr": "0000:00:00.0"}, "ctrlr_data": {"cntlid": 8224, "vendor_id": "0x15b7", "model_number": "WDS500G1X0E-00AFY0", "serial_number": "22050C800415", "firmware_revision": "614900WD", "subnqn": "nqn.2018-01.com.wdc:nguid:E8238FA6BF53-0001-001B448B45AFA6A7", "oacs": {"security": 1, "format": 1, "firmware": 1, "ns_manage": 0}, "multi_ctrlr": false, "ana_reporting": false}, "vs": {"nvme_version": "1.4"}, "ns_data": {"id": 1, "can_share": false}, "security": {"opal": false}}], "mp_policy": "active_passive"}}, {"name": "HotInNvmeWDS500AFY0-22050C800378n1", "aliases": [], "product_name": "NVMe disk", "block_size": 512, "num_blocks": 976773168, "uuid": "e8238fa6-bf53-0001-001b-448b45afe330", "assigned_rate_limits": {"rw_ios_per_sec": 0, "rw_mbytes_per_sec": 0, "r_mbytes_per_sec": 0, "w_mbytes_per_sec": 0}, "claimed": false, "zoned": false, "supported_io_types": {"read": true, "write": true, "unmap": true, "write_zeroes": true, "flush": true, "reset": true, "nvme_admin": true, "nvme_io": true}, "driver_specific": {"nvme": [{"pci_address": "0000:00:01.0", "trid": {"trtype": "PCIe", "traddr": "0000:00:01.0"}, "ctrlr_data": {"cntlid": 8224, "vendor_id": "0x15b7", "model_number": "WDS500G1X0E-00AFY0", "serial_number": "22050C800378", "firmware_revision": "614900WD", "subnqn": "nqn.2018-01.com.wdc:nguid:E8238FA6BF53-0001-001B448B45AFE330", "oacs": {"security": 1, "format": 1, "firmware": 1, "ns_manage": 0}, "multi_ctrlr": false, "ana_reporting": false}, "vs": {"nvme_version": "1.4"}, "ns_data": {"id": 1, "can_share": false}, "security": {"opal": false}}], "mp_policy": "active_passive"}}]
```

#### RAID

##### Create a raid on the Kalray DPU
- Supported RAID are raid0, raid1 and raid10
```
$ xe host-call-plugin host-uuid=<uuid> plugin=kalray_dpu.py fn=raid_create \
    args:username=<username> args:password=<password> \
    args:base_bdevs=HotInNvmeWDS500AFY0-22050C800415n1,HotInNvmeWDS500AFY0-22050C800378n1 \
    args:raid_name=raid0 \
    args:raid_level=raid0
true
```

##### Get the list of raids on the Kalray DPU
```
$ xe host-call-plugin host-uuid=<uuid> plugin=kalray_dpu.py fn=get_raids \
    args:username=<username> args:password=<password>
["raid0"]
```

#### Logical Volume Store (LVS)
##### Create an LVS on the Kalray DPU
```
$ xe host-call-plugin host-uuid=<uuid> plugin=kalray_dpu.py fn=lvs_create \
    args:username=<username> args:password=<password> \
    args:lvs_name=lvs \
    args:bdev_name=raid0
"6fb90332-56e4-4d03-aa6a-f858a2c2ca97"
```

##### Get the list of LVS on the Kalray DPU
```
$ xe host-call-plugin host-uuid=<uuid> plugin=kalray_dpu.py fn=get_lvs \
    args:username=<username> args:password=<password>
[{"uuid": "6fb90332-56e4-4d03-aa6a-f858a2c2ca97", "name": "lvs", "passive": false, "base_bdev": "raid0", "total_data_clusters": 29804, "free_clusters": 29772, "block_size": 512, "cluster_size": 33554432}]
```

#### Logical Volume (LVOL)
##### Create a new logical volume
```
$ xe host-call-plugin host-uuid=<uuid> plugin=kalray_dpu.py fn=lvol_create \
    args:username=<username> args:password=<password> \
    args:lvol_name=volume_09 \
    args:lvol_size_in_bytes=1073741824 \
    args:lvs_name=lvs
"6c84b44c-a61b-41a4-8b19-32ab643b57d9"
```

##### Delete a logical volume
- The name of the volume to be deleted is not the same than the one used to
create it. You need to prepend the name of the logical volume store as shown
in the example:

```
$ xe host-call-plugin host-uuid=<uuid> plugin=kalray_dpu.py fn=lvol_delete \
    args:username=<username> args:password=<password> \
    args:lvol_name=lvs/volume_09
true
```

## Tests

To run the plugins' unit tests you'll need to install `pytest`, `pyfakefs` and `mock`.

To run all tests you can run:
```py
pytest tests/
```
