#!/bin/bash

LOG_DIR=~/workspace/random-playlist-generator/src/.log
SCRIPT=~/workspace/random-playlist-generator/src/playlist_generator.py
FS_TIMESTAMP="FS_TIMESTAMP:"
SLEEP=259200


ENTRY=$(grep $FS_TIMESTAMP src/.log | tail -1)
LEXEC=${ENTRY#*$FS_TIMESTAMP}
LEXEC=$(date -d "$LEXEC" +%s)


TSTAMP=$(date +%s)
DELTA=$((TSTAMP-LEXEC))

if [ $DELTA -lt $SLEEP ]
then
    exit
fi

python3 $SCRIPT

# make sure that the new entry is matches the last missed execution (so the switch interval stays static)
MISSED_EXECS=-1
while [ $TSTAMP -gt $LEXEC ]
do 
    ((MISSED_EXECS++))
    TSTAMP=$((TSTAMP-SLEEP))
    #LEXEC=$((LEXEC+SLEEP))
done

LEXEC=$((LEXEC+SLEEP*MISSED_EXECS))

echo "INFO:cron:FS_TIMESTAMP:$(date -d @$LEXEC '+%Y-%m-%d %H:%M:%S')" >> src/.log
