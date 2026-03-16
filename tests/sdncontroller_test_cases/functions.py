# Plugin functions test cases, passed to fixture decorator
# PARAMS are in lists of test cases
# IDS are just a description of the test for pytest, manual matching is needed
import XenAPIPlugin
from mock import call

# List of ports in JSON format, as output by the `ovs-vsctl --format=json list port` command.
PORT_LIST_JSON = """
{"data":[[["uuid","0de54408-a136-4d67-a258-dc6e6b894f72"],["set",[]],0,false,["set",[]],0,["set",[]],["map",[]],false,["uuid","e1b02bec-caec-45ba-a548-536a64806423"],["set",[]],["set",[]],"xapi31_port15",["map",[["xo:sdn-controller:private-network-uuid","364a15c4-3138-4ef6-930f-704c1711e92c"]]],false,["set",[]],["map",[]],["map",[]],["map",[]],["map",[]],["set",[]],["set",[]],["set",[]]],[["uuid","f245a8f8-3845-4870-b2de-57e102bb4d9a"],["set",[]],0,false,["set",[]],0,["set",[]],["map",[]],false,["uuid","15472a6b-4aa9-4dcf-b300-715b79377bf1"],["set",[]],["set",[]],"vif2.0",["map",[]],false,["set",[]],["map",[]],["map",[]],["map",[]],["map",[]],["set",[]],["set",[]],["set",[]]],[["uuid","0e077dd0-df09-4864-a8c0-a6f485892921"],["set",[]],0,false,["set",[]],0,["set",[]],["map",[]],false,["uuid","fefec25f-1262-4acd-9d84-fe20f41d54b5"],["set",[]],["set",[]],"xapi9",["map",[]],false,["set",[]],["map",[]],["map",[]],["map",[]],["map",[]],["set",[]],["set",[]],["set",[]]],[["uuid","fef17539-5477-4914-b68e-60381c36f79d"],["set",[]],0,false,["set",[]],0,["set",[]],["map",[]],false,["uuid","23c506aa-a061-4c8e-b6ce-35a46265c2aa"],["set",[]],["set",[]],"xapi16_port13",["map",[["xo:sdn-controller:private-network-uuid","25ea1e51-b662-4679-a71f-d0a9624b4832"]]],false,["set",[]],["map",[]],["map",[]],["map",[]],["map",[]],["set",[]],["set",[]],["set",[]]],[["uuid","473301b2-7ca8-4741-bf66-236122e1176d"],["set",[]],0,false,["set",[]],0,["set",[]],["map",[]],false,["uuid","1d12f735-b1ef-458a-a7c8-a6f6a5f86172"],["set",[]],["set",[]],"eth0",["map",[]],false,["set",[]],["map",[]],["map",[]],["map",[]],["map",[]],["set",[]],["set",[]],["set",[]]],[["uuid","ec7b8cb2-9b65-4af0-9c67-f9bd8f5bef29"],["set",[]],0,false,["set",[]],0,["set",[]],["map",[]],false,["uuid","26ddebea-49d0-465e-991d-1b22a968f40e"],["set",[]],["set",[]],"xapi16",["map",[]],false,["set",[]],["map",[]],["map",[]],["map",[]],["map",[]],["set",[]],["set",[]],["set",[]]],[["uuid","6a737693-f9aa-42a6-a05d-e254d743c3fc"],["set",[]],0,false,["set",[]],0,["set",[]],["map",[]],false,["uuid","72e590be-14ba-4f64-8ede-1a0f751c6c56"],["set",[]],["set",[]],"xapi31",["map",[]],false,["set",[]],["map",[]],["map",[]],["map",[]],["map",[]],["set",[]],["set",[]],["set",[]]],[["uuid","7b52cff3-8b41-4e20-80db-62b927249b91"],["set",[]],0,false,["set",[]],0,["set",[]],["map",[]],false,["uuid","00314263-3096-4820-9a2f-509504fe9c1e"],["set",[]],["set",[]],"xapi9_port14",["map",[["xo:sdn-controller:private-network-uuid","b14c3cb2-2189-4086-b1c7-42d99d55f005"]]],false,["set",[]],["map",[]],["map",[]],["map",[]],["map",[]],["set",[]],["set",[]],["set",[]]],[["uuid","7f6cd65c-3382-4f2e-99c7-21637b198ffb"],["set",[]],0,false,["set",[]],0,["set",[]],["map",[]],false,["uuid","d76bc9ba-22c5-4fd6-9eaf-9502b59940ea"],["set",[]],["set",[]],"vif2.2",["map",[]],false,["set",[]],["map",[]],["map",[]],["map",[]],["map",[]],["set",[]],["set",[]],["set",[]]],[["uuid","01409acd-750e-4f37-a091-1006ab9acfb0"],["set",[]],0,false,["set",[]],0,["set",[]],["map",[]],true,["uuid","c3b73f81-0810-4fbe-b2b4-ff797f8abb22"],["set",[]],["set",[]],"xapi5",["map",[]],false,["set",[]],["map",[]],["map",[]],["map",[]],["map",[]],100,["set",[]],["set",[]]],[["uuid","bc222a76-b79c-4a43-b753-af91c9d10ff1"],["set",[]],0,false,["set",[]],0,["set",[]],["map",[]],false,["uuid","3a8c2af0-88ca-4a31-bbe3-b7b83668e52d"],["set",[]],["set",[]],"vif1.0",["map",[]],false,["set",[]],["map",[]],["map",[]],["map",[]],["map",[]],["set",[]],["set",[]],["set",[]]],[["uuid","4bb3cc76-5a2e-41eb-b018-26d9ef934f21"],["set",[]],0,false,["set",[]],0,["set",[]],["map",[]],false,["uuid","e0d981dd-ae2c-4e30-a7b0-e96f1a6ae4bc"],["set",[]],["set",[]],"vif2.1",["map",[]],false,["set",[]],["map",[]],["map",[]],["map",[]],["map",[]],100,["set",[]],["set",[]]],[["uuid","6cda9ca7-f0f3-47dd-8fff-93016be3497e"],["set",[]],0,false,["set",[]],0,["set",[]],["map",[]],false,["uuid","e60820dd-c660-4853-a78f-51a67a4c7b07"],["set",[]],["set",[]],"xenbr0",["map",[]],false,["set",[]],["map",[]],["map",[]],["map",[]],["map",[]],["set",[]],["set",[]],["set",[]]],[["uuid","7517d2d7-3679-4e90-8c79-4a52b585a582"],["set",[]],0,false,["set",[]],0,["set",[]],["map",[]],true,["uuid","191baed0-c6f5-470d-9aa6-e0c9ce960185"],["set",[]],["set",[]],"xapi0",["map",[]],false,["set",[]],["map",[]],["map",[]],["map",[]],["map",[]],42,["set",[]],["set",[]]]],"headings":["_uuid","bond_active_slave","bond_downdelay","bond_fake_iface","bond_mode","bond_updelay","cvlans","external_ids","fake_bridge","interfaces","lacp","mac","name","other_config","protected","qos","rstp_statistics","rstp_status","statistics","status","tag","trunks","vlan_mode"]}

"""

