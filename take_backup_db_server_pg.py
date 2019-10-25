import sys, socket, os, json, subprocess
from utils import runBashCommandGetOutput, runHelp, isPython3, getInstanceNameFromInput, runBashCommand, getUsername

def runBashCmdOnGCP(instance_name, command):
    server = 'root@'+instance_name
    cmd = 'gcloud compute ssh --zone "us-east1-b" --ssh-flag="-ServerAliveInterval=30" ' +server+ ' --command ' + command
    runBashCommand(cmd)

instance_name = getInstanceNameFromInput()
take_backup_cmd = '''\'sh -c "$(curl --user amazatic:1ru7f16lpevtobyzavml7aple416o7lxjhm4jn8blo0h4i27fetkpeeck6qedp8p -sSL 10.142.0.112/backup.sh)"\''''
runBashCmdOnGCP(instance_name, take_backup_cmd)
