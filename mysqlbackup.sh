#!/bin/sh

BACKUP_PATH="/home/Backup/mysql/"
SYNC_PATH="/home/Backup/mysql/to_sync/"
MYSQL_USER="root"
MYSQL_PASS="ard010fx"

mysqldump -u$MYSQL_USER -p$MYSQL_PASS --opt packager --ignore-table=packager.Packager_app_package > $BACKUP_PATH/packager_$(date +%s).sql

cd $BACKUP_PATH
tar -zcvf Packager_Backup_$(date +%d%m%y).tgz *.sql
mv  *.sql $SYNC_PATH
