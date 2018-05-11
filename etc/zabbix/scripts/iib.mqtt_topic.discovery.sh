#!/bin/bash
#

cat zabbix-iib-monitor-agent-data.json | jq '{"data":[foreach keys as $item ({"{#TOPIC}":"$item"}; {"{#TOPIC}":$item[]})]}'
