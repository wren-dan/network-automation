#!/usr/bin/python
#GET local user data from Fortigate, confirm each user has a fortitoken configured, print out users who don't

import requests
import smtplib

CREDS = 'username=cisco&secretkey=ciscocisco'
LOGIN_URL = 'https://10.1.1.1:8443/logincheck'
DATA_URL = 'https://10.1.1.1:8443/api/v2/cmdb/user/local/'
local_users = []

with requests.Session() as s:
    # Set up authenticated session.
    s.post(LOGIN_URL, data=CREDS, verify=False)

    # GET known user data from fgt and place into variable using json method.
    r = s.get(DATA_URL, verify=False)
    RETURN_DATA = r.json()
s.close()

for entry in RETURN_DATA['results']:
    local_users.append({'user': entry.get('name'), 'token': entry.get('fortitoken')})

for item in local_users:
    if not item['token']:
        print item['user']
