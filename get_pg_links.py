
import sys, socket, os, json, subprocess, getpass

def runBashCommand(command):
    command = command.strip()
    exit_code = os.system(command)
    if(exit_code != 0):
        print(command)
        print('EXITED...!!!!' + str(exit_code))
        sys.exit()


def runBashCommandGetOutput(command):
    return subprocess.check_output(command, shell=True).strip().decode()

user = getpass.getuser()
ls = runBashCommandGetOutput('''gcloud compute instances list | grep master| awk \'{print $1}\'''').split('\n')
ls.remove('compute-master')
cmd = "\"python3 -c \\\"import sys, json; print(json.load(open('/home/sumit/master_database_url.json', 'r'))['URL'])\\\"\""
getIp = "\"python3 -c \\\"from requests import get;ip = get('https://api.ipify.org').text;print('public IP:', ip)\\\"\""
for i in ls:
    print(i)
    runBashCommand("gcloud compute ssh --zone \"us-east1-b\" --ssh-flag=\"-ServerAliveInterval=30\" " + user + "@"+i+" --command "+cmd)
    runBashCommand("gcloud compute ssh --zone \"us-east1-b\" --ssh-flag=\"-ServerAliveInterval=30\" " + user + "@"+i+" --command "+ getIp)
    print('\n')