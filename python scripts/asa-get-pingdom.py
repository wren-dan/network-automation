#!/usr/bin/python3
#Purpose: Compare latest Pingdom probe IP's to ASA configs and print if any differences are seen

from ciscoconfparse import CiscoConfParse

pingdom = []; sensors = []; ip = []; ips = []

with open('/mnt/c/users/me/Documents/misc/asa-configs') as configs:
    config_parse = CiscoConfParse(configs.readlines())

with open('/mnt/c/users/me/Documents/misc/pingdom-ips.txt') as ping:
    ping_ips = ping.readlines()

pingdom = config_parse.find_children("object-group network Pingdom_NA_Probes_grp")

for item in pingdom:
        if "network-object object" in item:
            object = "object network " + item.split().pop()
            if object.split().pop() == item.split().pop():
                sensors.append(config_parse.find_children(object))

for line in sensors:
    ip.append(line[1].strip().split().pop())

for line in ping_ips:
    ips.append(line.split("\",\"").pop().strip("\"\n"))

print("IP's added: " + " ".join(set(ips).difference(set(ip))))
print("IP's removed: " + " ".join(set(ip).difference(set(ips))))

