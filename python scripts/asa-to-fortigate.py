#!/usr/bin/python3
#Purpose: As a starting point for ASA to Fortigate conversion - grab objects / object groups / service / service groups and convert to FGT Syntax.
#BUG: Too many to list, this script is Incomplete.

from ciscoconfparse import CiscoConfParse

def validIP(address):
    parts = address.split(".")
    if len(parts) != 4:
        return False
    for item in parts:
        if not 0 <= int(item) <= 255:
            return False
    return True

def format_addr(object):
    if type(object) != list:
        item = config_parse.find_children(object) 
    else:
        item = object  
    if item:
        if "subnet" in item[1]:
            print("edit " + "\"" + item[0].split().pop().strip() + "\"")
            print("set " + item[1].strip())
            print("next")
        elif "host" in item[1]:
            print("edit " + "\"" + item[0].split().pop().strip() + "\"")
            print("set subnet " + item[1].split().pop().strip() + " 255.255.255.255")
            print("next")
        elif "fqdn" in item[1]:
            print("edit " + "\"" + item[0].split().pop().strip() + "\"")
            print("set type fqdn")
            print("set fqdn " + "\"" + item[1].split().pop().strip() + "\"")
            print("next")
        elif "range" in item[1]:
            print("edit " + "\"" + item[0].split().pop().strip() + "\"")
            print("set type iprange")
            print("set start-ip " + item[1].split().pop(-2))
            print("set end-ip " + item[1].split().pop().strip())
            print("next")

def format_srv(srv):
    item = config_parse.find_children(srv)
    if item:
        if "tcp" in item[1] and "range" in item[1]:
            print("edit " + "\"" + item[0].split().pop().strip() + "\"")
            print("set tcp-portrange " + item[1].split().pop(-2) + "-" + item[1].split().pop().strip())
            print("next")
        elif "tcp" in item[1]:
            print("edit " + "\"" + item[0].split().pop().strip() + "\"")
            print("set tcp-portrange " + item[1].split().pop().strip())
            print("next")
        elif "udp" in item[1] and "range" in item[1]:
            print("edit " + "\"" + item[0].split().pop().strip() + "\"")
            print("set udp-portrange " + item[1].split().pop(-2) + "-" + item[1].split().pop().strip())
            print("next")
        elif "udp" in item[1]:
            print("edit " + "\"" + item[0].split().pop().strip() + "\"")
            print("set udp-portrange " + item[1].split().pop().strip())
            print("next")

def format_addr_grp(grp):
    item = config_parse.find_children(grp)
    if item:
        objs = []
        print("edit " + "\"" + item[0].split().pop().strip() + "\"")
        item.pop(0)
        for obj in item:
            if validIP(obj.split().pop(1)):
                objs.append("\"" + obj.split().pop(-2) + "\"")
            else:
                objs.append("\"" + obj.split().pop().strip() + "\"")
        print("set member " + " ".join(objs))
        print("next")

def format_srv_grp(srv_grp):
    item = config_parse.find_children(srv_grp)
    if item:
        objs = []
        if item[0].split().pop().strip() == "tcp" or item[0].split().pop().strip() == "udp" or item[0].split().pop().strip() == "tcp-udp":
            print("edit " + "\"" + item[0].split().pop(-2).strip() + "\"")
        else:
            proto = ""
            print("edit " + "\"" + item[0].split().pop().strip() + "\"")
        item.pop(0)
        for obj in item:
            if " range " in obj:
                objs.append("\"" + obj.split().pop(-2) + "-" + obj.split().pop().strip() + "\"")
            else:
                objs.append("\"" + obj.split().pop().strip() + "\"")
        print("set member " + " ".join(objs))
        print("next")

def append_hosts(host):
    objects.append([host.split().pop().strip(), ("host " + host.split().pop().strip())])

def append_nets(net):
    objects.append([net.split().pop(-2), ("subnet " + net.split().pop(-2) + " " + net.split().pop().strip())])

def append_srvs(srv):
    objects.append([srv.split().pop(-2), ("subnet " + srv.split().pop(-2) + " " + srv.split().pop().strip())])


if __name__ == "__main__":
    
    with open('/mnt/c/users/me/Documents/project/misc/asa-configs') as configs:
        config_parse = CiscoConfParse(configs.readlines(), syntax='asa')

    objects = config_parse.find_objects(r'^object network')

    hosts_in_grps = config_parse.find_objects(r'^ network-object host')

    nets_in_grps = config_parse.find_objects(r'^ network-object \d+')

    groups = config_parse.find_objects(r'^object-group network')

    services = config_parse.find_objects(r'^object service')

    srv_in_grps = config_parse.find_objects(r'^ port-object ')

    service_groups = config_parse.find_objects(r'^object-group service')

    for host in hosts_in_grps:
        append_hosts(host.text)

    for net in nets_in_grps:
        append_nets(net.text)

    print("config firewall address")
    for obj in objects:
        if type(obj) != list:
            format_addr(obj.text)
        else: 
            format_addr(obj)
    print("end")

    print("config firewall service custom")
    for srv in services:
        format_srv(srv.text)
    print("end")

    print("config firewall addrgrp")
    for grp in groups:
        format_addr_grp(grp.text)
    print("end")

    print("config firewall service group")
    for srv_grp in service_groups:
        format_srv_grp(srv_grp.text)
    print("end")

