#!/bin/bash

printenv

# Check Environment variables
#if [ -z "$CONNECT_BOOTSTRAP_SERVERS" ]; then
#    echo "Environment variable CONNECT_BOOTSTRAP_SERVERS not found"
#   exit 1
#fi



#export VERSION=0.60.1


# Launch filetrans server
python trastobrain/trasto/application/web.py

