#!/usr/bin/python3
#Purpose: Parse Fortigate logs in csv format, then pass them to numpy to organize by most seen, then print

import numpy as np

def line_parser(line):
    log_entry = {}
    for item in line.split():
        if "=" in item:
            k,v = item.split('=',1)
            log_entry.update({k : v.strip('\"')})
    return(log_entry)

if __name__ == "__main__":

    logs_list = []
    sessions = []
    
    with open('/mnt/c/users/me/Documents/misc/fgt-logs.csv') as file:
        logs = file.readlines()

    for line in logs:
        logs_list.append(line_parser(line))

    for log in logs_list:
        if log.get('srcip') and log.get('dstip') and log.get('proto') and log.get('dstport'):
            sessions.append(log.get('proto') + " " + log.get('srcip') + " " + log.get('dstip') + " " + log.get('dstport'))

    session,count = np.unique(sessions,return_counts = True) 

    sorted_sessions = np.argsort(-count)

    output = "\n".join("{} {}".format(x, y) for x, y in zip(count[sorted_sessions], session[sorted_sessions]))

    print(output)
