#!/usr/bin/python

import sys
import csv
import socket

# Map row to dictionary (dictionary comprehension)
def interface(column_names, row):
    return {column_names[column]: data for column, data in enumerate(row) if column < len(column_names)}

def replace_all(text, dic):
    for i, j in dic.iteritems():
        text = text.replace(i, j)
    return text

#program start
if len(sys.argv) != 2:
    quit("Feed me a csv to parse")

# define desired replacements here
replace = {"Loopback": "lo",
           "nV-Loopback": "lo",
           "nV-": "",
           "MgmtEth0/RP0/CPU0/": "mgmt",
           "MgmtEth0-RP0-CPU0-": "mgmt",
           "EINT0/RSP0/CPU": "mgmt",
           "EINT0-RSP0-CPU": "mgmt",
           "MgmtEth0/RSP0/CPU0/": "mgmt",
           "MgmtEth0-RSP0-CPU0-": "mgmt",
           "TenGigE": "te",
           "TenGigabitEthernet": "te",
           "Tenge": "te",
           "GigabitEthernet": "ge",
           "Bundle-Ether": "be",
           "Port-channel": "po",
           "FastEthernet": "fe",
           "Vlan": "vl",
           "Tunnel": "tu",
           "/": "-"}

# Map CSV file to list of dictionaries (list comprehension)
interfaces = [interface(['version', 'intdotdevice', 'ip', 'reverse'], row) for row in csv.reader(open(sys.argv[1], 'r'))]

delete = {}
to_add = {}
good = {}

# loop through each line of csv data
for number in range(0, len(interfaces)):
    fqdn = ""
    no_dns = False
    reversed_dns = [""]
    # adjust interface names per replace dictionary
    intdotdevice = replace_all(interfaces[number]['intdotdevice'], replace )
    # only worried about v4 right now
    if interfaces[number]['version'] == "ipv4":
        try:
            #dns query for each interface ip
            reversed_dns = socket.gethostbyaddr(interfaces[number]['ip'])
        except Exception:
            no_dns = True
        fqdn = intdotdevice + ".default.net"
        # compare dns results with csv data and place data into dicts
        if reversed_dns[0].lower() != fqdn.lower():
            if not no_dns:
                delete[reversed_dns[0]] = interfaces[number]['reverse']
            to_add[fqdn] = interfaces[number]['reverse']
        else:
            good[fqdn] = interfaces[number]['reverse']

print "Records to be deleted:"
print "Total records to be deleted:" + str(len(delete))
for key, value in delete.iteritems():
    print "addrr --del", value, "IN PTR", key
print "Records to be added:"
print "total records to be added:" + str(len(to_add))
for key, value in to_add.iteritems():
    print "addrr", value, "IN PTR", key
print "The following DNS Records will not be changed:"
for key, value in good.iteritems():
    print key, value
