#!/bin/bash
#

cat /tmp/zabbix-iib-monitor-agent-data.json | jq --arg TOPIC "$1" --arg DATA "$2" ' if [$DATA] != null OR [$DATA] != "" then .[$TOPIC].WMQIStatisticsAccounting.MessageFlow[$DATA] else .[$TOPIC].WMQIStatisticsAccounting.MessageFlow end'
