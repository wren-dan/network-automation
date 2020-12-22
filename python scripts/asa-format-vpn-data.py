#!/usr/bin/python3
#Purpose: Parse ASA config file for Subnet's/Host's and allowed Port's for VPN Tunnel's and print them out
#todo: mark inactive as not active

import sys
from ciscoconfparse import CiscoConfParse

class grp_search:
    def __init__(self, name):
        self.name = name
        self.dump = self.conf_search(self.name)
        if not self.dump:
            return(False)
        self.objects, self.acls = self.populate(self.dump)
        self.hosts = self.host_search(self.objects)
        self.p_in, self.p_out = self.port_search(self.acls)

    def __str__(self):
        return(self.name)

    def conf_search(self, name):
        results = config_parse.find_children(name)
        if results:
            for idx, val in enumerate(results):
                if val.strip().split().pop() == name and "group" in val:
                    del results[idx]
            return(results)

    def host_search(self, objects):
        hosts = {}
        for obj in objects:
            if "network-object object" in obj or "object network " in obj:
                host = config_parse.find_children("object network " + obj.strip().split().pop())
                if host[0].strip().split().pop() == obj.strip().split().pop():
                    hosts[host[0].strip().split().pop()] = host[1].strip()
            elif "network-object host" in obj:
                hosts[obj.strip().split().pop()] = ""
        return(hosts)

    def port_search(self, acls):
        p_in, p_out = [], []
        for line in acls:
            acllist = line.split()
            if len(acllist) >= 9 and (acllist[-1].strip()).isdigit():
                p_in.append(acllist[-1].strip())
            elif len(acllist) >= 9 and acllist[8].isdigit():
                p_out.append(acllist[8])
            elif len(acllist) >= 10 and acllist[9] == "print_services":
                p_out.append(acllist[9])
            elif len(acllist) >= 9 and acllist[4] == "icmp":
                p_in.append(acllist[4]); p_out.append(acllist[4])
        return(p_in, p_out)

    def populate(self, dump):
        _objects, _acls = [], []
        for item in dump:
            if "group-object" in item:
                dump.extend(self.conf_search(item.strip().split().pop()))
            elif "network-object object " in item:
                temp = self.conf_search(item.strip().split().pop())
                if temp:
                    for item in temp:
                        if "access-list" in item:
                            dump.append(item)
        for item in dump:
            if "network-object object " in item or "network-object host " in item or "object network " in item:
                if item not in _objects: _objects.append(item)
            elif "access-list" in item:
                if item not in _acls: _acls.append(item)
        return(_objects, _acls)

if __name__ == "__main__":
    
    with open('/mnt/c/users/me/Documents/project/misc/asa-configs') as configs:
        config_parse = CiscoConfParse(configs.readlines())

    vpns = []; crypto_maps = []; crypto_peers = []

    crypto_peers = config_parse.find_objects(r'^crypto map Outside_map.*peer')

    crypto_maps = config_parse.find_objects(r'^crypto map Outside_map.*match address')

    for line in crypto_peers:
        linelist = line.text.split(" ")
        index = linelist.index("Outside_map")
        vpns.append({'peer': linelist[index+4].strip(), 'map_id': linelist[index+1]})

    for line in crypto_maps:
        linelist = line.text.split(" ")
        index = linelist.index("Outside_map")
        for vpn in vpns:
            if linelist[index+1] == vpn.get('map_id'):
                vpn['crypto_map'] = linelist[index+4].strip()

    for vpn in vpns:
        vpn['groups'] = []; vpn['grp_obj'] = []; vpn['legacy'] = False
        for item in config_parse.find_children(vpn['crypto_map']):
            if len(item) >=7 and item.split().pop(6) == "Prod_grp": 
                vpn['legacy'] = True
            if item.split().pop(1) == vpn['crypto_map'] and item.split().pop(8) and item.split().pop(8) not in vpn['groups'] and item.strip().split().pop() != "inactive":
                vpn['groups'].append(item.split().pop(8))
               
    for vpn in vpns:
        for grp in vpn['groups']:
            vpn['grp_obj'].append(grp_search(grp)) 

    for vpn in vpns:
        print("*** Peer: " + vpn['peer'] + " Map-Seq: " + vpn['map_id'] + " LegacyIP: " + str(vpn['legacy']) + " Groups: " + " ".join(vpn['groups']) + " ***")
        for obj in vpn['grp_obj']:
            if obj.p_in: print("Inbound Ports: " + " ".join(sorted(set(obj.p_in))))
            if obj.p_out: print("Outbound Ports: " + " ".join(sorted(set(obj.p_out))))
            if obj.hosts: 
                print("Member Objects: ")
                for name, ip in obj.hosts.items():
                    print(name + " " + ip)
        print('\n')
