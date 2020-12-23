#!/usr/bin/python
#Purpose: Ask whois for each IP seen in log file, then print out the associated Organization returned.

import socket
from datetime import datetime as dt
import time

REMOTE = []
OUTPUT = []

def whois(ip):

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("whois.arin.net", 43))
    s.send(('n ' + ip + '\r\n').encode())

    response = b""

    startTime = time.mktime(dt.now().timetuple())
    timeLimit = 3
    while True:
        elapsedTime = time.mktime(dt.now().timetuple()) - startTime
        data = s.recv(4096)
        response += data
        if (not data) or (elapsedTime >= timeLimit):
            break
    s.close()

    return(response.decode())

with open("./ip-logs") as infile:
    REMOTE = infile.read().splitlines()

for ip in REMOTE:
    reversed_dns = ""
    PRIOR = ""
    WHO = [""]
    LINE = ""
    ORG = ""
    if ip in OUTPUT:
        for line in OUTPUT:
            if ip in line:
                OUTPUT.append(line)
                break
    else:
        try:
            reversed_dns = socket.gethostbyaddr(ip)
        except Exception:
            reversed_dns = " "
        try:
            WHO = (whois(ip)).splitlines()
        except:
            WHO = " "
        for line in WHO:
            if "Organization:" in line:
                ORG = line
                break
        LINE = ip + " " + str(reversed_dns[0]) + " " + ''.join(ORG)
        OUTPUT.append(LINE)

for line in OUTPUT:
    print line

#FIN
