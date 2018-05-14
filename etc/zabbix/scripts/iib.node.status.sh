#!/bin/bash
#

cat /tmp/zabbix-iib-monitor-agent-data.json | jq --arg TOPIC "$1" '.[$TOPIC].Broker.children[].StatusChange.attributes.new'
