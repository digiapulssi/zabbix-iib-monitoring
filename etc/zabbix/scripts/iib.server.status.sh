#!/bin/bash
#

cat zabbix-iib-monitor-agent-data.json | jq '."$1".Broker.children[].ExecutionGroup.children[] | keys[0]'
