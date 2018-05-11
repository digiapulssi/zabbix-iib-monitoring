#!/bin/bash
#

cat zabbix-iib-monitor-agent-data.json | jq '."$1".WMQIStatisticsAccounting.MessageFlow.$2'
