#!/bin/bash
#

cat /tmp/zabbix-iib-monitor-agent-data.json | jq -S --arg TOPIC_TYPE '{ "data": [keys[] | foreach . as $item (.; 
if $TOPIC_TYPE == "node" then (if $item | test("IBM/IntegrationBus/.*/Status$") then {"{#TOPIC_NODE}":$item}) 
elif $TOPIC_TYPE == "server" then (if $item | test("^IBM/IntegrationBus/.*/Status/ExecutionGroup/.*$") then {"{#TOPIC_SERVER}":$item} end) 
elif $TOPIC_TYPE == "messageflow" then (if $item | test("^IBM/IntegrationBus/.*/Statistics/JSON/SnapShot/") then {"{#TOPIC_MESSAGEFLOW}":$item})
else ({"Error unknown topic":$item}) end)]}'


#$TOPIC_TYPE
#if $TOPIC_TYPE == "node" then . elif if $TOPIC_TYPE == "server" then . if $TOPIC_TYPE == "message" then . else
#
#
#if $item | test("IBM/IntegrationBus/.*/Status$") then {"{#TOPIC_NODE}":$item} elif $item | test("^IBM/IntegrationBus/.*/Statistics/JSON/SnapShot/") then {"{#TOPIC_MESSAGEFLOW}":$item} elif $item | test("^IBM/IntegrationBus/.*/Status/ExecutionGroup/.*$") then {"{#TOPIC_SERVER}":$item} else {"Error unknown topic":$item} end