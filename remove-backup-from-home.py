
import sys, socket, os, json, subprocess, getpass

def runBashCommand(command):
    command = command.strip()
    exit_code = os.system(command)
    if(exit_code != 0):
        print(command, "Error/File Not found")
        #print('EXITED...!!!!' + str(exit_code))
        #sys.exit()


def runBashCommandGetOutput(command):
    return subprocess.check_output(command, shell=True).strip().decode()

user = 'sumit'
ls = runBashCommandGetOutput('''gcloud compute instances list |  grep 'slave\\|master' | awk \'{print $1}\'''').split('\n')
ls.remove('compute-master')
cmd = "\"rm 2019*\""
for i in ls:
    print(i)
    runBashCommand("gcloud compute ssh --zone \"us-east1-b\" --ssh-flag=\"-ServerAliveInterval=30\" " + user + "@"+i+" --command "+cmd)
    print('\n')