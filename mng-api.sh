#!/bin/bash

PROJECT_NAME='crawler'
COMPOSE_FILE='docker-compose.yml'
NGINX_FILE='crawler_api_nginx.conf'

API_CONTAINER_NAME=${PROJECT_NAME}'_api'
DB_CONTAINER_NAME=${PROJECT_NAME}'_db'
CELERY_CONTAINER_NAME=${PROJECT_NAME}'_celery'
CELERY_BEAT_CONTAINER_NAME=${PROJECT_NAME}'_beat'


function log() {
    docker logs -f ${API_CONTAINER_NAME}
}

function make_migrations() {
    docker exec -it ${API_CONTAINER_NAME} python ./manage.py makemigrations
}

function migrate() {
    echo -e "\n ... migrate db ... \n"
    docker exec -t $1 python ./manage.py migrate
}

function bash() {
    docker exec -it ${API_CONTAINER_NAME} bash
}

function shell() {
    docker exec -it ${API_CONTAINER_NAME} python ./manage.py shell
}

function drop_db() {
    docker exec -it ${DB_CONTAINER_NAME} psql -U postgres -c "drop schema public cascade;"
    docker exec -it ${DB_CONTAINER_NAME} psql -U postgres -c "create schema public;"
}

function populate_db() {
    cat $1 | docker exec -i ${DB_CONTAINER_NAME} psql -U postgres
}

function collectstatic() {
    echo -e "\n ... collect static files ... \n"
    docker exec -i $1 ./manage.py collectstatic --noinput
}

function create_admin_user() {
    docker exec -it ${API_CONTAINER_NAME} ./manage.py shell -c "from django.contrib.auth.models import User; User.objects.create_superuser('${1:-admin}', '', '${2:-test1234}')"
}

function issue_https_certificate() {
    sudo certbot --nginx certonly -d crawler.m-gh.com -d www.crawler.m-gh.com --nginx-server-root /etc/nginx/my_conf/
    sudo ln -s ${SERVER_PATH}${NGINX_FILE} /etc/nginx/sites-enabled/${NGINX_FILE}
    sudo service nginx restart
}

function dump_db() {
    echo -e "\n ... dump db ... \n"
    mkdir -p db_backup
    docker exec -t ${DB_CONTAINER_NAME} pg_dumpall -c -U postgres | gzip > ./db_backup/${PROJECT_NAME}_db_`date +\%d-\%m-\%Y"_"\%H_\%M_\%S`.sql.gz
}

function pull() {
    echo -e "\n ... pull images ... \n"
    docker-compose -f ${COMPOSE_FILE} pull ${API_CONTAINER_NAME} ${WS_CONTAINER_NAME} ${CELERY_CONTAINER_NAME} ${CELERY_BEAT_CONTAINER_NAME}
}

function up() {
    echo -e "\n ... up containers ... \n"
    docker-compose -f ${COMPOSE_FILE} up -d --build
}

function remove_unused_image() {
    echo -e "\n ... remove unused images ... \n"
    docker image prune -af
}

function scp_conf() {
    echo -e "\n ... copy conf files to server ... \n"
    scp ${COMPOSE_FILE} ${NGINX_FILE} mng-api.sh .docpasswd doc.json ${SERVER_NAME}:${SERVER_PATH}
}

case $1 in
scp_conf)
    scp_conf
;;
up)
    pull
    up
    migrate ${API_CONTAINER_NAME}
    collectstatic ${API_CONTAINER_NAME}
    remove_unused_image
;;
log)
    log
;;
makemigrations)
    make_migrations
;;
migrate)
    migrate ${API_CONTAINER_NAME}
;;
bash)
    bash
;;
shell)
    shell
;;
drop_db)
    drop_db
;;
populate_db)
    populate_db $2
;;
admin_user)
    create_admin_user $2 $3
;;
https)
    issue_https_certificate
;;
dump_db)
    dump_db
;;
down)
    docker-compose down
;;
*)
    echo "don't know what to do"
;;
esac
