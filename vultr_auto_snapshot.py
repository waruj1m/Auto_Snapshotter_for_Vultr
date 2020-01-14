import re
import time
import datetime
import requests

# ------------- User setting START -------------- #

# your vultr api_key
API_KEY = "N7BDQAJE5H5NGOYZPU4HEI3VZLYEVOOELEPA"

# The server's ip or subid which 
MAIN_IP = "45.76.246.164"
SUBID = None

BACKUP_TAG_PREFIX = "auto_backup"
MAX_NUM_OF_BACKUPS = 10

# ------------- User setting END   -------------- #

# Get base info
api_endpoint = "https://api.vultr.com/v1/"
day = time.strftime("%Y-%m-%d", time.localtime()) 


# simple wrapper to access vultr api
def vultr(method = "GET",action = "" , data = None):
    return requests.request(method,"{}{}".format(api_endpoint,action),headers = {"API-Key" : API_KEY}, data=data)


server_list = vultr("GET","server/list").json()

# Find subid if not set.
if SUBID == None:
    for server_subid,server_info in server_list.items():
        if server_info.get("main_ip", None) == MAIN_IP:
            SUBID = server_subid
            break

    if SUBID == None:
        raise Exception("Fail to find subid for IP: {}".format(MAIN_IP))

snapshot_list_raw = vultr("GET","snapshot/list").json()

# Resort the raw snapshot list dict to list obj
snapshot_list = [v for k,v in snapshot_list_raw.items()]

# Get auto-backup snapshot list
backup_snapshot_list = list(filter(lambda x:re.search("{}-{}".format(BACKUP_TAG_PREFIX,SUBID),x["description"]),snapshot_list))

# Remove old auto-backup-snapshot
if len(backup_snapshot_list) >= MAX_NUM_OF_BACKUPS:
    to_remove_snapshot_list = sorted(backup_snapshot_list,
    key = lambda k:datetime.datetime.strptime(k["date_created"],"%Y-%m-%d %H:%M:%S")
    )[:-MAX_NUM_OF_BACKUPS]
    
    for s in to_remove_snapshot_list:
        vultr("POST","snapshot/destroy",{"SNAPSHOTID": s["SNAPSHOTID"]})

# create New auto-backup-snapshot
vultr("POST","snapshot/create",{"SUBID": SUBID,"description": "{}-{}-{}".format(BACKUP_TAG_PREFIX,SUBID,day)})


