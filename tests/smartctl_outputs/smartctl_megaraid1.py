# Outputs are from real hardware:
#   INFO -> smartctl -j -a -d megaraid,1 /dev/bus/0 | jq .
#   HEALTH -> smartctl -j -H -d megaraid,1 /dev/bus/0 | jq .

INFO_MEGARAID1 = """{
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
      "megaraid,1",
      "/dev/bus/0"
    ],
    "messages": [
      {
        "string": "Warning: This result is based on an Attribute check.",
        "severity": "warning"
      }
    ],
    "exit_status": 4
  },
  "device": {
    "name": "/dev/bus/0",
    "info_name": "/dev/bus/0 [megaraid_disk_01] [SAT]",
    "type": "sat+megaraid,1",
    "protocol": "ATA"
  },
  "model_family": "Phison Driven SSDs",
  "model_name": "KINGSTON SA400S37240G",
  "serial_number": "50026B73815A7309",
  "wwn": {
    "naa": 5,
    "oui": 9911,
    "id": 15055090441
  },
  "firmware_version": "SAI20102",
  "user_capacity": {
    "blocks": 468862128,
    "bytes": 240057409536
  },
  "logical_block_size": 512,
  "physical_block_size": 512,
  "rotation_rate": 0,
  "in_smartctl_database": true,
  "ata_version": {
    "string": "ACS-3 T13/2161-D revision 4",
    "major_value": 2040,
    "minor_value": 283
  },
  "sata_version": {
    "string": "SATA 3.2",
    "value": 255
  },
  "interface_speed": {
    "max": {
      "sata_value": 14,
      "string": "6.0 Gb/s",
      "units_per_second": 60,
      "bits_per_unit": 100000000
    },
    "current": {
      "sata_value": 3,
      "string": "6.0 Gb/s",
      "units_per_second": 60,
      "bits_per_unit": 100000000
    }
  },
  "local_time": {
    "time_t": 1738053894,
    "asctime": "Tue Jan 28 09:44:54 2025 CET"
  },
  "smart_status": {
    "passed": true
  },
  "ata_smart_data": {
    "offline_data_collection": {
      "status": {
        "value": 0,
        "string": "was never started"
      },
      "completion_seconds": 120
    },
    "self_test": {
      "status": {
        "value": 0,
        "string": "completed without error",
        "passed": true
      },
      "polling_minutes": {
        "short": 2,
        "extended": 10
      }
    },
    "capabilities": {
      "values": [
        17,
        2
      ],
      "exec_offline_immediate_supported": true,
      "offline_is_aborted_upon_new_cmd": false,
      "offline_surface_scan_supported": false,
      "self_tests_supported": true,
      "conveyance_self_test_supported": false,
      "selective_self_test_supported": false,
      "attribute_autosave_enabled": false,
      "error_logging_supported": true,
      "gp_logging_supported": true
    }
  },
  "ata_smart_attributes": {
    "revision": 1,
    "table": [
      {
        "id": 1,
        "name": "Raw_Read_Error_Rate",
        "value": 100,
        "worst": 100,
        "thresh": 0,
        "when_failed": "",
        "flags": {
          "value": 50,
          "string": "-O--CK ",
          "prefailure": false,
          "updated_online": true,
          "performance": false,
          "error_rate": false,
          "event_count": true,
          "auto_keep": true
        },
        "raw": {
          "value": 100,
          "string": "100"
        }
      },
      {
        "id": 9,
        "name": "Power_On_Hours",
        "value": 100,
        "worst": 100,
        "thresh": 0,
        "when_failed": "",
        "flags": {
          "value": 50,
          "string": "-O--CK ",
          "prefailure": false,
          "updated_online": true,
          "performance": false,
          "error_rate": false,
          "event_count": true,
          "auto_keep": true
        },
        "raw": {
          "value": 23892,
          "string": "23892"
        }
      },
      {
        "id": 12,
        "name": "Power_Cycle_Count",
        "value": 100,
        "worst": 100,
        "thresh": 0,
        "when_failed": "",
        "flags": {
          "value": 50,
          "string": "-O--CK ",
          "prefailure": false,
          "updated_online": true,
          "performance": false,
          "error_rate": false,
          "event_count": true,
          "auto_keep": true
        },
        "raw": {
          "value": 10,
          "string": "10"
        }
      },
      {
        "id": 148,
        "name": "Unknown_Attribute",
        "value": 100,
        "worst": 100,
        "thresh": 0,
        "when_failed": "",
        "flags": {
          "value": 0,
          "string": "------ ",
          "prefailure": false,
          "updated_online": false,
          "performance": false,
          "error_rate": false,
          "event_count": false,
          "auto_keep": false
        },
        "raw": {
          "value": 0,
          "string": "0"
        }
      },
      {
        "id": 149,
        "name": "Unknown_Attribute",
        "value": 100,
        "worst": 100,
        "thresh": 0,
        "when_failed": "",
        "flags": {
          "value": 0,
          "string": "------ ",
          "prefailure": false,
          "updated_online": false,
          "performance": false,
          "error_rate": false,
          "event_count": false,
          "auto_keep": false
        },
        "raw": {
          "value": 0,
          "string": "0"
        }
      },
      {
        "id": 167,
        "name": "Unknown_Attribute",
        "value": 100,
        "worst": 100,
        "thresh": 0,
        "when_failed": "",
        "flags": {
          "value": 0,
          "string": "------ ",
          "prefailure": false,
          "updated_online": false,
          "performance": false,
          "error_rate": false,
          "event_count": false,
          "auto_keep": false
        },
        "raw": {
          "value": 0,
          "string": "0"
        }
      },
      {
        "id": 168,
        "name": "SATA_Phy_Error_Count",
        "value": 100,
        "worst": 100,
        "thresh": 0,
        "when_failed": "",
        "flags": {
          "value": 18,
          "string": "-O--C- ",
          "prefailure": false,
          "updated_online": true,
          "performance": false,
          "error_rate": false,
          "event_count": true,
          "auto_keep": false
        },
        "raw": {
          "value": 0,
          "string": "0"
        }
      },
      {
        "id": 169,
        "name": "Unknown_Attribute",
        "value": 100,
        "worst": 100,
        "thresh": 0,
        "when_failed": "",
        "flags": {
          "value": 0,
          "string": "------ ",
          "prefailure": false,
          "updated_online": false,
          "performance": false,
          "error_rate": false,
          "event_count": false,
          "auto_keep": false
        },
        "raw": {
          "value": 0,
          "string": "0"
        }
      },
      {
        "id": 170,
        "name": "Bad_Blk_Ct_Erl/Lat",
        "value": 100,
        "worst": 100,
        "thresh": 10,
        "when_failed": "",
        "flags": {
          "value": 0,
          "string": "------ ",
          "prefailure": false,
          "updated_online": false,
          "performance": false,
          "error_rate": false,
          "event_count": false,
          "auto_keep": false
        },
        "raw": {
          "value": 0,
          "string": "0/0"
        }
      },
      {
        "id": 172,
        "name": "Unknown_Attribute",
        "value": 100,
        "worst": 100,
        "thresh": 0,
        "when_failed": "",
        "flags": {
          "value": 50,
          "string": "-O--CK ",
          "prefailure": false,
          "updated_online": true,
          "performance": false,
          "error_rate": false,
          "event_count": true,
          "auto_keep": true
        },
        "raw": {
          "value": 0,
          "string": "0"
        }
      },
      {
        "id": 173,
        "name": "MaxAvgErase_Ct",
        "value": 100,
        "worst": 100,
        "thresh": 0,
        "when_failed": "",
        "flags": {
          "value": 0,
          "string": "------ ",
          "prefailure": false,
          "updated_online": false,
          "performance": false,
          "error_rate": false,
          "event_count": false,
          "auto_keep": false
        },
        "raw": {
          "value": 0,
          "string": "0"
        }
      },
      {
        "id": 181,
        "name": "Program_Fail_Cnt_Total",
        "value": 100,
        "worst": 100,
        "thresh": 0,
        "when_failed": "",
        "flags": {
          "value": 50,
          "string": "-O--CK ",
          "prefailure": false,
          "updated_online": true,
          "performance": false,
          "error_rate": false,
          "event_count": true,
          "auto_keep": true
        },
        "raw": {
          "value": 0,
          "string": "0"
        }
      },
      {
        "id": 182,
        "name": "Erase_Fail_Count_Total",
        "value": 100,
        "worst": 100,
        "thresh": 0,
        "when_failed": "",
        "flags": {
          "value": 0,
          "string": "------ ",
          "prefailure": false,
          "updated_online": false,
          "performance": false,
          "error_rate": false,
          "event_count": false,
          "auto_keep": false
        },
        "raw": {
          "value": 0,
          "string": "0"
        }
      },
      {
        "id": 187,
        "name": "Reported_Uncorrect",
        "value": 100,
        "worst": 100,
        "thresh": 0,
        "when_failed": "",
        "flags": {
          "value": 50,
          "string": "-O--CK ",
          "prefailure": false,
          "updated_online": true,
          "performance": false,
          "error_rate": false,
          "event_count": true,
          "auto_keep": true
        },
        "raw": {
          "value": 0,
          "string": "0"
        }
      },
      {
        "id": 192,
        "name": "Unsafe_Shutdown_Count",
        "value": 100,
        "worst": 100,
        "thresh": 0,
        "when_failed": "",
        "flags": {
          "value": 18,
          "string": "-O--C- ",
          "prefailure": false,
          "updated_online": true,
          "performance": false,
          "error_rate": false,
          "event_count": true,
          "auto_keep": false
        },
        "raw": {
          "value": 8,
          "string": "8"
        }
      },
      {
        "id": 194,
        "name": "Temperature_Celsius",
        "value": 23,
        "worst": 36,
        "thresh": 0,
        "when_failed": "",
        "flags": {
          "value": 34,
          "string": "-O---K ",
          "prefailure": false,
          "updated_online": true,
          "performance": false,
          "error_rate": false,
          "event_count": false,
          "auto_keep": true
        },
        "raw": {
          "value": 77311770647,
          "string": "23 (Min/Max 18/36)"
        }
      },
      {
        "id": 196,
        "name": "Not_In_Use",
        "value": 100,
        "worst": 100,
        "thresh": 0,
        "when_failed": "",
        "flags": {
          "value": 50,
          "string": "-O--CK ",
          "prefailure": false,
          "updated_online": true,
          "performance": false,
          "error_rate": false,
          "event_count": true,
          "auto_keep": true
        },
        "raw": {
          "value": 0,
          "string": "0"
        }
      },
      {
        "id": 199,
        "name": "CRC_Error_Count",
        "value": 100,
        "worst": 100,
        "thresh": 0,
        "when_failed": "",
        "flags": {
          "value": 50,
          "string": "-O--CK ",
          "prefailure": false,
          "updated_online": true,
          "performance": false,
          "error_rate": false,
          "event_count": true,
          "auto_keep": true
        },
        "raw": {
          "value": 0,
          "string": "0"
        }
      },
      {
        "id": 218,
        "name": "CRC_Error_Count",
        "value": 100,
        "worst": 100,
        "thresh": 0,
        "when_failed": "",
        "flags": {
          "value": 50,
          "string": "-O--CK ",
          "prefailure": false,
          "updated_online": true,
          "performance": false,
          "error_rate": false,
          "event_count": true,
          "auto_keep": true
        },
        "raw": {
          "value": 0,
          "string": "0"
        }
      },
      {
        "id": 231,
        "name": "SSD_Life_Left",
        "value": 97,
        "worst": 97,
        "thresh": 0,
        "when_failed": "",
        "flags": {
          "value": 0,
          "string": "------ ",
          "prefailure": false,
          "updated_online": false,
          "performance": false,
          "error_rate": false,
          "event_count": false,
          "auto_keep": false
        },
        "raw": {
          "value": 97,
          "string": "97"
        }
      },
      {
        "id": 233,
        "name": "Flash_Writes_GiB",
        "value": 100,
        "worst": 100,
        "thresh": 0,
        "when_failed": "",
        "flags": {
          "value": 50,
          "string": "-O--CK ",
          "prefailure": false,
          "updated_online": true,
          "performance": false,
          "error_rate": false,
          "event_count": true,
          "auto_keep": true
        },
        "raw": {
          "value": 1173,
          "string": "1173"
        }
      },
      {
        "id": 241,
        "name": "Lifetime_Writes_GiB",
        "value": 100,
        "worst": 100,
        "thresh": 0,
        "when_failed": "",
        "flags": {
          "value": 50,
          "string": "-O--CK ",
          "prefailure": false,
          "updated_online": true,
          "performance": false,
          "error_rate": false,
          "event_count": true,
          "auto_keep": true
        },
        "raw": {
          "value": 2168,
          "string": "2168"
        }
      },
      {
        "id": 242,
        "name": "Lifetime_Reads_GiB",
        "value": 100,
        "worst": 100,
        "thresh": 0,
        "when_failed": "",
        "flags": {
          "value": 50,
          "string": "-O--CK ",
          "prefailure": false,
          "updated_online": true,
          "performance": false,
          "error_rate": false,
          "event_count": true,
          "auto_keep": true
        },
        "raw": {
          "value": 1630,
          "string": "1630"
        }
      },
      {
        "id": 244,
        "name": "Average_Erase_Count",
        "value": 100,
        "worst": 100,
        "thresh": 0,
        "when_failed": "",
        "flags": {
          "value": 0,
          "string": "------ ",
          "prefailure": false,
          "updated_online": false,
          "performance": false,
          "error_rate": false,
          "event_count": false,
          "auto_keep": false
        },
        "raw": {
          "value": 35,
          "string": "35"
        }
      },
      {
        "id": 245,
        "name": "Max_Erase_Count",
        "value": 100,
        "worst": 100,
        "thresh": 0,
        "when_failed": "",
        "flags": {
          "value": 0,
          "string": "------ ",
          "prefailure": false,
          "updated_online": false,
          "performance": false,
          "error_rate": false,
          "event_count": false,
          "auto_keep": false
        },
        "raw": {
          "value": 124,
          "string": "124"
        }
      },
      {
        "id": 246,
        "name": "Total_Erase_Count",
        "value": 100,
        "worst": 100,
        "thresh": 0,
        "when_failed": "",
        "flags": {
          "value": 0,
          "string": "------ ",
          "prefailure": false,
          "updated_online": false,
          "performance": false,
          "error_rate": false,
          "event_count": false,
          "auto_keep": false
        },
        "raw": {
          "value": 58560,
          "string": "58560"
        }
      }
    ]
  },
  "power_on_time": {
    "hours": 23892
  },
  "power_cycle_count": 10,
  "temperature": {
    "current": 23
  },
  "ata_smart_error_log": {
    "summary": {
      "revision": 1,
      "count": 0
    }
  },
  "ata_smart_self_test_log": {
    "standard": {
      "revision": 1,
      "table": [
        {
          "type": {
            "value": 1,
            "string": "Short offline"
          },
          "status": {
            "value": 0,
            "string": "Completed without error",
            "passed": true
          },
          "lifetime_hours": 3612
        }
      ],
      "count": 1,
      "error_count_total": 0,
      "error_count_outdated": 0
    }
  }
}"""

HEALTH_MEGARAID1 = """{
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
      "megaraid,1",
      "/dev/bus/0"
    ],
    "messages": [
      {
        "string": "Warning: This result is based on an Attribute check.",
        "severity": "warning"
      }
    ],
    "exit_status": 4
  },
  "device": {
    "name": "/dev/bus/0",
    "info_name": "/dev/bus/0 [megaraid_disk_01] [SAT]",
    "type": "sat+megaraid,1",
    "protocol": "ATA"
  },
  "smart_status": {
    "passed": true
  }
}"""
