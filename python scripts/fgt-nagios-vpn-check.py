#!/usr/bin/python
#script to confirm VPN status for nagios monitor on Fortigates
#Takes 3 arguments - CREDS VPN_PEER DEVICE

import requests
import sys

LOGIN_LOC = '.int.me.com:8443/logincheck'
DATA_LOC = '.int.me.com:8443/api/v2/monitor/vpn/ipsec/'
CREDS = ""
VPN_PEER = "invalid"
DEVICE = ""
tunnels = []
up = 0

#Require Credentials, a vpn peer, and a device name as command line arguments or script exists
if len(sys.argv) == 4:
    CREDS = sys.argv[1]
    VPN_PEER = sys.argv[2]
    DEVICE = sys.argv[3]
else:
    print("CRITICAL - Script Argument ERROR")
    sys.exit(2)

if VPN_PEER != "site1-VPN" and VPN_PEER != "office-VPN" and VPN_PEER != "site2-VPN": 
    print("CRITICAL - Script Peer Argument ERROR")
    sys.exit(2)   

if DEVICE == "site1-fgt":
    LOGIN_URL = "https://site1-fgt" + LOGIN_LOC
    DATA_URL = "https://site1-fgt" + DATA_LOC
elif DEVICE == "site2-fgt": 
    LOGIN_URL = "https://site2-fgt" + LOGIN_LOC
    DATA_URL = "https://site2-fgt" + DATA_LOC
else:
    print("CRITICAL - Script Argument ERROR")
    sys.exit(2)

# Use 'with' to ensure the session context is closed after use.
with requests.Session() as s:
    # Set up authenticated session.
    s.post(LOGIN_URL, data=CREDS, verify=False)
    # Obtain data and format to json
    r = s.get(DATA_URL, verify=False)
    if r.status_code == 200: RETURN_DATA = r.json()

#Grab the list of ipsec tunnels for a given peer
if r.status_code == 200 and RETURN_DATA['results']:
    for entry in RETURN_DATA['results']:
        if entry.get('name') == VPN_PEER:
            tunnels = entry.get('proxyid')
            break
else:
    print("CRITICAL - No Data Returned ERROR")
    sys.exit(2)

#Determine if any of the ipsec tunnels are listed as up and active
for tunnel in tunnels:
	if tunnel.get('status') == 'up':
		up = 1
	else: pass

if up: 
    print("OK - " + VPN_PEER + " is UP on " + DEVICE)
else: 
    print("CRITICAL - " + VPN_PEER + " is DOWN on " + DEVICE)
    sys.exit(2)
