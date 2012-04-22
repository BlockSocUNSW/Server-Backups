#!/bin/bash
#pushes exerything here to the git repo
#git@github.com:BlockSocUNSW/Server-Backups.git

server_dir="/home/minecraft/server"


current_dir=`pwd`
name=`date`

cd ${server_dir} >> backup_log 2>&1
echo >> backup_log 2>&1
echo "Backup: ${name}" >> backup_log 2>&1

echo "Origin directory: ${current_dir}" >> backup_log 2>&1
echo "Moved to: ${server_dir}" >> backup_log 2>&1

echo "Adding all updates." >> backup_log 2>&1
git add --all >> backup_log 2>&1

echo "Commiting under name: ${name}" >> backup_log 2>&1
git commit  -m "${name}" >> backup_log 2>&1

echo "Pushing to github" >> backup_log 2>&1
git remote add origin git@github.com:BlockSocUNSW/Server-Backups.git >> backup_log 2>&1
git push -u origin master >> backup_log 2>&1

echo "Returning to original directory." >> backup_log 2>&1

cd ${current_dir} 

