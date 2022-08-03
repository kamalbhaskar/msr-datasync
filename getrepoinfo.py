from re import X
from urllib.request import HTTPBasicAuthHandler
import requests
import json
import os
import shutil
import logging
import logconf

#Setup logging
logconf.setup_logging()
logger = logging.getLogger(__name__)

MSR_HOSTNAME = input("Enter the MSR hostname and press [ENTER]:")
MSR_USER = input("Enter the MSR username and press [ENTER]:")
MSR_PASSWORD = input("Enter the MSR token or password and press [ENTER]:")

NAMESPACE = input("Org/Namespace(all):")
REPO_FILE = input("Repositories file(repositories.json):")
REPO_TAG_INFO = input("Repositories with tags info(repo_tags):")
REPO_COUNT_FILE = input("Repository Count file(repo_count):")

#Setting defaults
if NAMESPACE == "":
    NAMESPACE = "all"
    print(NAMESPACE)

if REPO_FILE == "":
    REPO_FILE = NAMESPACE + "_repositories.json"
    print(REPO_FILE)

if REPO_TAG_INFO == "":
    REPO_TAG_INFO = NAMESPACE + "_repo_tags"
    print(REPO_TAG_INFO)

if REPO_COUNT_FILE == "":
    REPO_COUNT_FILE = NAMESPACE + "_repo_count"
    print(REPO_COUNT_FILE)

if os.path.exists(REPO_FILE):
    os.remove(REPO_FILE)

if os.path.exists(REPO_COUNT_FILE):
    os.remove(REPO_COUNT_FILE)

if os.path.exists("tags"):
    shutil.rmtree("tags")

#Prepare the API call
URL = 'https://' + MSR_HOSTNAME + '/api/v0/repositories/'
print(URL)
PARAMS = {'pageSize':'100000', 'count':'true'}
HEADERS = {"accept": "application/json"}

#GET repositories
resp = requests.get(url = URL, auth = (MSR_USER , MSR_PASSWORD) , params = PARAMS, headers = HEADERS, verify=False)
data = resp.json()
#print(data)
json_data = json.dumps(data)
dict_repos = json.loads(json_data)

#Dump repositories to REPO_FILE
outfile = open(REPO_FILE, "w")
json.dump(dict_repos['repositories'], outfile)
outfile.close()

#Get number of repos
reponum = len(dict_repos['repositories'])
#print(reponum)

#Fetch tags for the repositories
for repo in dict_repos['repositories']:
    #print(repo)
    repons = repo['namespace']
    reponame = repo['name']
    repourl = 'https://' + MSR_HOSTNAME + '/api/v0/repositories/' + repons + '/' + reponame + '/tags'
    #print(URL)
    repoparams = {'pageSize':'1000000'}
    #Send API call
    resp = requests.get(url = repourl, auth = (MSR_USER , MSR_PASSWORD) , params = repoparams, verify=False)
    data = resp.json()
    json_data = json.dumps(data)
    list_tags = json.loads(json_data)
    tagcount = len(list_tags)
    #tagnames = list_tags['name']
    #print(data)
    if not os.path.exists('tags'):
        os.makedirs('tags')
    tagfilepath = "tags"
    tagfilename = repons + "_" + reponame + '.json'
    outfile_tags = open(os.path.join(tagfilepath, tagfilename), "a")
    json.dump(data, outfile_tags)
    outfile_cnt = open(REPO_COUNT_FILE, "a")
    outfile_cnt.write(repons + "," + reponame + "," + str(tagcount) + "\n")
outfile_tags.close()
outfile_cnt.close()