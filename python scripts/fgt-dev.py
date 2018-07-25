#!/usr/bin/python
#GET known devices data from CMT Office FGT, Compare with last GET, email if new devices are present.

import requests
import smtplib

# Variable for location of stored mac list from previous script run.
MAC_FILE = './fgt-mac-list.txt'
CREDS = 'username=USER&secretkey=REMOVED'
LOGIN_URL = 'https://10.1.1.1:8443/logincheck'
DATA_URL = 'https://10.1.1.1:8443/api/v2/monitor/user/device/select/'
MACS_NOW = []
DIFF = []
DEVICE = []
UPDATE = []
sender = 'me@me.com'
receiver = 'me@me.com'
message = """From: me@me.com
To: me@me.com
Subject: new device discovered

New Device(s) Discovered:
"""

#function to snag data from nested Dictionary
def iter_leafs(entry, item):
    for key, val in entry.iteritems():
        if isinstance(val, dict) and key == item:
          for key, value in val.iteritems():
            if key == "name":
              return value

#Read mac data from previous script run.
with open(MAC_FILE) as infile:
    MACS_PRIOR = infile.read().splitlines()

# Use 'with' to ensure the session context is closed after use.
with requests.Session() as s:
    # Set up authenticated session.
    s.post(LOGIN_URL, data=CREDS, verify=False)

    # GET known device data from fgt and place into variable using json method.
    r = s.get(DATA_URL, verify=False)
    RETURN_DATA = r.json()

#capture current mac data from the list of nested dictionaries.
for entry in RETURN_DATA['results']:
    MACS_NOW.append(entry.get('mac'))
    NAME = iter_leafs(entry, "host")
    OS =  iter_leafs(entry, "os")
    USER = iter_leafs(entry, "user")
    DEVICE.append(entry.get('mac') + " " +
                  entry.get('interface', "Unknown-Interface") + " " +
                  entry.get('manufacturer', "Unknown-Manufacturer") + " " +
                  entry.get('addr', "Unknown-IP") + " " +
                  str(OS) + " " + str(NAME) + " " + str(USER)
                  )


#compute whether any macs have been added since last script run.
DIFF = list(set(MACS_NOW).difference(set(MACS_PRIOR)))

# #If any mac's have been added, send email to team
if DIFF:
    for mac in DIFF:
        for dev in DEVICE:
            if mac in dev:
                UPDATE.append(dev)
    message = message + "\n".join(UPDATE)
    try:
        smtpObj = smtplib.SMTP('10.1.1.255', 25)
        smtpObj.sendmail(sender, receiver, message)
        print "Successfully sent email"
    except SMTPException:
        print "Error: unable to send email"

# Save current mac data to file for next script run comparison.
with open(MAC_FILE, "w") as outfile:
    outfile.write("\n".join(MACS_NOW))

# #end
