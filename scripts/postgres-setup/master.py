## this script is to setup master postgres database
import random, string, sys, socket, os, json, re
from subprocess import STDOUT, check_call, check_output

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

def getRamSize():
    return int((os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES'))/(1024.**3)*1024)

def getPostgresConfigFile(url):
    file_path = check_output('psql '+ url +' -t -P format=unaligned  -c "show config_file;"', shell=True)
    if type(file_path)() == b'':
        return file_path.strip().decode("utf-8")

## Creating dj url here
DATABASE = "postgres"
PORT = "5432"
HOST = socket.gethostbyname(socket.gethostname())
USER = "".join( [random.choice(string.ascii_lowercase) for i in xrange(14)] )
PASSWORD = "".join( [random.choice(string.ascii_lowercase + string.digits) for i in xrange(64)] )
NAME = "".join( [random.choice(string.ascii_lowercase) for i in xrange(14)] )
dj_db_url = DATABASE+"://"+USER+":"+PASSWORD+"@"+HOST+":"+PORT+"/"+NAME


SLAVE_IP = input("Enter Slave Server IP: ")
if not re.match(r'[0-9]+(?:\.[0-9]+){3}', SLAVE_IP):
    print('Invalid IP Address')
    sys.exit()


## Installing prosgres
runBashCommand('sudo apt-get install wget ca-certificates')
runBashCommand('wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -')
runBashCommand("sudo sh -c 'echo \"deb http://apt.postgresql.org/pub/repos/apt/ `lsb_release -cs`-pgdg main\" >> /etc/apt/sources.list.d/pgdg.list'")

runBashCommand('sudo apt-get update -qqy')
runBashCommand('sudo apt-get install postgresql-11 -qqy')

## Create SSH keys for "postgres" user
runBashCommand('echo "n\n" | sudo -H -u postgres ssh-keygen  -N ""  -f /var/lib/postgresql/.ssh/id_rsa -q')
runBashCommand('cat /var/lib/postgresql/.ssh/id_rsa.pub | tee /var/lib/postgresql/.ssh/authorized_keys')
#runBashCommand('''echo "echo \""`cat /var/lib/postgresql/.ssh/id_rsa.pub`"\" >> /var/lib/postgresql/.ssh/authorized_keys"''')

## Creating new user and database and giving permissions
runBashCommand('sudo -u postgres psql -c "CREATE ROLE replicate WITH REPLICATION LOGIN;"')
runBashCommand('''sudo -u postgres psql -c "CREATE USER {} REPLICATION LOGIN CONNECTION LIMIT 5 ENCRYPTED PASSWORD '{}';"'''.format(USER, PASSWORD))
runBashCommand('sudo -u postgres psql -c "ALTER ROLE '+ USER +' SUPERUSER;"')
runBashCommand('sudo -u postgres createdb -O ' + USER + ' '+ NAME)


# change this if DB version changes
config_file_path = "/etc/postgresql/11/main/postgresql.conf" # getPostgresConfigFile(dj_db_url)
hg_hba_file_path = "/etc/postgresql/11/main/pg_hba.conf"

ram = getRamSize()

## Allow access to cluster
textToInsertInFile = "host      replication     " + USER + "        " + SLAVE_IP + "/32     md5\n"
filePath = hg_hba_file_path
addLineInFile(filePath, textToInsertInFile)

textToInsertInFile =  "host    all             all             0.0.0.0/0               md5\n"
filePath = hg_hba_file_path
addLineInFile(filePath, textToInsertInFile)

textToFind = "#listen_addresses = 'localhost'"
textToReplace = "listen_addresses = 'localhost,"+ HOST +"'"
filePath = config_file_path
findAndReplace(config_file_path, textToFind, textToReplace)

textToFind = "#wal_level = replica"
textToReplace = "wal_level = 'hot_standby'"
findAndReplace(config_file_path, textToFind, textToReplace)

textToFind = "#archive_mode = off"
textToReplace = "archive_mode = on"
findAndReplace(config_file_path, textToFind, textToReplace)

textToFind = "#archive_command = ''"
textToReplace = "archive_command = 'cd .'"
findAndReplace(config_file_path, textToFind, textToReplace)

textToFind = "#max_wal_senders = 10"
textToReplace = "max_wal_senders = 5"
findAndReplace(config_file_path, textToFind, textToReplace)

textToFind = "#hot_standby = on"
textToReplace = "hot_standby = on"
findAndReplace(config_file_path, textToFind, textToReplace)

textToFind = "timezone = 'Etc/UTC'"
textToReplace = "timezone = 'MST7MDT'"
findAndReplace(config_file_path, textToFind, textToReplace)

textToFind = "log_timezone = 'Etc/UTC'"
textToReplace = "log_timezone = 'MST7MDT'"
findAndReplace(config_file_path, textToFind, textToReplace)

textToFind = "#log_statement = 'none'"
textToReplace = "log_statement = 'all'"
findAndReplace(config_file_path, textToFind, textToReplace)

textToFind = "#log_directory = 'log'"
textToReplace = "log_directory = 'pg_log'"
findAndReplace(config_file_path, textToFind, textToReplace)

textToFind = "#log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'"
textToReplace = "log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'"
findAndReplace(config_file_path, textToFind, textToReplace)

textToFind = "#logging_collector = off"
textToReplace = "logging_collector = on"
findAndReplace(config_file_path, textToFind, textToReplace)

textToFind = "#log_min_error_statement = error"
textToReplace = "log_min_error_statement = error"
findAndReplace(config_file_path, textToFind, textToReplace)

# min_wal_size is 1GB  recommended
textToFind = "#min_wal_size = 80MB"
textToReplace = "min_wal_size = 1GB"
findAndReplace(config_file_path, textToFind, textToReplace)

# max_wal_size is 2GB  recommended
textToFind = "#max_wal_size = 1GB"
textToReplace = "max_wal_size = 4GB"
findAndReplace(config_file_path, textToFind, textToReplace)

textToFind = "#effective_cache_size = 4GB"
textToReplace = "effective_cache_size = " + str(int(ram*(0.75))) + "MB"
findAndReplace(config_file_path, textToFind, textToReplace)

# shared_buffers is 1/4th of ram is recommended
textToFind = "shared_buffers = 128MB"
textToReplace = "shared_buffers = "+ str(int(ram/4)) +"MB"
findAndReplace(config_file_path, textToFind, textToReplace)

# Helps to database backup and restores
textToFind = "#maintenance_work_mem = 64MB"
textToReplace = "maintenance_work_mem = 1024MB"
findAndReplace(config_file_path, textToFind, textToReplace)


textToFind = "#checkpoint_completion_target = 0.5"
textToReplace = "checkpoint_completion_target = 0.7"
findAndReplace(config_file_path, textToFind, textToReplace)

textToFind = "#log_rotation_age = 1d"
textToReplace = "log_rotation_age = 10d"
findAndReplace(config_file_path, textToFind, textToReplace)

textToFind = "#log_truncate_on_rotation = off"
textToReplace = "log_truncate_on_rotation = on"
findAndReplace(config_file_path, textToFind, textToReplace)

# wal_buffers to 16MB is recommended
textToFind = "#wal_buffers = -1"
textToReplace = "wal_buffers = 16MB"
findAndReplace(config_file_path, textToFind, textToReplace)

textToFind = "#random_page_cost = 4.0"
textToReplace = "random_page_cost = 4.0"
findAndReplace(config_file_path, textToFind, textToReplace)

# 1-1000; 0 disables prefetching
textToFind = "#effective_io_concurrency = 1"
textToReplace = "effective_io_concurrency = 2"
findAndReplace(config_file_path, textToFind, textToReplace)

# 2621kB per GB is recommended
textToFind = "#work_mem = 4MB"
textToReplace = "work_mem = "+ str(int((ram/1024)*2621)) +"kB"
findAndReplace(config_file_path, textToFind, textToReplace)

runBashCommand('sudo service postgresql restart')
runBashCommand('tail /var/log/postgresql/postgresql-11-main.log')

data = {}
data["URL"] = dj_db_url
data["HOST"] = HOST
data["USER"] = USER
data["PASSWORD"] = PASSWORD
data["NAME"] = NAME


## Writing credentials to file
with open('master_database_url.json', 'w') as outfile:
    json.dump(data, outfile)

print(dj_db_url)
