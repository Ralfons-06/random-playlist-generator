#!/bin/bash

LOG_DIR=~/workspace/random-playlist-generator/src/.log
SCRIPT=~/workspace/random-playlist-generator/src/playlist_generator.py
SLEEP=345600


ENTRY=$(grep FS_TIMESTAMP src/.log | tail -1)
IFS=':' read -r -a entry <<< "$ENTRY"
LEXEC=${entry[3]}

TSTAMP=$(date +%s)
DELTA=$((TSTAMP-LEXEC))

if [ $DELTA -lt $SLEEP ]
then
    exit
fi

python3 $SCRIPT

# make sure that the new entry is matches the last missed execution (so the switch interval stays static)
while [ $LEXEC -lt $TSTAMP ]
do 
    LEXEC=$((LEXEC+SLEEP))
done

echo "INFO:cron:FS_TIMESTAMP:$LEXEC" >> .log


