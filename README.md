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

This XAPI plugin provides information and health details for the physical disks on the host. 

It uses the `smartctl --scan` command to retrieve the list of devices. For devices managed by
MegaRAID, the device names may be identical. To handle this, the plugin returns information
for each unique "name:type" pair.

The plugin parses the JSON output from the `smartctl` command to gather information and health
data. As a result, it requires a version of `smartctl` capable of producing JSON output.
This functionality is available in **XCP-ng 8.3**, but not in **XCP-ng 8.2**.

### `information`:

This function returns information about all detected devices. The JSON can be quite big.

```
xe host-call-plugin host-uuid=<uuid> plugin=smartctl.py fn=information
{"/dev/nvme1:nvme": {"smart_status": {"nvme": {"value": 0}, "passed": true}, "nvme_controller_id": 0, "smartctl": {"build_info": "(local build)", "exit_status": 0, "argv": ["smartctl", "-j", "-a", "-d", "nvme",
 "/dev/nvme1"], "version": [7, 0], "svn_revision": "4883", "platform_info": "x86_64-linux-4.19.0+1"}, "temperature": {"current": 32}, ...
```

### `health`:

This function returns health status per detected devices.

```
xe host-call-plugin host-uuid=<uuid>  plugin=smartctl.py fn=health
{"/dev/nvme1:nvme": "PASSED", "/dev/sda:scsi": "PASSED", "/dev/nvme0:nvme": "PASSED", "/dev/bus/0:megaraid,1": "PASSED", "/dev/bus/0:megaraid,0": "PASSED"}
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

## Ipmitool

A xapi plugin that uses `ipmitool` to get information about sensors and the IPMI server. Before
running the commands you need to ensure that your system have support for IPMI.

### `is_ipmi_device_available`

Returns `true` if IPMI device is found and `ipmitool` can be used. If it could not open device at `/dev/ipmi*`
it returns `false`. In that case you need to ensure the IPMI module is loaded and that your system
supports IPMI. Others unexpected errors raise a XenAPIPlugin error.

```
$ xe host-call-plugin host-uuid=<uuid> plugin=ipmitool.py fn=is_ipmi_device_available
false
```

If `true` is returned you should be able to run `get_all_sensors`, `get_sensor`
or `get_ipmi_lan` without raising a XenAPIPlugin error.

### `get_all_sensors`

Returns a JSON containing all sensor data repository entries and readings or raise a XenAPIPlugin error.
```
$ xe host-call-plugin host-uuid=<uuid> plugin=ipmitool.py fn=get_all_sensors
[
 {"name": "Fan1A", "value": "10920 RPM", "event": "ok"},
 {"name": "Fan2A", "value": "10800 RPM", "event": "ok"},
 {"name": "Inlet Temp", "value": "23 degrees C", "event": "ok"},
 {"name": "Exhaust Temp", "value": "28 degrees C", "event": "ok"},
 {"name": "Temp", "value": "38 degrees C", "event": "ok"}
 {"name": "PFault Fail Safe", "value": "Not Readable", "event": "ns"}
 ...
]
```

### `get_sensor`

Returns a JSON containing detailed information about the sensors passed as paramaters
or raise an XenAPIPlugin error. The names of the sensors can be found by running `get_all_sensors`
function. If a wrong sensor name is passed an error is logged in `/var/log/ipmitool-xapi-plugin-plugin.log`
and the sensor is skipped.

```
$ xe host-call-plugin host-uuid=<uuid> plugin=ipmitool.py fn=get_sensor args:sensors="Fan7B,PFault Fail Safe"
[
  {
    "name": "Fan7B",
    "info": [{"name": "Sensor ID", "value": "Fan7B (0x3d)"}, {"name": "Entity ID", "value": "7.1 (System Board)"}, {"name": "Sensor Type (Threshold)", "value": "Fan (0x04)"}, {"name": "Sensor Reading", "value": "10320 (+/- 120) RPM"}, {"name": "Status", "value": "ok"}, {"name": "Nominal Reading", "value": "6720.000"}, {"name": "Normal Minimum", "value": "16680.000"}, {"name": "Normal Maximum", "value": "23640.000"}, {"name": "Lower critical", "value": "720.000"}, {"name": "Lower non-critical", "value": "840.000"}, {"name": "Positive Hysteresis", "value": "120.000"}, {"name": "Negative Hysteresis", "value": "120.000"}, {"name": "Minimum sensor range", "value": "Unspecified"}, {"name": "Maximum sensor range", "value": "Unspecified"}, {"name": "Event Message Control", "value": "Per-threshold"}, {"name": "Readable Thresholds", "value": "lcr lnc"}, {"name": "Settable Thresholds", "value": ""}, {"name": "Threshold Read Mask", "value": "lcr lnc"}, {"name": "Assertion Events", "value": ""}, {"name": "Assertions Enabled", "value": "lnc- lcr-"}, {"name": "Deassertions Enabled", "value": "lnc- lcr-"}]
  },
  {
    "name": "PFault Fail Safe",
    "info": [{"name": "Sensor ID", "value": "PFault Fail Safe (0x66)"}, {"name": "Entity ID", "value": "7.1 (System Board)"}, {"name": "Sensor Type (Discrete)", "value": "Voltage (0x02)"}, {"name": "Sensor Reading", "value": "No Reading"}, {"name": "Event Message Control", "value": "Per-threshold"}, {"name": "OEM", "value": "0"}]
  }
]
```

### `get_ipmi_lan`

Returns JSON that contains information about the configuration of the network related to the IPMI server
or raise a XenAPIPlugin error.

```
$ xe host-call-plugin host-uuid=<uuid> plugin=ipmitool.py fn=get_ipmi_lan
[
  {
    "name": "IP Address Source",
    "value": "Static Address"
  },
  {
    "name": "IP Address",
    "value": "1.2.3.4"
  },
  {
    "name": "Subnet Mask",
    "value": "255.255.255.0"
  },
  {
    "name": "MAC Address",
    "value": "a8:ac:a2:a5:a0:ae"
  },
  ...
]

