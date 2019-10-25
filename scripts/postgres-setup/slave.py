## this script is to setup slave postgres database
import random, string, sys, socket, os, json, re
from subprocess import STDOUT, check_call
from urllib.parse import urlparse

try:
    xrange
except NameError:
    xrange = range

def findAndReplace(filePath, findLine, replaceLine):
    s = open(filePath).read()
    s = s.replace(findLine, replaceLine)
    f = open(filePath, 'w')
    f.write(s)
    f.close()

def addLineInFile(filePath, textToInsertInFile):
    with open(filePath, "r+") as file:
        for line in file.readlines():
            if textToInsertInFile in line:
               break
        else:
            file.write(textToInsertInFile+'\n')

def runBashCommand(command):
    command = command.strip()
    exit_code = os.system(command)
    if(exit_code != 0):
        os.system('printbanner '+ str(exit_code))
        os.system('printbanner exited')
        sys.exit()

MASTER_URL = input("Enter master postgres URL: ")
DB_NAME = input("Enter master postgres DATABASE NAME: ")
result = urlparse(MASTER_URL)

if not (result.hostname):
    sys.exit()

## Installing prosgres
runBashCommand('sudo apt-get install wget ca-certificates')
runBashCommand('wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -')
runBashCommand("sudo sh -c 'echo \"deb http://apt.postgresql.org/pub/repos/apt/ `lsb_release -cs`-pgdg main\" >> /etc/apt/sources.list.d/pgdg.list'")

runBashCommand('sudo apt-get update -qqy')
runBashCommand('sudo apt-get install postgresql-11 -qqy')
runBashCommand('sudo service postgresql stop')

lineToAdd = 'host   '+ DB_NAME +'   '+ result.username +' '+ result.hostname +'/32    md5'
addLineInFile('/etc/postgresql/11/main/pg_hba.conf', lineToAdd)

runBashCommand('echo "n\n" | sudo -H -u postgres ssh-keygen  -N ""  -f /var/lib/postgresql/.ssh/id_rsa -q')
runBashCommand('cat /var/lib/postgresql/.ssh/id_rsa.pub | tee /var/lib/postgresql/.ssh/authorized_keys')

runBashCommand("mv /var/lib/postgresql/11/main /var/lib/postgresql/11/main_old")
#runBashCommand("sudo mkdir -p /var/lib/postgresql/11/main/")
runBashCommand("sudo -u postgres pg_basebackup -h " + result.hostname + " -D /var/lib/postgresql/11/main -U "+ result.username +" -P -v")
runBashCommand("sudo touch /var/lib/postgresql/11/main/recovery.conf")

lineToAdd = "standby_mode = 'on'"
addLineInFile('/var/lib/postgresql/11/main/recovery.conf', lineToAdd)

lineToAdd = "primary_conninfo = 'host="+ result.hostname +" port=5432 user="+ result.username +" password=" + result.password + "'"
addLineInFile('/var/lib/postgresql/11/main/recovery.conf', lineToAdd)

lineToAdd = "trigger_file = '/tmp/postgresql.trigger."+ str(result.port) +"'"
addLineInFile('/var/lib/postgresql/11/main/recovery.conf', lineToAdd)


textToFind = "timezone = 'Etc/UTC'"
textToReplace = "timezone = 'MST7MDT'"
filePath = "/etc/postgresql/11/main/postgresql.conf"
findAndReplace(filePath, textToFind, textToReplace)

textToFind = "log_timezone = 'Etc/UTC'"
textToReplace = "log_timezone = 'MST7MDT'"
filePath = "/etc/postgresql/11/main/postgresql.conf"
findAndReplace(filePath, textToFind, textToReplace)

runBashCommand("sudo chown postgres.postgres /var/lib/postgresql/11/main/recovery.conf")
runBashCommand("sudo service postgresql start")
runBashCommand("tail /var/log/postgresql/postgresql-11-main.log")
