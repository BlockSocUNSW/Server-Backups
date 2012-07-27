#!/bin/bash
# updates the website. 
git clone git://github.com/bwright/Blocksoc.git /var/www/nginx-default/update
cp -r /var/www/nginx-default/update/* /var/www/nginx-default/
rm -rf /var/www/nginx-default/update
