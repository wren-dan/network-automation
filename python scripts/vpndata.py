#!/usr/bin/python
#Gather and format VPN Peer, Group, IP, and Port data from raw asa config file 

import sys
import re
from ciscoconfparse import CiscoConfParse


# Function to parse the full configuration into dictionaries/lists that we will later use for analysis. Returns a bunch of lists and dictionaries.
def parse_asa_configuration(input_raw,input_parse):
    # Set up lists and dictionaries for return purposes
    objects = {}
    object_groups = {}
    access_lists = []
    crypto_maps = []
    crypto_peers = []
    # Read each line of the config, looking for configuratio components that we care about
    for line in input_raw:

        # Identify and collect configurations for all configured objects
        if 'object network' in line:
            obj = input_parse.find_children_w_parents(line,'.*')
            obj_name = (line.split()).pop(2)
            if not obj_name in objects and obj:
                objects[obj_name] = (obj)

        # Identify and collect configurations for all configured object groups
        if 'object-group network' in line:
            obj_group = input_parse.find_children_w_parents(line,'.*')
            obj_group_name = (line.split()).pop(2)
            if not obj_group_name in object_groups and obj_group:
                object_groups[obj_group_name] = (obj_group)

        # Identify and collect configurations for all configured access lists
        if re.match("^access-list.*",line):
            access_lists.append(line)

        # Identify and collect configurations for all configured crypto maps
        if re.match("^crypto map Prod_map.*peer",line):
            crypto_peers.append(line)

        # Identify and collect configurations for all configured crypto peers
        if re.match("^crypto map Prod_map.*match address",line):
            crypto_maps.append(line)

    return(objects,object_groups,access_lists,crypto_peers,crypto_maps)


def main():
    peers = {}

    # Open the source configuration file for reading and import/parse it.
    x = open('./asa-configs','r')
    config_raw = x.readlines()
    config_parse = CiscoConfParse(config_raw)
    x.close()

    # Send configuration off to get split up into different lists/dictionaries for reference
    ret_objects, ret_object_groups, ret_access_lists, ret_crypto_peers, ret_crypto_maps = parse_asa_configuration(config_raw,config_parse)

    #build dictionary of Peers with associated crypto map

    for line in ret_crypto_peers:
        mapid = ""
        linelist = line.split(" ")
        index = linelist.index("Prod_map")
        mapid = linelist[index+1]
        for line2 in ret_crypto_maps:
            mapid2 = ""
            linelist2 = line2.split(" ")
            index2 = linelist2.index("Prod_map")
            mapid2 = linelist2[index2+1]
            if mapid2 == mapid:
                peers[((linelist[index+4]).strip())] = (linelist2[index2+4]).strip()

    for k,v in peers.iteritems():
        for acl in ret_access_lists:
            acllist = acl.split(" ")
            if v == acllist[1]:
                iports = []
                oports = []
                grp = (acllist[-1]).strip()
                for acl2 in ret_access_lists:
                    acllist2 = acl2.split(" ")
                    if len(acllist2) >= 9:
                        if grp == acllist2[6] and (acllist2[-1].strip()).isdigit():
                            iports.append(acllist2[-1].strip())
                        if grp == acllist2[6] and (acllist2[8].strip()).isdigit():
                            oports.append(acllist2[8].strip())
                for k2,v2 in ret_object_groups.iteritems():
                    if grp == k2:
                        print "\nPeer: " + k + " Group: " + k2 + "\nInbound Port(s): " + (" ".join(iports))
                        print "Outbound Port(s): " + (" ".join(oports)) + "\nGroup Members:"
                        for obj in v2:
                            objclean = (obj.replace("network-object object", "")).strip()
                            if "group-object" in obj:
                                grpclean = (obj.replace("group-object", "")).strip()
                                for k4,v4 in ret_object_groups.iteritems():
                                    if grpclean == k4:
                                        for obj2 in v4:
                                            obj2clean = (obj2.replace("network-object object", "")).strip()
                                            for k5,v5 in ret_objects.iteritems():
                                                if (obj2clean == k5):
                                                    print obj2clean + " " + ("".join(v3)).strip()
                            if "network-object host" in obj:
                                hostclean = (obj.replace("network-object", "")).strip()
                                print hostclean
                            for k3,v3 in ret_objects.iteritems():
                                if (objclean == k3):
                                    print objclean + " " + ("".join(v3)).strip()


if __name__ == '__main__':
  main()
