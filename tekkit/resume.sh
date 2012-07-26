#!/bin/sh

#If the screen command was used to start bukkit and the server has not been stopped then this will resume the process.
#not sure what happens if two people connect simultaniously though...
screen -dr  minecraft_tekkit_screen
