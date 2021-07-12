#!/usr/bin/python

import json
import re

import XenAPIPlugin

from xcpngutils import run_command

def list_blockdevices(session, args):
    result = run_command(["lsblk", "-P", "-b", "-o", "NAME,KNAME,PKNAME,SIZE,TYPE,RO,MOUNTPOINT"])
    output_string = result["stdout"].decode("utf-8").strip()

    results = list()
    blockdevices = dict()
    for output in output_string.split("\n"):
        output_dict = dict(re.findall(r'(\S+)=(".*?"|\S+)', output))
        output_dict = {key.lower(): output_dict[key].strip('"') for key in output_dict}
        kname = output_dict["kname"]
        pkname = output_dict["pkname"]
        if pkname != "":
            parent = blockdevices[pkname]
            if "children" not in parent:
                parent["children"] = list()
            parent["children"].append(output_dict)
        else:
            results.append(output_dict)

        blockdevices[kname] = output_dict

    result["blockdevices"] = results
    return json.dumps(result)

if __name__ == "__main__":
    XenAPIPlugin.dispatch({"list_blockdevices": list_blockdevices})
