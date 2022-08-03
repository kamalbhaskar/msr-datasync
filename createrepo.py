from urllib.request import HTTPBasicAuthHandler
import requests
import threading
import json
import logging
import logconf


#Setup logging
logconf.setup_logging()
logger = logging.getLogger(__name__)


def generatetoken(msr_fqdn, username, password):
    #Generate AUTH_TOKEN
    URL = 'https://' + msr_fqdn + '/auth/token'
    logger.info("Generating AUTH_TOKEN for %s with user %s", URL, username)
    PARAMS = {}
    HEADERS = {"accept": "application/json"}
    resp = requests.get(url = URL, auth = (username , password) , params = PARAMS, headers = HEADERS, verify=False)
    data = resp.json()
    #print(data)
    json_data = json.dumps(data)
    dict_data = json.loads(json_data)
    if resp.status_code == "200":
        TOKEN = dict_data['token']
        logger.info("Generated AUTH_TOKEN: %s successfully.", TOKEN)
        return TOKEN
    else:
        print("Token generation failed with error:\n" + resp.json())
        logger.error("Token generation failed with error:\n%s", resp.json())
        return 1
    

def createrepo(msr_fqdn, token, repofile, offset, workers):
    #load REPO_FILE
    dict_repos = json.loads(repofile)

    logger.info("Creating repositiories")
    ROWCOUNT = 1
    for repo in dict_repos['repositories']:
        repocount = len(dict_repos['repositories'])
        share = repocount / workers
        startpoint = (share * (offset - 1)) + 1
        endpoint = share * offset
        if ROWCOUNT >= startpoint and ROWCOUNT <= endpoint:
            #check if repo exists already
            #TO-DO
            #create the repo
            repons = repo['namespace']
            reponame = repo['name']
            repodetails = repo['id']
            logger.info("Creating repository: %s/%s", repons, reponame)
            REPOURL = 'https://' + msr_fqdn + '/api/v0/repositories/' + repons
            PARAMS = {}
            HEADERS = {"accept": "application/json", "content-type": "application/json",  "Authorization": "Bearer" + token}
            response = requests.post(url = REPOURL, data = json.dumps(repodetails), params = PARAMS, headers = HEADERS, verify=False)
            if response.status_code == "200":
                print("Repo: " + repons + "/" + reponame + "created.")
                logger.info("Repository: %s/%s created.", repons, reponame)
            else:
                print("Creation for Repo: " + repons + "/" + reponame + "failed with error:\n" + response.json())
                logger.error("Creation for Repo: %s/%s failed with error:\n%s", repons, reponame, response.json())
        elif ROWCOUNT > endpoint:
            return 0
        else:
            ROWCOUNT += 1


class Repo (threading.Thread):
   def __init__(self, msr_fqdn, authtoken, repofile, offset, workers):
      threading.Thread.__init__(self)
      self.msr_fqdn = msr_fqdn
      self.authtoken = authtoken
      self.repofile = repofile
      self.offset = offset
      self.workers = workers
   def run(self):
      logger.debug("Starting thread %s/%s", self.offset, self.name)
      createrepo(self.msr_fqdn, self.authtoken, self.repofile, self.offset, self.workers)
      logger.debug("Exiting thread %s/%s", self.offset, self.name)




def main ():
    MSR_HOSTNAME = input("Enter the MSR hostname and press [ENTER]:")
    logger.info("MSR Hostname is set to %s", MSR_HOSTNAME)
    MSR_USER = input("Enter the MSR username and press [ENTER]:")
    logger.info("MSR Username is set to %s", MSR_USER)
    MSR_PASSWORD = input("Enter the MSR token or password and press [ENTER]:")

    NAMESPACE = input("Org/Namespace(all):")
    REPO_FILE = input("Repositories file(repositories.json):")
    #Setting defaults
    if NAMESPACE == "":
        NAMESPACE = "all"
        print(NAMESPACE)

    if REPO_FILE == "":
        REPO_FILE = NAMESPACE + "_repositories.json"
        print(REPO_FILE)

    TOKEN = generatetoken(MSR_HOSTNAME, MSR_USER, MSR_PASSWORD)
    if TOKEN == 1:
        print("Authentication token generation failed. Exiting.")
        logger.error("Authentication token generation failed. Exiting.")
        exit
    else:
        WORKERS = 5
        COUNT = 1
        while COUNT <= WORKERS:
            thread = Repo(MSR_HOSTNAME, TOKEN, REPO_FILE, COUNT, WORKERS)
            thread.start()
            thread.join()
            COUNT += 1

main()