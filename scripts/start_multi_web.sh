#!/bin/bash

printenv

source /Users/javierin/.pyenv/versions/3.7.7/envs/trastobrain/bin/activate

export FLASK_APP=trasto/application/web_multi.py

python -m flask run --host=0.0.0.0 --port 8080 &