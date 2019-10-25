import sys, socket, os, json, subprocess
from utils import scaleDownDeployments, scaleUpDeployments


# Todo
# backup and resore db server to server

run_ls = [scaleDownDeployments, scaleUpDeployments]
for fun in run_ls:
    fun()





































# function indent() {
#     sed 's/^/    /';
# }

# function set_maintenance() {
#     # app_name mode
#     heroku maintenance:$2 --app $1
# }

# function scale_down() {
#     # app_name
#     heroku ps --app $1 | grep === | while read line ; do
#         name=$( echo "$line" |cut -d ' ' -f2 )
#         heroku ps:scale $name=0 --app $1
#     done
# }

# function backup_db {
#     echo "    CREATING BACKUP OF $1/$2"
#     heroku pg:backups capture $2 --app $1 # capture backup # not required if we want to use the latest backup
# }

# function restore_db {
#     # from_app, from_db, to_app, to_db, optional backup_id
#     if [ $5 ]
#     then
#         backup_id=$5
#     else
#         backup_id=`heroku pg:backups --app $1 | grep $2 | head -n1 | cut -d " " -f 1`
#     fi
#     echo "    RESTORING BACKUP ID $backup_id ($1/$2) to $3/$4"
#     heroku pg:backups restore `heroku pg:backups public-url $backup_id --app $1` $4 --app $3 --confirm $3  # restore backup
# }

# function scale_web_dyno_to_one() {
#     # app_name
#     heroku ps:scale web=1 --app $1
# }

# echo -e "\n*** ENABLING MAINTENANCE MODE  ***"
# set_maintenance mmt-console-4-staging on
# set_maintenance aggregator-tbn-staging on
# set_maintenance services-tbn-staging on

# echo -e "\n*** TURN OFF DYNOS  ***"
# scale_down services-tbn-staging
# scale_down aggregator-tbn-staging
# scale_down mmt-console-4-staging

# echo -e "\n*** EMPTYING DB ***"
# heroku pg:reset DATABASE --app services-tbn-staging --confirm services-tbn-staging
# heroku pg:reset DATABASE --app aggregator-tbn-staging --confirm aggregator-tbn-staging
# heroku pg:reset HEROKU_POSTGRESQL_YELLOW --app aggregator-tbn-staging --confirm aggregator-tbn-staging

# echo -e "\n*** CREATING BACKUP ***"
# backup_db services-tbn-production DATABASE | indent # tier db
# backup_db aggregator-tbn-production IVORY | indent # stats db
# backup_db aggregator-tbn-production WHITE | indent # aggregator db

# echo -e "\n*** RESTORING DB ***"
# restore_db services-tbn-production DATABASE services-tbn-staging DATABASE | indent # tier db
# restore_db aggregator-tbn-production IVORY aggregator-tbn-staging DATABASE | indent # stats db
# restore_db aggregator-tbn-production WHITE aggregator-tbn-staging YELLOW | indent # aggregator db

# echo -e "\n*** TURN ON WEB DYNOS  ***"
# scale_web_dyno_to_one mmt-console-4-staging
# scale_web_dyno_to_one aggregator-tbn-staging
# scale_web_dyno_to_one services-tbn-staging

# echo -e "\n*** DISABLING MAINTENANCE MODE  ***"
# set_maintenance services-tbn-staging off
# set_maintenance aggregator-tbn-staging off
# set_maintenance mmt-console-4-staging off