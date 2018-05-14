#!/bin/bash
#

cat /tmp/zabbix-iib-monitor-agent-data.json | jq '{ "data": [keys[] | foreach . as $item (.; if $item | test("IBM/IntegrationBus/.*/Status$") then {"{#TOPIC_NODE}":$item} elif $item | test("^IBM/IntegrationBus/.*/Statistics/JSON/SnapShot/") then {"{#TOPIC_MESSAGEFLOW}":$item} elif $item | test("^IBM/IntegrationBus/.*/Status/ExecutionGroup/.*$") then {"{#TOPIC_SERVER}":$item} else {"Error unknown topic":"$item"} end)]}'