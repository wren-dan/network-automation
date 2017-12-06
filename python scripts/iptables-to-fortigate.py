#!/usr/bin/python
#Script Name: ssa-to-fgt.py


import sys
import string
import re
import csv
import argparse
import socket
import struct

def help_funct():
    print "script to convert ssa iptables rule set to fgt address, service, and policy syntax"
    print "pass the csv file obtained from the bae portal as a command line arguement"
    print "this is not meant to be a copy/paste operation, simply to get a start on the conversion"
    print "script does not yet process vip objects and only acts on FORWARD and DROP actions"
    quit()

def cidr_to_netmask(cidr):
    network, net_bits = cidr.split('/')
    host_bits = 32 - int(net_bits)
    netmask = socket.inet_ntoa(struct.pack('!I', (1 << 32) - (1 << host_bits)))
    return network, netmask

def prefix_format(prefix):
    if str(prefix) != "None":
        #seperate multiple prefixes
        if re.search(r',', prefix):
            ip_list = (prefix).split(',')
            for num in ip_list:
                if not re.search(r'/\d', num):
                    num = num + "/32"
                ip_addresses.append(num)
        #if host address doesn't inlucde /32
        if not re.search(r'/\d', prefix):
            prefix = prefix + "/32"
        if not re.search(r',', prefix):
            ip_addresses.append(prefix)
    return

def service_format(service):
    if str(service) != "None":
        service = string.replace(service, ":", "-")
        if re.search(r',', service):
            service_list = (service).split(',')
            for num in service_list:
                services.append(num)
        else:
            services.append(service)
    return

def ip_address_objects():
    print "\n\n---------- address objects to be added to fgt ----------\n\n"
    print "config firewall address"
    for line in range(0, len(ip_addresses)):
        network, netmask = cidr_to_netmask(ip_addresses[line])
        print 'edit "{}"'.format(ip_addresses[line])
        print 'set subnet {} {}'.format(network, netmask)
        print "next"
    print "end\n\n"
    return

def service_objects():
    print "\n\n---------- service objects to be added to fgt ----------\n\n"
    print "config firewall service custom"
    print 'edit "ALL"'
    print 'set protocol IP'
    print 'next'
    for line in range(0, len(services)):
        print 'edit "tcp-{}"'.format(services[line])
        print 'set tcp-portrange {}'.format(services[line])
        print 'next'
        print 'edit "udp-{}"'.format(services[line])
        print 'set udp-portrange {}'.format(services[line])
        print 'next'
    print "end\n\n"
    return

def policy_format():
    print "\n\n---------- policies to be added to fgt ----------\n\n"
    pol_id = 2000
    print "config firewall policy"
    for number in range(0, len(rules)):
        print rules[number] #for debugging
        match = (rules[number]['match']).split(' ')
        args, unknown  = parser.parse_known_args(match[0:])
        if rules[number]['chain'] == 'FORWARD' and rules[number]['action'] != "LOG" and not re.search(r'DEFAULT', rules[number]['description']):
            print "edit", (pol_id + number)
            #print input interface
            if str(args.i) != "None":
                print 'set srcintf "{}"'.format(args.i)
            #print output interface
            if str(args.o) != "None":
                print 'set dstintf "{}"'.format(args.o)
            #print source addresses
            if str(args.s) != "None":
                if re.search(r',', args.s):
                    ip_list = (args.s).split(',')
                    for num in ip_list:
                        if not re.search(r'/\d', num):
                            num = num + "/32"
                    for num in range(0, len(ip_list)):
                        ip_list[num] = '"' + ip_list[num] + '"'
                    ipstr = (' ').join(ip_list)
                    print 'set srcaddr {}'.format(ipstr)
                else:
                    if not re.search(r'/\d', args.s):
                        args.s = args.s + "/32"
                    print 'set srcaddr "{}"'.format(args.s)
            #prints destination addresses
            if str(args.d) != "None":
                if re.search(r',', args.d):
                    ip_list = (args.d).split(',')
                    for num in ip_list:
                        if not re.search(r'/\d', num):
                            num = num + "/32"
                    for num in range(0, len(ip_list)):
                        ip_list[num] = '"' + ip_list[num] + '"'
                    ipstr = (' ').join(ip_list)
                    print 'set dstaddr {}'.format(ipstr)
                else:
                    if not re.search(r'/\d', args.d):
                        args.d = args.d + "/32"
                    print 'set dstaddr "{}"'.format(args.d)
            print 'set schedule "always"'
            #print action
            if rules[number]['action'] == 'ACCEPT':
                print "set action accept"
            if rules[number]['action'] == 'DROP':
                print "set action deny"
            #print destination ports
            ports = []
            prot = ""
            if str(args.dport) != "None":
                if re.search(r',', args.dport):
                    ports = (args.dport).split(',')
                if not re.search(r',', args.dport):
                    ports.append(args.dport)
            if str(args.dports) != "None":
                if re.search(r',', args.dports):
                    ports = (args.dports).split(',')
                if not re.search(r',', args.dports):
                    ports.append(args.dports)
            for num in range(0, len(ports)):
                if args.p == "udp":
                    ports[num] = '"udp-' + ports[num] + '"'
                if args.p == "tcp":
                    ports[num] = '"tcp-' + ports[num] + '"'
            servicestr = (' ').join(ports)
            servicestr = string.replace(servicestr, ":", "-")
            if len(servicestr) > 0:
                print "set service {}".format(servicestr)
            print 'set comments "{}"'.format(rules[number]['description'])
            print "next"
        else:
            skipped.append(rules[number])
    print "end"

# Map row to dictionary (dictionary comprehension)
def rule(column_names, row):
    return {column_names[column]: data for column, data in enumerate(row) if column < len(column_names)}

#program start
if len(sys.argv) != 2:
    quit("Feed me a csv to parse")
if sys.argv[1] in ("--help", "--Help", "-h", "-H"):
    help_funct()

# Map CSV file to list of dictionaries (list comprehension)
rules = [rule(['ruleid', 'match', 'chain', 'action', 'description'], row) for row in csv.reader(open(sys.argv[1], 'r'))]

parser = argparse.ArgumentParser()
#add our known match arguements to parse through
parser.add_argument("-s")
parser.add_argument("-d")
parser.add_argument("-i")
parser.add_argument("-o")
parser.add_argument("-p")
parser.add_argument("-m")
parser.add_argument("--dport")
parser.add_argument("--dports")

ip_addresses = []
services = []
skipped = []

#parse the match data and build our address and services lists
for number in range(0, len(rules)):
    match = (rules[number]['match']).split(' ')
    args, unknown  = parser.parse_known_args(match[0:])

    prefix_format(args.s)

    prefix_format(args.d)

    service_format(args.dport)

    service_format(args.dports)

ip_addresses = sorted(set(ip_addresses))
services = sorted(set(services))

ip_address_objects()

service_objects()

policy_format()

print "\n\n---------- The following rules were not processed by this script: ----------\n\n"
for number in range(0, len(skipped)):
    print skipped[number]