# List of interfaces in JSON format, as output by the `ovs-vsctl --format=json list interface` command.
INTERFACE_LIST_JSON = """
{"data":[[["uuid","191baed0-c6f5-470d-9aa6-e0c9ce960185"],"up",["map",[]],["map",[]],["set",[]],["set",[]],["set",[]],["set",[]],["set",[]],["set",[]],["set",[]],["set",[]],["set",[]],["map",[]],22,0,0,0,0,["set",[]],1,["set",[]],"up",["map",[]],"f8:0d:ac:1a:da:de","f8:0d:ac:1a:da:de",1500,1500,"xapi0",9,["set",[]],["map",[]],["map",[]],["map",[["collisions",0],["rx_bytes",0],["rx_crc_err",0],["rx_dropped",0],["rx_errors",0],["rx_frame_err",0],["rx_missed_errors",0],["rx_multicast_packets",0],["rx_over_err",0],["rx_packets",0],["tx_bytes",0],["tx_dropped",0],["tx_errors",0],["tx_packets",0]]],["map",[["driver_name","openvswitch"]]],"internal"],[["uuid","3a8c2af0-88ca-4a31-bbe3-b7b83668e52d"],"up",["map",[]],["map",[]],["set",[]],["set",[]],["set",[]],["set",[]],["set",[]],["set",[]],["set",[]],["set",[]],["set",[]],["map",[["attached-mac","56:55:a4:a4:ce:71"],["xs-network-uuid","9334aa83-6960-62e5-a463-5acc05295af4"],["xs-vif-uuid","e41c690e-c0a1-f130-4e95-b9a505db2f3c"],["xs-vm-uuid","0ec00fdc-8127-8817-40d4-79d61797f87a"]]],5,0,0,0,0,["set",[]],3,["set",[]],"up",["map",[]],["set",[]],"fe:ff:ff:ff:ff:ff",1500,["set",[]],"vif1.0",2,["set",[]],["map",[]],["map",[]],["map",[["collisions",0],["rx_bytes",950026692],["rx_crc_err",0],["rx_dropped",0],["rx_errors",0],["rx_frame_err",0],["rx_missed_errors",0],["rx_multicast_packets",0],["rx_over_err",0],["rx_packets",8366385],["tx_bytes",101259026443],["tx_dropped",5],["tx_errors",0],["tx_packets",13563793]]],["map",[["driver_name","vif"],["driver_version",""],["firmware_version",""]]],""],[["uuid","c3b73f81-0810-4fbe-b2b4-ff797f8abb22"],"up",["map",[]],["map",[]],["set",[]],["set",[]],["set",[]],["set",[]],["set",[]],["set",[]],["set",[]],["set",[]],["set",[]],["map",[]],15,0,0,0,0,["set",[]],1,["set",[]],"up",["map",[]],"f8:0d:ac:1a:da:de","f8:0d:ac:1a:da:de",1500,1500,"xapi5",4,["set",[]],["map",[]],["map",[]],["map",[["collisions",0],["rx_bytes",32756],["rx_crc_err",0],["rx_dropped",0],["rx_errors",0],["rx_frame_err",0],["rx_missed_errors",0],["rx_multicast_packets",0],["rx_over_err",0],["rx_packets",732],["tx_bytes",0],["tx_dropped",0],["tx_errors",0],["tx_packets",0]]],["map",[["driver_name","openvswitch"]]],"internal"],[["uuid","23c506aa-a061-4c8e-b6ce-35a46265c2aa"],"up",["map",[]],["map",[]],["set",[]],["set",[]],["set",[]],["set",[]],["set",[]],["set",[]],["set",[]],["set",[]],["set",[]],["map",[]],11,0,0,0,0,["set",[]],0,["set",[]],"up",["map",[]],["set",[]],"2a:b8:2c:93:bc:fd",["set",[]],["set",[]],"xapi16_iface13",1,["set",[]],["map",[["key","12"],["remote_ip","192.168.1.221"]]],["map",[]],["map",[["rx_bytes",0],["rx_packets",0],["tx_bytes",0],["tx_packets",0]]],["map",[["tunnel_egress_iface","xenbr0"],["tunnel_egress_iface_carrier","up"]]],"gre"],[["uuid","26ddebea-49d0-465e-991d-1b22a968f40e"],"up",["map",[]],["map",[]],["set",[]],["set",[]],["set",[]],["set",[]],["set",[]],["set",[]],["set",[]],["set",[]],["set",[]],["map",[]],7,0,0,0,0,["set",[]],1,["set",[]],"up",["map",[]],["set",[]],"6e:54:d3:eb:1e:a4",1500,1500,"xapi16",65534,["set",[]],["map",[]],["map",[]],["map",[["collisions",0],["rx_bytes",0],["rx_crc_err",0],["rx_dropped",0],["rx_errors",0],["rx_frame_err",0],["rx_missed_errors",0],["rx_multicast_packets",0],["rx_over_err",0],["rx_packets",0],["tx_bytes",0],["tx_dropped",0],["tx_errors",0],["tx_packets",0]]],["map",[["driver_name","openvswitch"]]],"internal"],[["uuid","d76bc9ba-22c5-4fd6-9eaf-9502b59940ea"],"up",["map",[]],["map",[]],["set",[]],["set",[]],["set",[]],["set",[]],["set",[]],["set",[]],["set",[]],["set",[]],["set",[]],["map",[["attached-mac","0a:27:cf:e6:d2:9c"],["xs-network-uuid","3d809de7-f11b-db02-40ca-0f51330aae19"],["xs-vif-uuid","547e321d-88f2-c698-7f8d-d26630165078"],["xs-vm-uuid","e07d8464-9a05-e391-b4c3-5dc38be4c792"]]],16,0,0,0,0,["set",[]],3,["set",[]],"up",["map",[]],["set",[]],"fe:ff:ff:ff:ff:ff",1500,["set",[]],"vif2.2",2,["set",[]],["map",[]],["map",[]],["map",[["collisions",0],["rx_bytes",12136],["rx_crc_err",0],["rx_dropped",0],["rx_errors",0],["rx_frame_err",0],["rx_missed_errors",0],["rx_multicast_packets",0],["rx_over_err",0],["rx_packets",215],["tx_bytes",15146],["tx_dropped",0],["tx_errors",0],["tx_packets",215]]],["map",[["driver_name","vif"],["driver_version",""],["firmware_version",""]]],""],[["uuid","15472a6b-4aa9-4dcf-b300-715b79377bf1"],"up",["map",[]],["map",[]],["set",[]],["set",[]],["set",[]],["set",[]],["set",[]],["set",[]],["set",[]],["set",[]],["set",[]],["map",[["attached-mac","4e:01:39:a6:46:69"],["xs-network-uuid","9334aa83-6960-62e5-a463-5acc05295af4"],["xs-vif-uuid","e9a7914a-9518-82e2-7052-42cb16cc9724"],["xs-vm-uuid","e07d8464-9a05-e391-b4c3-5dc38be4c792"]]],17,0,0,0,0,["set",[]],1,["set",[]],"up",["map",[]],["set",[]],"fe:ff:ff:ff:ff:ff",1500,["set",[]],"vif2.0",6,["set",[]],["map",[]],["map",[]],["map",[["collisions",0],["rx_bytes",1080132],["rx_crc_err",0],["rx_dropped",0],["rx_errors",0],["rx_frame_err",0],["rx_missed_errors",0],["rx_multicast_packets",0],["rx_over_err",0],["rx_packets",32439],["tx_bytes",257625162],["tx_dropped",0],["tx_errors",0],["tx_packets",2379022]]],["map",[["driver_name","vif"],["driver_version",""],["firmware_version",""]]],""],[["uuid","00314263-3096-4820-9a2f-509504fe9c1e"],"up",["map",[]],["map",[]],["set",[]],["set",[]],["set",[]],["set",[]],["set",[]],["set",[]],["set",[]],["set",[]],["set",[]],["map",[]],13,0,0,0,0,["set",[]],0,["set",[]],"up",["map",[]],["set",[]],"ce:5a:a4:99:b0:e5",["set",[]],["set",[]],"xapi9_iface14",1,["set",[]],["map",[["key","5"],["remote_ip","192.168.1.221"]]],["map",[]],["map",[["rx_bytes",15146],["rx_packets",215],["tx_bytes",15146],["tx_packets",215]]],["map",[["tunnel_egress_iface","xenbr0"],["tunnel_egress_iface_carrier","up"]]],"vxlan"],[["uuid","e1b02bec-caec-45ba-a548-536a64806423"],"up",["map",[]],["map",[]],["set",[]],["set",[]],["set",[]],["set",[]],["set",[]],["set",[]],["set",[]],["set",[]],["set",[]],["map",[]],11,0,0,0,0,["set",[]],0,["set",[]],"up",["map",[]],["set",[]],"22:2f:77:14:8b:ea",["set",[]],["set",[]],"xapi31_iface15",1,["set",[]],["map",[["key","14"],["remote_ip","192.168.1.221"]]],["map",[]],["map",[["rx_bytes",0],["rx_packets",0],["tx_bytes",0],["tx_packets",0]]],["map",[["tunnel_egress_iface","xenbr0"],["tunnel_egress_iface_carrier","up"]]],"gre"],[["uuid","e0d981dd-ae2c-4e30-a7b0-e96f1a6ae4bc"],"up",["map",[]],["map",[]],["set",[]],["set",[]],["set",[]],["set",[]],["set",[]],["set",[]],["set",[]],["set",[]],["set",[]],["map",[["attached-mac","62:16:6e:15:38:c3"],["xs-network-uuid","3878b6de-84e8-a988-5341-d09cf8c821ba"],["xs-vif-uuid","75980193-aa29-3359-087c-2bd11cb04b24"],["xs-vm-uuid","e07d8464-9a05-e391-b4c3-5dc38be4c792"]]],18,0,0,0,0,["set",[]],3,["set",[]],"up",["map",[]],["set",[]],"fe:ff:ff:ff:ff:ff",1500,["set",[]],"vif2.1",5,["set",[]],["map",[]],["map",[]],["map",[["collisions",0],["rx_bytes",20732],["rx_crc_err",0],["rx_dropped",0],["rx_errors",0],["rx_frame_err",0],["rx_missed_errors",0],["rx_multicast_packets",0],["rx_over_err",0],["rx_packets",519],["tx_bytes",15364],["tx_dropped",0],["tx_errors",0],["tx_packets",218]]],["map",[["driver_name","vif"],["driver_version",""],["firmware_version",""]]],""],[["uuid","1d12f735-b1ef-458a-a7c8-a6f6a5f86172"],"up",["map",[]],["map",[]],["set",[]],["set",[]],["set",[]],["set",[]],["set",[]],["set",[]],["set",[]],"full",["set",[]],["map",[]],2,0,0,0,0,["set",[]],1,1000000000,"up",["map",[]],["set",[]],"f8:0d:ac:1a:da:de",1500,1500,"eth0",1,["set",[]],["map",[]],["map",[]],["map",[["collisions",0],["rx_bytes",143676807514],["rx_crc_err",0],["rx_dropped",0],["rx_errors",0],["rx_frame_err",0],["rx_missed_errors",0],["rx_multicast_packets",1130962],["rx_over_err",0],["rx_packets",198109882],["tx_bytes",50188460190],["tx_dropped",0],["tx_errors",0],["tx_packets",142255313]]],["map",[["driver_name","r8169"],["driver_version",""],["firmware_version",""]]],""],[["uuid","e60820dd-c660-4853-a78f-51a67a4c7b07"],"up",["map",[]],["map",[]],["set",[]],["set",[]],["set",[]],["set",[]],["set",[]],["set",[]],["set",[]],["set",[]],["set",[]],["map",[]],4,0,0,0,0,["set",[]],1,["set",[]],"up",["map",[]],["set",[]],"f8:0d:ac:1a:da:de",1500,1500,"xenbr0",65534,["set",[]],["map",[]],["map",[]],["map",[["collisions",0],["rx_bytes",36745505785],["rx_crc_err",0],["rx_dropped",602217],["rx_errors",0],["rx_frame_err",0],["rx_missed_errors",0],["rx_multicast_packets",0],["rx_over_err",0],["rx_packets",122886392],["tx_bytes",48280983892],["tx_dropped",0],["tx_errors",0],["tx_packets",121147512]]],["map",[["driver_name","openvswitch"]]],"internal"],[["uuid","72e590be-14ba-4f64-8ede-1a0f751c6c56"],"up",["map",[]],["map",[]],["set",[]],["set",[]],["set",[]],["set",[]],["set",[]],["set",[]],["set",[]],["set",[]],["set",[]],["map",[]],14,0,0,0,0,["set",[]],1,["set",[]],"up",["map",[]],["set",[]],"8a:7e:24:58:c9:21",1500,1500,"xapi31",65534,["set",[]],["map",[]],["map",[]],["map",[["collisions",0],["rx_bytes",0],["rx_crc_err",0],["rx_dropped",0],["rx_errors",0],["rx_frame_err",0],["rx_missed_errors",0],["rx_multicast_packets",0],["rx_over_err",0],["rx_packets",0],["tx_bytes",0],["tx_dropped",0],["tx_errors",0],["tx_packets",0]]],["map",[["driver_name","openvswitch"]]],"internal"],[["uuid","fefec25f-1262-4acd-9d84-fe20f41d54b5"],"up",["map",[]],["map",[]],["set",[]],["set",[]],["set",[]],["set",[]],["set",[]],["set",[]],["set",[]],["set",[]],["set",[]],["map",[]],12,0,0,0,0,["set",[]],1,["set",[]],"up",["map",[]],["set",[]],"62:98:0c:6c:2e:d1",1500,1500,"xapi9",65534,["set",[]],["map",[]],["map",[]],["map",[["collisions",0],["rx_bytes",24272],["rx_crc_err",0],["rx_dropped",0],["rx_errors",0],["rx_frame_err",0],["rx_missed_errors",0],["rx_multicast_packets",0],["rx_over_err",0],["rx_packets",430],["tx_bytes",0],["tx_dropped",0],["tx_errors",0],["tx_packets",0]]],["map",[["driver_name","openvswitch"]]],"internal"]],"headings":["_uuid","admin_state","bfd","bfd_status","cfm_fault","cfm_fault_status","cfm_flap_count","cfm_health","cfm_mpid","cfm_remote_mpids","cfm_remote_opstate","duplex","error","external_ids","ifindex","ingress_policing_burst","ingress_policing_kpkts_burst","ingress_policing_kpkts_rate","ingress_policing_rate","lacp_current","link_resets","link_speed","link_state","lldp","mac","mac_in_use","mtu","mtu_request","name","ofport","ofport_request","options","other_config","statistics","status","type"]}
"""

