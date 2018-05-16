#!/bin/bash
#

cat /tmp/zabbix-iib-monitor-agent-data.json | jq -S --arg TOPIC_TYPE "$1" '{ "data": [keys[] | foreach . as $item (.;  
if $TOPIC_TYPE == "node" then (if $item | test("IBM/IntegrationBus/.*/Status$") then {"{#TOPIC_NODE}":$item} else empty end)  
elif $TOPIC_TYPE== "server" then (if $item | test("^IBM/IntegrationBus/.*/Status/ExecutionGroup/.*$") then {"{#TOPIC_SERVER}":$item} else empty end)  
elif $TOPIC_TYPE== "messageflow" then (if $item | test("^IBM/IntegrationBus/.*/Statistics/JSON/Archive/") then {"{#TOPIC_MESSAGEFLOW}":$item} else empty end) 
else ({"Error unknown topic":$item}) end)]}'
