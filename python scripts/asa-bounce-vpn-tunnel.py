#!/usr/bin/python
#Bounce VPN tunnel
#version 0.1 /Auth DWren

import base64
import json
import sys
import urllib2
import ssl

RESPONSE = None
VPN_PEER = "Invalid"
DATA_URL = "https://10.1.1.1/api/cli"
USER = "USER"
PWD = "REMOVED"
RESPONSE = ""
DATA = "NONE"
CAFILE = "./root.crt"
headers = {'Content-Type': 'application/json'}

#Confirm argument given is a valid IP
def validIP(address):
    parts = address.split(".")
    if len(parts) != 4:
        return False
    for item in parts:
        if not 0 <= int(item) <= 255:
            return False
    return True

#Require a valid IP as command line arguement or script exists
if len(sys.argv) == 2 and validIP(sys.argv[1]):
    VPN_PEER = sys.argv[1]
else:
    sys.exit("Valid VPN Peer IP required as command line argument")

#command to send to asa
post_data = {"commands": ["show vpn-sessiondb detail l2l filter ipaddress " + VPN_PEER]}

#Make request to asa including auth info and cli command
req = urllib2.Request(DATA_URL, json.dumps(post_data), headers)
base64string = base64.encodestring('%s:%s' % (USER, PWD)).replace('\n', '')
req.add_header("Authorization", "Basic %s" % base64string)
try:
    RESPONSE = urllib2.urlopen(req, cafile= CAFILE)
    status_code = RESPONSE.getcode()
    DATA = RESPONSE.read()
    #Need different commands for ikev1 and v2 peers
    if "IKEv2" in DATA:
        post_data = {"commands": ["clear crypto ikev2 sa " + VPN_PEER]}
        req = urllib2.Request(DATA_URL, json.dumps(post_data), headers)
        base64string = base64.encodestring('%s:%s' % (USER, PWD)).replace('\n', '')
        req.add_header("Authorization", "Basic %s" % base64string)
        RESPONSE = urllib2.urlopen(req, cafile= CAFILE)
        status_code = RESPONSE.getcode()
        if status_code == 200:
            print "IKEv2 VPN Peer: " + VPN_PEER + " successfully bounced"
    elif "IKEv1" in DATA:
        post_data = {"commands": ["clear crypto ikev1 sa " + VPN_PEER]}
        req = urllib2.Request(DATA_URL, json.dumps(post_data), headers)
        base64string = base64.encodestring('%s:%s' % (USER, PWD)).replace('\n', '')
        req.add_header("Authorization", "Basic %s" % base64string)
        RESPONSE = urllib2.urlopen(req, cafile= CAFILE)
        status_code = RESPONSE.getcode()
        if status_code == 200:
            print "IKEv1 VPN Peer: " + VPN_PEER + " successfully bounced"
    else:
        print "Error - Unable to Bounce VPN Peer: " + VPN_PEER
except urllib2.HTTPError, err:
    print "Error received from server. HTTP Status code :"+str(err.code)
    try:
        json_error = json.loads(err.read())
        if json_error:
            print json.dumps(json_error,sort_keys=True,indent=4, separators=(',', ': '))
    except ValueError:
        pass
finally:
    if RESPONSE:  RESPONSE.close()