UPDATE_ARGS_PARAMS = [
    {  # no vlan
        "args": {"bridge": "xenbr0"},
        "exception": None,
        "cmd": [
            {"returncode": 0, "stdout": "xenbr0", "stderr": ""},  # br-to-parent
            {
                "returncode": 0,
                "stdout": "eth0\nvif1.0\nvif2.0\n",
                "stderr": "",
            },  # list-ports
            {
                "returncode": 0,
                "stdout": "eth0\nvif1.0\nvif2.0\n",
                "stderr": "",
            },  # list-ports parent
            {"returncode": 0, "stdout": "[]", "stderr": ""},  # get port tag
            {"returncode": 0, "stdout": PORT_LIST_JSON, "stderr": ""},  # list port
            {
                "returncode": 0,
                "stdout": INTERFACE_LIST_JSON,
                "stderr": "",
            },  # list-interfaces
        ],
        "ofports": [2, 6],
        "uplinks": [1],
    },
    {  # with vlan
        "args": {"bridge": "xapi5"},
        "exception": None,
        "cmd": [
            {"returncode": 0, "stdout": "xenbr0", "stderr": ""},  # br-to-parent
            {"returncode": 0, "stdout": "vif2.1\n", "stderr": ""},  # list-ports
            {
                "returncode": 0,
                "stdout": "eth0\nvif1.0\nvif2.0\n",
                "stderr": "",
            },  # list-ports parent
            {"returncode": 0, "stdout": "100", "stderr": ""},  # get port tag
            {"returncode": 0, "stdout": PORT_LIST_JSON, "stderr": ""},  # list port
            {
                "returncode": 0,
                "stdout": INTERFACE_LIST_JSON,
                "stderr": "",
            },  # list-interfaces
        ],
        "ofports": [5],
        "uplinks": [1],
    },
    {  # invalid bridge
        "args": {"bridge": "abcd"},
        "exception": {
            "type": XenAPIPlugin.Failure,
            "code": "3",
            "text": "Error running ovs-vsctl command: ['ovs-vsctl', "
            "'br-to-parent', 'abcd']: ovs-vsctl: no bridge named abcd",
        },
        "cmd": [
            {
                "returncode": 1,
                "stdout": "",
                "stderr": "ovs-vsctl: no bridge named abcd",
            },
        ],
    },
    {  # error listing ports in bridge``
        "args": {"bridge": "xenbr0"},
        "exception": {
            "type": XenAPIPlugin.Failure,
            "code": "3",
            "text": "Error running ovs-vsctl command: ['ovs-vsctl', 'list-ports', 'xenbr0']: fake error",
        },
        "cmd": [
            {"returncode": 0, "stdout": "xenbr0", "stderr": ""},  # br-to-parent
            {"returncode": 1, "stdout": "", "stderr": "fake error"},
        ],
    },
    {  # error getting bridge tag
        "args": {"bridge": "xenbr0"},
        "exception": {
            "type": XenAPIPlugin.Failure,
            "code": "3",
            "text": "Error running ovs-vsctl command: ['ovs-vsctl', 'get', 'port', 'xenbr0', 'tag']: fake error",
        },
        "cmd": [
            {"returncode": 0, "stdout": "xenbr0", "stderr": ""},  # br-to-parent
            {"returncode": 0, "stdout": "vif2.1\n", "stderr": ""},  # list-ports
            {
                "returncode": 0,
                "stdout": "eth0\nvif1.0\nvif2.0\n",
                "stderr": "",
            },  # list-ports parent
            {"returncode": 1, "stdout": "", "stderr": "fake error"},
        ],
    },
    {  # error listing all ports
        "args": {"bridge": "xenbr0"},
        "exception": {
            "type": XenAPIPlugin.Failure,
            "code": "3",
            "text": "Error running ovs-vsctl command: ['ovs-vsctl', '--format=json', 'list', 'port']: fake error",
        },
        "cmd": [
            {"returncode": 0, "stdout": "xenbr0", "stderr": ""},  # br-to-parent
            {"returncode": 0, "stdout": "vif2.1\n", "stderr": ""},  # list-ports
            {
                "returncode": 0,
                "stdout": "eth0\nvif1.0\nvif2.0\n",
                "stderr": "",
            },  # list-ports parent
            {"returncode": 0, "stdout": "[]", "stderr": ""},  # get port tag
            {"returncode": 1, "stdout": "", "stderr": "fake error"},
        ],
    },
    {  # error listing all interfaces
        "args": {"bridge": "xenbr0"},
        "exception": {
            "type": XenAPIPlugin.Failure,
            "code": "3",
            "text": "Error running ovs-vsctl command: ['ovs-vsctl', '--format=json', 'list', 'interface']: fake error",
        },
        "cmd": [
            {"returncode": 0, "stdout": "xenbr0", "stderr": ""},  # br-to-parent
            {"returncode": 0, "stdout": "vif2.1\n", "stderr": ""},  # list-ports
            {
                "returncode": 0,
                "stdout": "eth0\nvif1.0\nvif2.0\n",
                "stderr": "",
            },  # list-ports parent
            {"returncode": 0, "stdout": "[]", "stderr": ""},  # get port tag
            {"returncode": 0, "stdout": PORT_LIST_JSON, "stderr": ""},  # list port
            {"returncode": 1, "stdout": "", "stderr": "fake error"},
        ],
    },
]
UPDATE_ARGS_IDS = [
    "no vlan",
    "with vlan",
    "invalid bridge",
    "error listing ports in bridge",
    "error getting bridge tag",
    "error listing all ports",
    "error listing all interfaces",
]

