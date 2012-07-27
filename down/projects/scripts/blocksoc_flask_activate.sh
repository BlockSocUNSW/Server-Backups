#!/bin/bash

cd /var/www/nginx-default
. env/bin/activate
cd env/blocksoc/
gunicorn -w 4 -b 127.0.0.1:4001  blocksoc:app
