#!/bin/bash
#

cat /tmp/zabbix-iib-monitor-agent-data.json | jq -S --arg TOPIC "$1" --arg DATA "$2" 'if ($DATA != null) and ($DATA != "") then .[$TOPIC].WMQIStatisticsAccounting.MessageFlow[$DATA] else .[$TOPIC].WMQIStatisticsAccounting.MessageFlow end'
