#!/bin/bash

for OUTPUT in $(ps -fe | grep "trasto/application" | awk '{print $2}')
do
	echo Matamos $OUTPUT
	kill -9 $OUTPUT
done

kill -9 $(ps -fe | grep "python -m flask run" | awk '{print $2}')

