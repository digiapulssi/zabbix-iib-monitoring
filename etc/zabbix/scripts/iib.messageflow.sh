#!/bin/bash
#

cat /tmp/zabbix-iib-monitor-agent-data.json | jq --arg TOPIC "$1" --arg DATA "$2" '.[$TOPIC].WMQIStatisticsAccounting.MessageFlow.[$DATA]'
