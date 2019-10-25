import sys
from utils import runBashCommand, runBashCommandGetOutput, getUsernameOrUseDefault


instance_list = runBashCommandGetOutput("gcloud compute instances list | grep master | awk '{print $1}'").split('\n')

user = getUsernameOrUseDefault()

for instance in instance_list:
    print('gcloud compute ssh --zone "us-east1-b" --ssh-flag="-ServerAliveInterval=30" '+ user +'@'+instance+' --command ' + str(sys.argv[1]))
    runBashCommand('gcloud compute ssh --zone "us-east1-b" --ssh-flag="-ServerAliveInterval=30" '+ user +'@'+instance+' --command ' + str(sys.argv[1]))