# Outputs are from real hardware:
#   INFO -> smartctl -j -a -d nvme /dev/nvme1 | jq .
#   HEALTH -> smartctl -j -H -d nvme /dev/nvme1 | jq .
INFO_NVME1 = """{
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
      "-d",
      "nvme",
      "/dev/nvme1"
    ],
    "exit_status": 0
  },
  "device": {
    "name": "/dev/nvme1",
    "info_name": "/dev/nvme1",
    "type": "nvme",
    "protocol": "NVMe"
  },
  "model_name": "INTEL SSDPED1D280GA",
  "serial_number": "PHMB7466015Y280CGN",
  "firmware_version": "E2010325",
  "nvme_pci_vendor": {
    "id": 32902,
    "subsystem_id": 32902
  },
  "nvme_ieee_oui_identifier": 6083300,
  "nvme_controller_id": 0,
  "nvme_number_of_namespaces": 1,
  "nvme_namespaces": [
    {
      "id": 1,
      "size": {
        "blocks": 547002288,
        "bytes": 280065171456
      },
      "capacity": {
        "blocks": 547002288,
        "bytes": 280065171456
      },
      "utilization": {
        "blocks": 547002288,
        "bytes": 280065171456
      },
      "formatted_lba_size": 512
    }
  ],
  "user_capacity": {
    "blocks": 547002288,
    "bytes": 280065171456
  },
  "logical_block_size": 512,
  "local_time": {
    "time_t": 1738053854,
    "asctime": "Tue Jan 28 09:44:14 2025 CET"
  },
  "smart_status": {
    "passed": true,
    "nvme": {
      "value": 0
    }
  },
  "nvme_smart_health_information_log": {
    "critical_warning": 0,
    "temperature": 31,
    "available_spare": 100,
    "available_spare_threshold": 0,
    "percentage_used": 0,
    "data_units_read": 67343004,
    "data_units_written": 65516455,
    "host_reads": 3265697818,
    "host_writes": 2714560339,
    "controller_busy_time": 628,
    "power_cycles": 26,
    "power_on_hours": 42772,
    "unsafe_shutdowns": 14,
    "media_errors": 0,
    "num_err_log_entries": 4
  },
  "temperature": {
    "current": 31
  },
  "power_cycle_count": 26,
  "power_on_time": {
    "hours": 42772
  }
}"""

HEALTH_NVME1 = """{
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
      "-d",
      "nvme",
      "/dev/nvme1"
    ],
    "exit_status": 0
  },
  "device": {
    "name": "/dev/nvme1",
    "info_name": "/dev/nvme1",
    "type": "nvme",
    "protocol": "NVMe"
  },
  "smart_status": {
    "passed": true,
    "nvme": {
      "value": 0
    }
  }
}"""
