
import sys, socket, os, json, subprocess, getpass
from utils import getUsernameOrUseDefault 

def runBashCommand(command):
    command = command.strip()
    exit_code = os.system(command)
    if(exit_code != 0):
        print(command)
        print('EXITED...!!!!' + str(exit_code))
        sys.exit()


def runBashCommandGetOutput(command):
    return subprocess.check_output(command, shell=True).strip().decode()

user = getUsernameOrUseDefault()
ls = runBashCommandGetOutput('''gcloud compute instances list |  grep 'slave\\|master' | awk \'{print $1}\'''').split('\n')
ls.remove('compute-master')
cmd = "\"ls\""
for i in ls:
    print(i)
    runBashCommand("gcloud compute ssh --zone \"us-east1-b\" --ssh-flag=\"-ServerAliveInterval=30\" " + user + "@"+i+" --command "+cmd)
    print('\n')
