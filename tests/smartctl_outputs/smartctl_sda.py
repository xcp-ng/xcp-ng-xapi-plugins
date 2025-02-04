# Unlike other logs this one has been truncated.
# But it corresponds to reality
INFO_SDA = """{
  "json_format_version": [
    1,
    0
  ],
  "smartctl": {
    "version": [
      7,
      0
    ],
    "svn_revision": "4883",
    "platform_info": "x86_64-linux-4.19.0+1",
    "build_info": "(local build)",
    "argv": [
      "smartctl",
      "-j",
      "-a",
      "/dev/sda"
    ],
    "exit_status": 0
  }
}"""

HEALTH_SDA = """{
  "json_format_version": [
    1,
    0
  ],
  "smartctl": {
    "version": [
      7,
      0
    ],
    "svn_revision": "4883",
    "platform_info": "x86_64-linux-4.19.0+1",
    "build_info": "(local build)",
    "argv": [
      "smartctl",
      "-j",
      "-H",
      "/dev/sda"
    ],
    "exit_status": 0
  },
  "device": {
    "name": "/dev/sda",
    "info_name": "/dev/sda [SAT]",
    "type": "sat",
    "protocol": "ATA"
  },
  "smart_status": {
    "passed": true
  }
}"""