ADD_RULE_PARAMS = [
    {  # no args
        "args": {},
        "exception": {
            "type": XenAPIPlugin.Failure,
            "code": "1",
            "text": "add_rule: Failed to get parameters: bridge parameter is missing",
        },
        "cmd": [],
    },
    {  # ip drop
        "args": {
            "bridge": "xenbr0",
            "direction": "to",
            "protocol": "ip",
            "ipRange": "1.1.1.1",
            "allow": "false",
        },
        "exception": None,
        "cmd": [
            {"returncode": 0, "stdout": "xenbr0", "stderr": ""},  # br-to-parent
            {"returncode": 0, "stdout": "vif2.1\n", "stderr": ""},  # list-ports
            {"returncode": 0, "stdout": "vif2.1\n", "stderr": ""},  # list-ports parent
            {"returncode": 0, "stdout": "[]", "stderr": ""},  # get port tag
            {"returncode": 0, "stdout": PORT_LIST_JSON, "stderr": ""},  # list port
            {
                "returncode": 0,
                "stdout": INTERFACE_LIST_JSON,
                "stderr": "",
            },  # list-interfaces
        ],
        "calls": [
            call("add-flow", "xenbr0", "ip,cookie=0x0,in_port=5,nw_dst=1.1.1.1,actions=drop"),
        ],
    },
    {  # subnet tcp 4242 allow
        "args": {
            "bridge": "xenbr0",
            "direction": "to",
            "protocol": "tcp",
            "port": "4242",
            "ipRange": "1.1.1.1/24",
            "allow": "true",
        },
        "exception": None,
        "cmd": [
            {"returncode": 0, "stdout": "xenbr0", "stderr": ""},  # br-to-parent
            {"returncode": 0, "stdout": "vif2.1\n", "stderr": ""},  # list-ports
            {"returncode": 0, "stdout": "vif2.1\n", "stderr": ""},  # list-ports parent
            {"returncode": 0, "stdout": "[]", "stderr": ""},  # get port tag
            {"returncode": 0, "stdout": PORT_LIST_JSON, "stderr": ""},  # list port
            {
                "returncode": 0,
                "stdout": INTERFACE_LIST_JSON,
                "stderr": "",
            },  # list-interfaces
        ],
        "calls": [
            call(
                "add-flow",
                "xenbr0",
                "tcp,cookie=0x0,in_port=5,nw_dst=1.1.1.1/24,tp_dst=4242,actions=normal",
            )
        ],
    },
    {  # udp port from vif drop
        "args": {
            "bridge": "xenbr0",
            "direction": "from",
            "mac": "DE:AD:BE:EF:CA:FE",
            "protocol": "udp",
            "port": "2121",
            "ipRange": "4.4.4.4",
            "allow": "false",
        },
        "exception": None,
        "cmd": [
            {"returncode": 0, "stdout": "xenbr0", "stderr": ""},  # br-to-parent
            {"returncode": 0, "stdout": "vif2.1\n", "stderr": ""},  # list-ports
            {"returncode": 0, "stdout": "vif2.1\n", "stderr": ""},  # list-ports parent
            {"returncode": 0, "stdout": "[]", "stderr": ""},  # get port tag
            {"returncode": 0, "stdout": PORT_LIST_JSON, "stderr": ""},  # list port
            {
                "returncode": 0,
                "stdout": INTERFACE_LIST_JSON,
                "stderr": "",
            },  # list-interfaces
        ],
        "calls": [
            call(
                "add-flow",
                "xenbr0",
                "udp,cookie=0x0,dl_dst=DE:AD:BE:EF:CA:FE,nw_src=4.4.4.4,tp_src=2121,actions=drop",
            ),
        ],
    },
    {  # tcp no port
        "args": {
            "bridge": "xenbr0",
            "direction": "to",
            "protocol": "tcp",
            "ipRange": "1.1.1.1/24",
            "allow": "false",
        },
        "exception": {
            "type": XenAPIPlugin.Failure,
            "code": "2",
            "text": "add_rule: No port provided, tcp and udp requires one",
        },
        "cmd": {"returncode": 0, "stdout": "", "stderr": ""},
    },
    {  # failed ovs call
        "args": {
            "bridge": "xenbr0",
            "direction": "to",
            "protocol": "ip",
            "ipRange": "1.1.1.1/24",
            "allow": "false",
        },
        "exception": {
            "type": XenAPIPlugin.Failure,
            "code": "3",
            "text": "Error running ovs-ofctl command: ['ovs-ofctl', '-O', 'OpenFlow11', 'add-flow', 'xenbr0', "
            "'ip,cookie=0x0,in_port=5,nw_dst=1.1.1.1/24,actions=drop']: fake error",
        },
        "cmd": [
            {"returncode": 0, "stdout": "xenbr0", "stderr": ""},  # br-to-parent
            {"returncode": 0, "stdout": "vif2.1\n", "stderr": ""},  # list-ports
            {"returncode": 0, "stdout": "vif2.1\n", "stderr": ""},  # list-ports parent
            {"returncode": 0, "stdout": "[]", "stderr": ""},  # get port tag
            {"returncode": 0, "stdout": PORT_LIST_JSON, "stderr": ""},  # list port
            {
                "returncode": 0,
                "stdout": INTERFACE_LIST_JSON,
                "stderr": "",
            },  # list-interfaces
            {"returncode": 1, "stdout": "", "stderr": "fake error"},  # ofctl error
        ],
    },
]
ADD_RULE_IDS = [
    "no args",
    "ip drop",
    "subnet tcp 4242 allow",
    "udp port from vif drop",
    "tcp no port",
    "failed ovs call",
]

