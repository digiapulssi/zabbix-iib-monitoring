#!/bin/bash
#

cat zabbix-iib-monitor-agent-data.json | jq '[ 
   {"{#STATUS}": ."IBM/IntegrationBus/IB10NODE/Status/ExecutionGroup/server1".Broker.children[].ExecutionGroup.children[]|keys[0]}, 
   {"{#FLOWS}":."IBM/IntegrationBus/IB10NODE/Status/ExecutionGroup/server1".Broker.children[].ExecutionGroup.children[].Stop.AllMEssageFlows}
]'
