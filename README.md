#XCP-ng updater

A xapi plugin to invoke yum commands on the hosts.

examples: 
 - ```xe host-call-plugin host-uuid=${HOST_UNDER_TEST_UUID} plugin=updater.py fn=check_update```
 
 => 
 ```json
 {"result": [{"release": "4.2", "fullName": "xen-dom0-libs-4.7.5-4.2.x86_64", "version": "4.7.5", "arch": "x86_64", "name": "xen-dom0-libs"}, {"release": "4.2", "fullName": "xen-dom0-tools-4.7.5-4.2.x86_64", "version": "4.7.5", "arch": "x86_64", "name": "xen-dom0-tools"}, {"release": "4.2", "fullName": "xen-tools-4.7.5-4.2.x86_64", "version": "4.7.5", "arch": "x86_64", "name": "xen-tools"}, {"release": "22.xs1", "fullName": "2:microcode_ctl-2.1-22.xs1.x86_64", "version": "2.1", "arch": "x86_64", "name": "microcode_ctl"}, {"release": "4.2", "fullName": "xen-hypervisor-4.7.5-4.2.x86_64", "version": "4.7.5", "arch": "x86_64", "name": "xen-hypervisor"}, {"release": "4.2", "fullName": "xen-libs-4.7.5-4.2.x86_64", "version": "4.7.5", "arch": "x86_64", "name": "xen-libs"}]}
```
 
 - ```xe host-call-plugin host-uuid=${HOST_UNDER_TEST_UUID} plugin=updater.py fn=update```
