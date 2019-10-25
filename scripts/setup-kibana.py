import random, string, sys, socket, os, json, re
from subprocess import STDOUT, check_call, check_output


try:
    xrange
except NameError:
    xrange = range

def get_ip():
    from requests import get; return get('https://api.ipify.org').text

def write_in_file(path, content):
  try:
    f = open(path, "w+"); f.write(content); f.close()
  except IOError as e:
    print("exited because:- ", e)
    sys.exit()

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
        os.system('echo [error] '+ str(exit_code))
        os.system('/bin/printerbanner exited')
        sys.exit()


def install_prerequisites():
    print("Installing JDK 8")
    run = ["sudo add-apt-repository ppa:webupd8team/java -y", "sudo apt update -qqy", "sudo apt install openjdk-8-jre-headless -qqy", "sudo apt install default-jdk -qqy", "java -version"]
    for command in run:
        runBashCommand(command)
    print("Installing nginx")
    run = ["sudo apt install nginx -qqy"]
    for command in run:
        runBashCommand(command)

def install_elasticsearch():
    print("Installing elasticsearch")
    run = ["wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add -", '''echo "deb https://artifacts.elastic.co/packages/6.x/apt stable main" | sudo tee -a /etc/apt/sources.list.d/elastic-6.x.list''', "sudo apt update -qqy", "sudo apt install elasticsearch -qqy"]

    for command in run:
        runBashCommand(command)

    findAndReplace('/etc/elasticsearch/elasticsearch.yml', '#network.host: 192.168.0.1', 'network.host: 0.0.0.0')
    
    for command in ["sudo systemctl start elasticsearch", "sudo systemctl enable elasticsearch"]:
        runBashCommand(command)
    
def install_kibana():
    run = ["sudo apt install kibana -qqy", "sudo systemctl enable kibana", "sudo systemctl start kibana", '''echo "fkphzqjpiyzo:`openssl passwd -apr1 12et05jk5zfeya46xu1kccmqdshxmvxfbt7o5t3tibbsn6zm0ej6`" | sudo tee -a /etc/nginx/htpasswd.users''']

    for command in run:
        runBashCommand(command)

def config_nginx():
    ip = get_ip()
    nginx = '''server {
        listen 80;
    
        server_name '''+ ip +''';
    
        auth_basic "Restricted Access";
        auth_basic_user_file /etc/nginx/htpasswd.users;
    
        location / {
            proxy_pass http://localhost:5601;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host $host;
            proxy_cache_bypass $http_upgrade;
        }
    }
    '''
    write_in_file("/etc/nginx/sites-available/" + ip, nginx)

    for command in ['sudo ln -sfn /etc/nginx/sites-available/' + ip + ' /etc/nginx/sites-enabled/' + ip , 'sudo nginx -t', 'sudo systemctl restart nginx', 'sudo ufw allow "Nginx Full"']:
      runBashCommand(command)


def setup_logstash():
    for command in ['sudo apt install logstash -qqy', 'sudo -u logstash /usr/share/logstash/bin/logstash --path.settings /etc/logstash -t', 'sudo systemctl start logstash', "sudo systemctl enable logstash"]:
      #'cp 02-beats-input.conf /etc/logstash/conf.d/', 'cp 10-syslog-filter.conf /etc/logstash/conf.d/', 'cp 30-elasticsearch-output.conf /etc/logstash/conf.d/',
      runBashCommand(command)

functions_to_run = [install_prerequisites, install_elasticsearch, install_kibana, config_nginx, setup_logstash]
for func in functions_to_run:
    func()
