#!/bin/bash

lib=$1
container=$2
result="$lib"
cd /home/appuser/script/
echo "from $lib import Userlib"|cat - grader.py|python3 > `echo "$result.output"` 2>&1 
echo "Generated $result.output from container $container" >> `echo "$result.output"`
