import json
from smartctl_outputs.smartctl_sda import INFO_SDA
from smartctl_outputs.smartctl_nvme1 import INFO_NVME1
from smartctl_outputs.smartctl_megaraid0 import INFO_MEGARAID0
from smartctl_outputs.smartctl_megaraid1 import INFO_MEGARAID1

# Parse the INFO JSON string for each devices
info_sda_dict = json.loads(INFO_SDA)
info_nvme1_dict = json.loads(INFO_NVME1)
info_megaraid0_dict = json.loads(INFO_MEGARAID0)
info_megaraid1_dict = json.loads(INFO_MEGARAID1)

expected_info_dict = {
    "/dev/sda:sat": info_sda_dict,
    "/dev/nvme1:nvme": info_nvme1_dict,
    "/dev/bus/0:megaraid,0": info_megaraid0_dict,
    "/dev/bus/0:megaraid,1": info_megaraid1_dict,
}

# Convert the result back to a JSON string
EXPECTED_INFO = json.dumps(expected_info_dict, indent=2)

expected_health_dict = {
    "/dev/sda:sat": "PASSED",
    "/dev/nvme1:nvme": "PASSED",
    "/dev/bus/0:megaraid,0": "PASSED",
    "/dev/bus/0:megaraid,1": "PASSED",
}

EXPECTED_HEALTH = json.dumps(expected_health_dict, indent=2)
