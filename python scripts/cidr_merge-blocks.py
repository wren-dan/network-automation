#!/usr/bin/python3
#Purpose: Find and print aggregates for all IP blocks listed in file.

from math import log
from netaddr import cidr_merge

def find_cidr(ip, hosts):
    host_bits = log(hosts) / log(2)
    net_bits = 32 - int(host_bits)
    return(ip + "/" + str(net_bits))


with open('/mnt/c/users/me/Documents/Notes/usip.txt') as raw_ip:
    data = raw_ip.readlines()

non_agg = []; agg = []

for line in data:
    non_agg.append(find_cidr(line.split().pop(0),int(line.split().pop(1))))

agg = cidr_merge(non_agg)

for line in agg:
    print(line)
