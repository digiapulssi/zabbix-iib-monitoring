#!/bin/bash
#

cat zabbix-iib-monitor-agent-data.json | jq '[. | {node: ."IBM/IntegrationBus/IB10NODE/Status".Broker.attributes.label , change: ."IBM/IntegrationBus/IB10NODE/Status".Broker.children[0].StatusChange.attributes.new}, {EndDate: ."IBM/IntegrationBus/IB10NODE/Statistics/JSON/SnapShot/server1/applications/IoTonCloud/messageflows/TemperatureSensor".WMQIStatisticsAccounting.MessageFlow.EndDate , name: .commit.committer.name},{keys: keys}]'
