#!/bin/bash
#

cat /tmp/zabbix-iib-monitor-agent-data.json | jq -S --arg TOPIC "$1" '.[$TOPIC].Broker.children[].ExecutionGroup.children[] | keys[0]'
