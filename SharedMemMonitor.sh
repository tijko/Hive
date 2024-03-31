#!/usr/bin/env bash

firefox_pid=""
rss_total=0
verbose=false

if [[ $# -gt 0 ]]
then
    echo "Verbosity Set"
    verbose="true"
fi

for ((;;))
do
    for pid in $(pidof firefox | tr ' ' '\n' | sort -n)
    do
        # linux/Documentation/filesystems/proc.rst (Status VmRSS)
        # Contains - (RssAnon + RssShmem + RssFile)    
        #
        # This 1st PID will be the PPID of the rest that follow.
        if [[ $firefox_pid -eq "" ]]
        then
            firefox_pid=$pid
            if [[ "${verbose}" == true ]]
            then
                echo Found Firefox PID $firefox_pid
            fi
        else
            if [[ "${verbose}" == true ]]
            then
                echo Found Firefox Child $pid
            fi
            cd /proc/$pid/
            ppid=$(ps -o ppid= -p $pid)
            if [[ $ppid -eq $firefox_pid ]]
            then
                rss=$(cat status | awk -F':' '{if ($1 == "VmRSS") print $2}' | tr -d 'kB')
                rss_total=$(($rss + $rss_total))
            fi
        fi
    done

    echo Total Memory ${rss_total}kB
done