#!/usr/bin/env bash
### every exit != 0 fails the script
set -e

echo -e "\n------------------ startup of Activity Browser ------------------"

### disable screensaver and power management
xset -dpms &
xset s noblank &
xset s off &

exec $HOME/start_activity_browser.sh > $HOME/wm.log &
sleep 1
cat $HOME/wm.log