```

## Service

A xapi plugin that uses `systemctl` to manage services.

### `start_service`

Start a service if it is not already running.

```
$ xe host-call-plugin host-uuid<uuid> plugin=service.py fn=start_service args:service=<service>
```

### `stop_service`

Stop a service if it is currently running.

```
$ xe host-call-plugin host-uuid<uuid> plugin=service.py fn=stop_service args:service=<service>
```

### `restart_service`

Stop a service if it is running and then start it.

```
$ xe host-call-plugin host-uuid<uuid> plugin=service.py fn=restart_service args:service=<service>
```

### `try_restart_service`

Restart a service only if it is already running.

```
$ xe host-call-plugin host-uuid<uuid> plugin=service.py fn=try_restart_service args:service=<service>
```


### `sdncontroller`

Add, delete rules and dump openflow rules.

#### Add rule

Parameters for adding a rule:
- *bridge* :  The name of the bridge to add rule to.
- *priority* (optional): A number between 0 and 65535 for the rule priority.
- *mac* (optional): The MAC address of the VIF to create the rule for, if not
  specified, a network-wide rule will be created.
- *iprange*: An IP or range of IPs in CIDR notation, for example `192.168.1.0/24`.
- *direction*: can be **from**, **to** or **from/to**
  - *to*: means the parameters for **port** and **iprange** are to be used as destination
  - *from*: means they will be use as source
  - *from/to*: 2 rules will be created, one per direction
- *protocol*: IP, TCP, UDP, ICMP or ARP
- *port*: required for TCP/UDP protocol
- *allow*: If set to false the packets are dropped.

```
$ xe host-call-plugin host-uuid<uuid> plugin=sdncontroller.py \
  fn=add-rule                   \
  args:bridge="xenbr0"          \
  args:priority="100"           \
  args:mac="6e:0b:9e:72:ab:c6"  \
  args:iprange="192.168.1.0/24" \
  args:direction="from/to"      \
  args:protocol="tcp"           \
  args:port="22"                \
  args:allow="false"
```

##### Delete rule

Parameters for removing a rule:
- *bridge* :  The name of the bridge to delete the rule from.
- *mac* (optional): The MAC address of the VIF to delete the rule for.
- *iprange*: An IP or range of IPs in CIDR notation, for example `192.168.1.0/24`.
- *direction*: can be **from**, **to** or **from/to**
  - *to*: means the parameters for **port** and **iprange** are to be used as destination
  - *from*: means they will be use as source
  - *from/to*: 2 rules will be created, one per direction
- *protocol*: IP, TCP, UDP, ICMP or ARP
- *port*: required for TCP/UDP protocol

```
$ xe host-call-plugin host-uuid<uuid> plugin=sdncontroller.py \
  fn=del-rule                   \
  args:bridge="xenbr0"          \
  args:mac="6e:0b:9e:72:ab:c6"  \
  args:iprange="192.168.1.0/24" \
  args:direction="from/to"      \
  args:protocol="tcp"           \
  args:port="22"
```

##### Dump flows

- This command will return all flows entries in the bridge passed as a parameter.
```
$ xe host-call-plugin host-uuid=<uuid> plugin=sdncontroller.py fn=dump-flows args:bridge=xenbr0 | jq .
{
  "returncode": 0,
  "command": [
    "ovs-ofctl",
    "dump-flows",
    "xenbr0"
  ],
  "stderr": "",
  "stdout": "NXST_FLOW reply (xid=0x4):\n cookie=0x0, duration=248977.339s, table=0, n_packets=24591786, n_bytes=3278442075, idle_age=0, hard_age=65534, priority=0 actions=NORMAL\n"
}
```

- This error is raised when the bridge parameter is missing:
```
$ xe host-call-plugin host-uuid=<uuid> plugin=sdncontroller.py fn=dump-flows | jq .
{
  "returncode": 1,
  "command": [
    "ovs-ofctl",
    "dump-flows"
  ],
  "stderr": "bridge parameter is missing",
  "stdout": ""
}
```

- If the bridge is unknown, the following error will occur:
```
$ xe host-call-plugin host-uuid=<uuid> plugin=sdncontroller.py args:bridge=xenbr10 fn=dump-flows | jq .
{
  "returncode": 1,
  "command": [
    "ovs-ofctl",
    "dump-flows",
    "xenbr10"
  ],
  "stderr": "ovs-ofctl: xenbr10 is not a bridge or a socket\n",
  "stdout": ""
}
```

## Tests

To run the plugins' unit tests you'll need to install `pytest`, `pyfakefs` and `mock`.

To run all tests you can run:
```py
pytest tests/
```
