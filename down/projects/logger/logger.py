#!/usr/bin/env python

import os
import config
import time

class Logger:
  def __init__(self, file_path):
    '''
    Opens the new file_path.
    '''
    self.file_path = file_path
    self.fin = open(file_path, 'rU')
    self.last_modified = os.stat(file_path).st_mtime
  
  def has_changed():
    '''
    Returns true if the file has changed. Else false
    '''
    modified_time = os.stat(self.file_path).st_mtime
    if modified_time != self.last_modified:
      self.last_modified = modified_time
      return True
    return False
    
  def daemon(self):
    '''
    Continually checks the logs and then builds an internal sturcture from
    that.
    '''
    while True:
      where = self.fin.tell()
      line = self.fin.readline()
      if not line:
        time.sleep(1)
        self.fin.seek(where)
        for hook in config.HOOKS:
            hook(line)
      
if __name__ == '__main__':
  log = Logger('/home/minecraft/test/server.log')
  log.daemon()
