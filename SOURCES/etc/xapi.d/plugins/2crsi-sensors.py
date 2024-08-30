#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import sys
import XenAPIPlugin
import re
import subprocess

sys.path.append('.')
from xcpngutils import configure_logging, run_command, error_wrapped
from xcpngutils.operationlocker import OperationLocker

@error_wrapped
def get_data(session, args):
    data = subprocess.check_output(["ipmi-sensors", "-Q", "--ignore-not-available-sensors", "--ignore-unrecognized-events"])
    data = str(data)
    data = re.sub(r'\\n\d+', '\n', data)
    data = data.replace('\\n', '\n')
    # Split the data into lines
    lines = data.splitlines()
    
    # Remove the header line
    headers = lines[0].split('|')
    lines = lines[1:]

    # Strip whitespace from headers and create a list of header names
    headers = [header.strip() for header in headers]

    # Parse the remaining lines into a list of dictionaries
    result = []
    for line in lines[1:]:
        columns = [col.strip() for col in line.split('|')]
        if len(columns) == len(headers):
            entry = {headers[i]: columns[i] for i in range(len(headers))}
            # Remove the "ID" field from each entry
            entry.pop("ID", None)
            result.append(entry)

    return json.dumps(result)

def get_ip(session,args):
    IP = subprocess.check_output(["ipmitool lan print | grep 'IP Address  '"], shell=True)
    IP = str(IP)
    IP = IP.replace(" ", "")
    result =  re.findall(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", IP)
    return result[0]


_LOGGER = configure_logging('2crsi-sensors')
if __name__ == "__main__":
    XenAPIPlugin.dispatch({
        'get_info': get_data,
        'get_ip': get_ip
    })