DEL_RULE_PARAMS = [
    {
        "args": {},
        "exception": {
            "type": XenAPIPlugin.Failure,
            "code": "1",
            "text": "del_rule: Failed to get parameters: bridge parameter is missing",
        },
        "cmd": {"returncode": 0, "stdout": "", "stderr": ""},
    },
    {  # ip drop
        "args": {
            "bridge": "xenbr0",
            "direction": "to",
            "protocol": "ip",
            "ipRange": "1.1.1.1",
            "allow": "false",
        },
        "exception": None,
        "cmd": [
            {"returncode": 0, "stdout": "xenbr0", "stderr": ""},  # br-to-parent
            {"returncode": 0, "stdout": "vif2.1\n", "stderr": ""},  # list-ports
            {"returncode": 0, "stdout": "vif2.1\n", "stderr": ""},  # list-ports parent
            {"returncode": 0, "stdout": "[]", "stderr": ""},  # get port tag
            {"returncode": 0, "stdout": PORT_LIST_JSON, "stderr": ""},  # list port
            {
                "returncode": 0,
                "stdout": INTERFACE_LIST_JSON,
                "stderr": "",
            },  # list-interfaces
        ],
        "calls": [
            call("del-flows", "xenbr0", "ip,cookie=0x0/-1,in_port=5,nw_dst=1.1.1.1"),
        ],
    },
    {  # subnet tcp 4242 allow
        "args": {
            "bridge": "xenbr0",
            "direction": "to",
            "protocol": "tcp",
            "port": "4242",
            "ipRange": "1.1.1.1/24",
            "allow": "true",
        },
        "exception": None,
        "cmd": [
            {"returncode": 0, "stdout": "xenbr0", "stderr": ""},  # br-to-parent
            {"returncode": 0, "stdout": "vif2.1\n", "stderr": ""},  # list-ports
            {"returncode": 0, "stdout": "vif2.1\n", "stderr": ""},  # list-ports parent
            {"returncode": 0, "stdout": "[]", "stderr": ""},  # get port tag
            {"returncode": 0, "stdout": PORT_LIST_JSON, "stderr": ""},  # list port
            {
                "returncode": 0,
                "stdout": INTERFACE_LIST_JSON,
                "stderr": "",
            },  # list-interfaces
        ],
        "calls": [
            call(
                "del-flows",
                "xenbr0",
                "tcp,cookie=0x0/-1,in_port=5,nw_dst=1.1.1.1/24,tp_dst=4242",
            )
        ],
    },
    {  # udp port from vif drop
        "args": {
            "bridge": "xenbr0",
            "direction": "from",
            "mac": "DE:AD:BE:EF:CA:FE",
            "protocol": "udp",
            "port": "2121",
            "ipRange": "4.4.4.4",
            "allow": "false",
        },
        "exception": None,
        "cmd": [
            {"returncode": 0, "stdout": "xenbr0", "stderr": ""},  # br-to-parent
            {"returncode": 0, "stdout": "vif2.1\n", "stderr": ""},  # list-ports
            {"returncode": 0, "stdout": "vif2.1\n", "stderr": ""},  # list-ports parent
            {"returncode": 0, "stdout": "[]", "stderr": ""},  # get port tag
            {"returncode": 0, "stdout": PORT_LIST_JSON, "stderr": ""},  # list port
            {
                "returncode": 0,
                "stdout": INTERFACE_LIST_JSON,
                "stderr": "",
            },  # list-interfaces
        ],
        "calls": [
            call(
                "del-flows",
                "xenbr0",
                "udp,cookie=0x0/-1,dl_dst=DE:AD:BE:EF:CA:FE,nw_src=4.4.4.4,tp_src=2121",
            ),
        ],
    },
    {  # tcp no port
        "args": {
            "bridge": "xenbr0",
            "direction": "to",
            "protocol": "tcp",
            "ipRange": "1.1.1.1/24",
            "allow": "false",
        },
        "exception": {
            "type": XenAPIPlugin.Failure,
            "code": "2",
            "text": "del_rule: No port provided, tcp and udp requires one",
        },
        "cmd": {"returncode": 0, "stdout": "", "stderr": ""},
    },
    {  # failed ovs call
        "args": {
            "bridge": "xenbr0",
            "direction": "to",
            "protocol": "ip",
            "ipRange": "1.1.1.1/24",
            "allow": "false",
        },
        "exception": {
            "type": XenAPIPlugin.Failure,
            "code": "3",
            "text": "Error running ovs-ofctl command: ['ovs-ofctl', '-O', 'OpenFlow11', 'del-flows', 'xenbr0', "
            "'ip,cookie=0x0/-1,in_port=5,nw_dst=1.1.1.1/24']: fake error",
        },
        "cmd": [
            {"returncode": 0, "stdout": "xenbr0", "stderr": ""},  # br-to-parent
            {"returncode": 0, "stdout": "vif2.1\n", "stderr": ""},  # list-ports
            {"returncode": 0, "stdout": "vif2.1\n", "stderr": ""},  # list-ports parent
            {"returncode": 0, "stdout": "[]", "stderr": ""},  # get port tag
            {"returncode": 0, "stdout": PORT_LIST_JSON, "stderr": ""},  # list port
            {
                "returncode": 0,
                "stdout": INTERFACE_LIST_JSON,
                "stderr": "",
            },  # list-interfaces
            {"returncode": 1, "stdout": "", "stderr": "fake error"},  # ofctl error
        ],
    },
]
DEL_RULE_IDS = [
    "no args",
    "ip drop",
    "subnet tcp 4242 allow",
    "udp port from vif drop",
    "tcp no port",
    "failed ovs call",
]


