#!/bin/bash
# Creater a dated backup, generates a md5 hash and pushes it.
BACKUP_NAME="backup-`date +%F`.tar.bz2"
tar -cjf "$BACKUP_NAME" --files-from backup_list
md5sum "$BACKUP_NAME" > $BACKUP_NAME.md5
