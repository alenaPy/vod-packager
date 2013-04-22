#!/bin/sh

BACKUP_PATH="/home/Backup/mysql"
MYSQL_USER="root"
MYSQL_PASS="ard010fx"

mysqldump -u$MYSQL_USER -p$MYSQL_PASS --opt packager > $BACKUP_PATH/packager.sql

cd $BACKUP_PATH
tar -zcvf Packager_Backup_$(date +%d%m%y).tgz *.sql
rm  *.sql