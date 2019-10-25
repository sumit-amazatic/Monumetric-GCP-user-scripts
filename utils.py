import sys, socket, os, json, subprocess, getpass

def isPython3():
    if not sys.version_info >= (3,0):
        print("run script in python3")
        sys.exit()
        return False
    return True

isPython3()

def runHelp():
    print("\nrun: python3", sys.argv[0], "<app/instance name>\n")

def getUsername():
    return getpass.getuser()

def getUsernameOrUseDefault():
    user = input("enter GCP username or hit [ENTER] to use '"+ getpass.getuser() +"' : ", )
    return user if user else getpass.getuser() 

def runBashCommandGetOutput(command):
    return subprocess.check_output(command, shell=True).strip().decode()

def runBashCommand(command):
    command = command.strip()
    exit_code = os.system(command)
    if(exit_code != 0):
        print(command)
        print('EXITED...!!!!' + str(exit_code))
        sys.exit()

def getAppNameFromInput():
    k8s_clusters_list = runBashCommandGetOutput("gcloud container clusters list | grep RUNNING | awk '{print $1}'").split('\n')
    if len(sys.argv) is 2 and sys.argv[1] in k8s_clusters_list:
        return sys.argv[1]
    else:
        for cluster_name in k8s_clusters_list:
            print(cluster_name)
        return input("Enter cluster names from above list: ")

def getInstanceNameFromInput():
    k8s_clusters_list = runBashCommandGetOutput("gcloud compute instances list | grep 'master' | awk '{print $1}'").split('\n')
    if len(sys.argv) is 2 and sys.argv[1] in k8s_clusters_list:
        return sys.argv[1]
    else:
        for cluster_name in k8s_clusters_list:
            print(cluster_name)
        runHelp()
        return input("Enter cluster names from above list: ")



def getCurrentState(kubernetes_clusters_name):
    with open(kubernetes_clusters_name + "_CurrentStatus.json", 'r') as f:
        currentState = json.load(f)
        return currentState

def saveStatusDict(d, kubernetes_clusters_name):
    f = open(kubernetes_clusters_name + "_CurrentStatus.json","w")
    f.write(json.dumps(d))
    f.close()

def parseDep(shellOutput):
    output = shellOutput.split('\n')
    keyss = output[0].split()
    upToDateIndex = keyss.index('UP-TO-DATE')
    d = {}
    for deployment in output[1:]:
        dep = deployment.split()
        d[dep[0]] = dep[upToDateIndex]
    #d["status"] = "scaled-down"
    return d

def scaleDeployment(name, replicas):
    runBashCommand("kubectl scale --replicas="+ str(replicas) +" deployment/"+ name)
    print(name, "\tScaled to\t", replicas)

def scaleUpDeployments():
    isPython3()
    kubernetes_clusters_name = getAppNameFromInput()
    runBashCommand("gcloud container clusters get-credentials " + kubernetes_clusters_name + " --zone us-east1-b --project console-234301")
    state = getCurrentState(kubernetes_clusters_name)
    if not os.path.exists(kubernetes_clusters_name + "_CurrentStatus.json"):
        print("already scaled up")
        return True

    for name, replicas in state.items():
        scaleDeployment(name, replicas)
    os.remove(kubernetes_clusters_name + "_CurrentStatus.json")

def scaleDownDeployments():
    isPython3()
    kubernetes_clusters_name = getAppNameFromInput()
    runBashCommand("gcloud --quiet container clusters get-credentials " + kubernetes_clusters_name + " --zone us-east1-b --project console-234301")

    if os.path.exists(kubernetes_clusters_name + "_CurrentStatus.json"):
        print("already scaled down")
        return False

    output = parseDep(runBashCommandGetOutput("kubectl get deployment"))
    saveStatusDict(output, kubernetes_clusters_name)
    for name, replicas in output.items():
        scaleDeployment(name, 0)
    return True