DUMP_FLOWS_PARAMS = [
    {  # no args
        "args": {},
        "exception": {
            "type": XenAPIPlugin.Failure,
            "code": "1",
            "text": "dump_flows: Failed to get parameters: bridge parameter is missing",
        },
        "cmd": {"returncode": 0, "stdout": "", "stderr": ""},
    },
    {  # invalid bridge
        "args": {"bridge": ""},
        "exception": {
            "type": XenAPIPlugin.Failure,
            "code": "1",
            "text": "dump_flows: Failed to get parameters: '' is not a valid bridge name",
        },
        "cmd": {"returncode": 0, "stdout": "", "stderr": ""},
    },
    {  # xenbr0
        "args": {"bridge": "xenbr0"},
        "exception": None,
        "cmd": {
            "returncode": 0,
            "stdout": '"OFPST_FLOW reply (OF1.1) (xid=0x2):\n cookie=0x0, duration=10553.194s, table=0, '
            'n_packets=221808, n_bytes=84062096, priority=0 actions=NORMAL\n"',
            "stderr": "",
        },
    },
    {  # non-exsting bridge
        "args": {"bridge": "xapi42"},
        "exception": {
            "type": XenAPIPlugin.Failure,
            "code": "3",
            "text": "Error dumping flows: ['ovs-ofctl', '-O', 'OpenFlow11', 'dump-flows', 'xapi42']: "
            "ovs-ofctl: xapi42 is not a bridge or a socket\n",
        },
        "cmd": {
            "returncode": 1,
            "stdout": "",
            "stderr": "ovs-ofctl: xapi42 is not a bridge or a socket\n",
        },
    },
]
DUMP_FLOWS_IDS = ["no args", "invalid bridge", "xenbr0", "non-exsting bridge"]
