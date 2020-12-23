#!/usr/bin/python
#GET Current IP Range data from Incapsula/Imperva, then email if any changes are seen

import json
import urllib2
import ssl
import smtplib

INCAP_IP_FILE = "./incapips.txt"
DATA_URL = "https://my.incapsula.com/api/integration/v1/ips"
RESPONSE = ""
SEND_DATA = "resp_format=json"
IP_NOW = []
sender = 'me@me.com'
receiver = ['me@me.com','me@me.com']
message = """From: me@me.com
To: me@me.com
CC: me@me.com
Subject: Incapsula NEW IP Range discovered <TEST Please Ignore>

New Incapsula IP Range Discovered - Need to add the following to allow list: <TEST Please Ignore>
"""


#Read IP Range data from previous script run.
with open(INCAP_IP_FILE) as infile:
    IP_PRIOR = infile.read().splitlines()

#Make request to Incapsula
req = urllib2.Request(DATA_URL, json.dumps(SEND_DATA))
try:
    RESPONSE = urllib2.urlopen(req)
    status_code = RESPONSE.getcode()
    DATA = json.load(RESPONSE)
    for entry in DATA['ipRanges']:
        IP_NOW.append(entry)
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

#compute whether any IP Ranges have been added since last script run.
DIFF = list(set(IP_NOW).difference(set(IP_PRIOR)))

# #If any IP Ranges have been added, send email to Jira to open tix.
if DIFF:
    message = message + "\n".join(DIFF)
    try:
        smtpObj = smtplib.SMTP('10.1.1.25', 25)
        smtpObj.sendmail(sender, receiver, message)
        print "Successfully sent email"
    except SMTPException:
        print "Error: unable to send email"

# Save current IP Range data to file for next script run comparison.
with open(INCAP_IP_FILE, "w") as outfile:
    outfile.write("\n".join(IP_NOW))
