#!/bin/bash
#

cat zabbix-iib-monitor-agent-data.json | jq 'if . == "IBM/IntegrationBus/IB10NODE/Status" then {"test":"started", "test2":"stopped"} else . end'
