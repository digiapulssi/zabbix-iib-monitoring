#!/bin/bash
#

cat zabbix-iib-monitor-agent-data.json | jq '
{
   "{NODE}":."IBM/IntegrationBus/IB10NODE/Statistics/JSON/SnapShot/server1/applications/IoTonCloud/messageflows/TemperatureSensor".WMQIStatisticsAccounting.MessageFlow.BrokerLabel, 
   "{SERVER}":."IBM/IntegrationBus/IB10NODE/Statistics/JSON/SnapShot/server1/applications/IoTonCloud/messageflows/TemperatureSensor".WMQIStatisticsAccounting.MessageFlow.ExecutionGroupName, 
   "{APP}":."IBM/IntegrationBus/IB10NODE/Statistics/JSON/SnapShot/server1/applications/IoTonCloud/messageflows/TemperatureSensor".WMQIStatisticsAccounting.MessageFlow.ApplicationName, 
   "{MSGFLOW}":.  "IBM/IntegrationBus/IB10NODE/Statistics/JSON/SnapShot/server1/applications/IoTonCloud/messageflows/TemperatureSensor".WMQIStatisticsAccounting.MessageFlow.MessageFlowName
}
'
