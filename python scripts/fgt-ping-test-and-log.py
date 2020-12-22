#!/usr/bin/python3
#Purpose: Use netmiko to log into Fortigate and run pings every minute, then log Results to Troubleshoot Connectivity issues.

from netmiko import ConnectHandler
from datetime import datetime
from getpass import getpass
import time

firewall = {
    'device_type': 'fortinet',
    'ip': '10.1.1.1',
    'username': 'USER',
    'password': getpass(),
}

command = "exec ping 192.168.249.3"

while True:
    with ConnectHandler(**firewall) as net_connect:
        output = net_connect.send_command(command, delay_factor=2)

    update = ""; rtt = ""

    for line in output.split("\n"):
        if "packet loss" in line:
            update = line 
        elif "round-trip" in line:
            rtt = line 

    file = open('./ping_log', "a")  
    file.write(str(datetime.now()) + " | " + update + " | " + rtt + "\n") 
    file.close() 

    net_connect.disconnect()

    print(str(datetime.now()) + " " + "Sleeping")

    time.sleep(16)



