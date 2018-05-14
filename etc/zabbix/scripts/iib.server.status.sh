#!/bin/bash
#

cat zabbix-iib-monitor-agent-data.json | jq --arg TOPIC "$1" '.[$TOPIC].Broker.children[].ExecutionGroup.children[] | keys[0]'
