#!/usr/bin/env bash
### every exit != 0 fails the script
set -e

echo "Install Openbox UI components"
apt-get update
apt-get install -y  supervisor openbox xterm dbus-x11 libdbus-glib-1-2
apt-get clean -y