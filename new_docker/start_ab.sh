#!/bin/bash
eval "$(micromamba shell hook --shell bash)"
micromamba activate base
echo "--- Starting Activity Browser ---"
nohup activity-browser &
exec "$@"