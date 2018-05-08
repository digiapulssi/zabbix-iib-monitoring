#!/bin/bash
#

cat zabbix-iib-monitor-agent-data.json | jq '{"{#TOPIC}": keys[]}'
