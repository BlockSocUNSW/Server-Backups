#!/usr/bin/python2.6
#A script that maintains backups of the server if called regularly (say every 6 hours as a cron job). Calls a git update for short term updates and creates tar archives weekly. These archives are maintained for up to 4 weeks before deletion. And archive older than 4 weeks will be deleted. Archives set in the 'future' will be ignored

import os
import time
import re
import logging

#This is the screen alias (from: screen -S [alias] [server init script]) that the server runs under. Will be used to send commands to the server. 
SERVER_SCREEN_NAME = "minecraft_server_screen"

#The path that is to be backed up instide tar files.
BACKUP_TARGET_DIR = "/home/minecraft/server/"
#If there are any files/directories that you want to exclude from the tar in this path, add them here.
BACKUP_TARGET_EXCLUDE = [".git", "MCProxy"]

#Path to a script that updates the git repo for the server. 
GIT_UPDATE_SCRIPT = "~/server/git_backup.sh"

#The directory were tar backups are placed
BACKUP_DIR = "/home/minecraft/backup/"

#If the earliest backup is older than this then a new back up will be created (in seconds)
MIN_BACKUP_AGE = 604800 - 3600      #number of seconds in a week - hour of overhead

#Any backup older than this will be deleted.
MAX_BACKUP_AGE = 604800 * 4 + 3600  #number of seconds in 4 weeks + hour of over head 

#regex form for tar files. Anything not matching exactly will be ignored.
#Everything except the epoch time is just for human readability.
#[day][-][month][-][year][-][hour][-][minute][-][second]:[seconds since epoch (gmtime)][\.tar]
tar_form = re.compile('\d\d-\d\d-\d\d\d\d-\d\d-\d\d-\d\d:\d+.tar')

#Set up the log
LOG_FORMAT = '%(asctime)-15s\t%(levelname)s\t%(message)s'
LOG_NAME = "server_backup.log"

logger = logging.getLogger('Server Backup')
handle = logging.FileHandler(LOG_NAME)
formatter = logging.Formatter(LOG_FORMAT)
handle.setFormatter(formatter)
logger.addHandler(handle) 
logger.setLevel(logging.INFO)


#sends a console message to the server.
def sendServerCommand(screen, command):
    logger.info("    Sending server command: " + command)
    send = "screen -S " + SERVER_SCREEN_NAME + " -X stuff \"" + command + "\n\""
    status = os.system(send)
    logger.info("    Exit Status: " + str(status))
    if status != 0:
        logger.critical("    Failed to send command")
    return

#creates a tar backup with the current timestamp in the backup directory.
def createBackup():
    #make the name from the time stamp
    t = time.gmtime()
    name =              ('%02d' % t.tm_mday ) #day
    name = name + "-" + ('%02d' % t.tm_mon )
    name = name + "-" + ('%04d' % t.tm_year )
    name = name + "-" + ('%02d' % t.tm_hour )
    name = name + "-" + ('%02d' % t.tm_min )
    name = name + "-" + ('%02d' % t.tm_sec )
    name = name + ":" + str(int(time.time())) + ".tar"
    #add the full path
    name = os.path.join(BACKUP_DIR, name)
    #get the target path
    os.chdir(BACKUP_TARGET_DIR)
    target = "*"
    #and any excludes
    exclude = "--exclude "
    for i in BACKUP_TARGET_EXCLUDE:
        exclude = exclude + i + " "
    #compile and execute command
    command = "tar -cf " + name + " " + target + " " + exclude
    logger.info("    Creating backup with command: " + command)
    status = os.system(command)
    logger.info("    Exit Status: " + str(status))
    if status != 0:
        logger.critical("    Failed to create backup. Attempting to contact server.")
        sendServerCommand(SERVER_SCREEN_NAME , "say WARNING: Server backup failed. Contact admin.")
    return

#removes a file/directory.
def removeBackup(path):
    logger.info("    Removing path: " + path)
    status = os.system("rm -r " + path)
    logger.info("    Exit Status: " + str(status))
    if status != 0:
        logger.critical("    Failed to send command")
    return

if __name__=='__main__':
    logger.info("Starting backup process.")
    #send alert that back up process started and stop saves.
    sendServerCommand (SERVER_SCREEN_NAME,"\nsay Starting backup.")
    sendServerCommand (SERVER_SCREEN_NAME,"\nsave-all")
    time.sleep(3)
    sendServerCommand (SERVER_SCREEN_NAME,"\nsave-off")
    time.sleep(3)
    try:
        #push to git
        logger.info("Calling git update script.")
        os.system(GIT_UPDATE_SCRIPT)

        #get the backups
        os.chdir(BACKUP_DIR)
        backups = []
        for f in os.listdir("."):
            if len(tar_form.findall(f)) == 1:
                #get the epoch time and save it and the file name
                t = int(f[0:len(f)-4].split(":")[1])
                if t > time.time():
                    logging.info("Found tar that is set in the future. Ignoring it.")
                    logging.info("    :" + f)
                else:
                    backups.append([t,f])
                
        #sort the backups by epoch.
        backups.sort()
        logger.info("Current Backups: ")
        for b in backups:
           logger.info("    " + b[1]) 
           
        logger.info("Preforming tar check.")

        # if there are no backups, make one.
        if len(backups) == 0:
            logging.info("No backups. Creating one.")
            createBackup()
        else:
            #otherwise, if the newest backup is outside of the minimum bound, make a new backup
            if time.time() - backups[len(backups)-1][0] > MIN_BACKUP_AGE:
                logging.info("New backup required.")
                createBackup()
            #prune off any backups that are older than the max bound.
            while len(backups) != 0 and  time.time() - backups[0][0] > MAX_BACKUP_AGE:
                logging.info("Removing old backup: " + backups[0][1])
                path = os.path.join(BACKUP_DIR, backups[0][1])
                removeBackup(path)
                del backups[0]
                
        logger.info("Tar check done.")
        
        #send alert that backup complete and enable saves.
        sendServerCommand (SERVER_SCREEN_NAME,"\nsave-on")
        sendServerCommand (SERVER_SCREEN_NAME,"\nsave-all")
        sendServerCommand (SERVER_SCREEN_NAME,"\nsay Backup complete.")
        logger.info("Backup done.")
    except :
        sendServerCommand (SERVER_SCREEN_NAME,"\nsave-on")
        sendServerCommand (SERVER_SCREEN_NAME,"\nsave-all")
        sendServerCommand (SERVER_SCREEN_NAME,"\nsay Backup complete.")
        logger.critical("An exception occured. Backup aborted.")
        sendServerCommand (SERVER_SCREEN_NAME,"WARNING: Exception occurred in backup. Contact admin immediately.")
