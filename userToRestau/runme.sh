#!/bin/bash

killId=$(ps x | grep main | awk '{print $1;}')

kill -9 $killId

for pid in $(ps -ef | grep "geckodriver" | awk '{print $2}'); do kill -9 $pid; done
for pid in $(ps -ef | grep "firefox" | awk '{print $2}'); do kill -9 $pid; done

export PATH=$(pwd):$PATH

python3 main.py&
