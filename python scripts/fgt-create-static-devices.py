#!/usr/bin/python
#Get Device Data from Fortigate, then prep static device configs for each Device seen by FGT

import requests
import smtplib

CREDS = 'username=cisco&secretkey=ciscocisco'
LOGIN_URL = 'https://10.1.1.1:8443/logincheck'
DATA_URL = 'https://10.1.1.1:8443/api/v2/monitor/user/device/select/'

def iter_leafs(entry, item):
    for key, val in entry.iteritems():
        if isinstance(val, dict) and key == item:
          for key, value in val.iteritems():
            if key == "name":
              return value

with requests.Session() as s:
    s.post(LOGIN_URL, data=CREDS, verify=False)

    r = s.get(DATA_URL, verify=False)
    RETURN_DATA = r.json()


print "config user device"
for entry in RETURN_DATA['results']:
    print "edit \"" + str(iter_leafs(entry, "host")) + " " + str(iter_leafs(entry, "user")) + "\""
    print "set mac " + entry.get('mac')
    print "set type " + str(iter_leafs(entry, "os"))
    print "next"
print "end

#end
