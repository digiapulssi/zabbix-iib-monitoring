#!/bin/bash
#

cat /tmp/zabbix-iib-monitor.json | jq -S --arg TOPIC "$1" '.[$TOPIC].Broker.children[].StatusChange.attributes.new'
