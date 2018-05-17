# zabbix-iib-monitoring

This project contains scripts for listening to IBM Integration Bus MQTT messages and ready-to-install scripts for Zabbix Agent.

## Installation

1. Copy the files under [etc/zabbix/scripts](etc/zabbix/scripts) to `/etc/zabbix/scripts`
2. Copy the files under [etc/zabbix/zabbix_agentd.d](etc/zabbix/zabbix_agentd.d) to `/etc/zabbix/zabbix_agentd.d`
3. Copy "zabbix-iib-monitoring.py" and "zabbix-iib-monitoring.ini" anywhere on the agent machine (does **not** require to be local with IBM Integration Bus)

## Usage

### IBM Integration Bus

1. Activate messageflow data collection for integration node in IBM Integration Console with command:
```
mqsichangeflowstats yourNodeName -g -j -a -o json -c active
```
("-g" = all integration servers, "-j" = all message flows, "-a" = archive publishing, "-o json" = output format "json", -"c active" = control enable data collection, use command ```mqsichangeflowstats``` to see all options)

**NOTE: Messageflow data collection is off by default and must be reactivated after (re)deployment!**


2. Change data collection interval for integration node with command:

**NOTE: Integration node needs to be shutdown first**
```
mqsichangebroker yourNodeName -v 1
```
("-v" = data collection interval, in minutes, min 1 max 43200)

### Scripts & Zabbix

3. Run "zabbix-iib-monitoring.py" (check "zabbix-iib-monitoring.ini" for connection settings) to start recieving monitoring data

4. Add 3 iib.mqtt_topic.discovery to host/template
   - Use key "iib.mqtt_topic.discovery[]" with parameter "node", "server" or "messageflow" (one of each)
   - Set filter ```"{#TOPIC_NODE}" matches "^IBM/IntegrationBus/[A-Za-z0-9]*/Status$"``` for "iib.mqtt_topic.discovery[node]"
   - Set filter ```"{#TOPIC_SERVER}" matches "^IBM/IntegrationBus/[A-Za-z0-9]*/Status/ExecutionGroup/[A-Za-z0-9]*$"``` for "iib.mqtt_topic.discovery[server]"
   - Set filter ```"{#TOPIC_MESSAGEFLOW}" matches "^IBM/IntegrationBus/[A-Za-z0-9]*/Statistics/JSON/Archive"``` for "iib.mqtt_topic.discovery[messageflow]"
5. Add items to host/template
   - Use key "iib.messageflow[{TOPIC_MESSAGEFLOW}, dataName]" where "datanName" is the monitoring data field name (leave empty to see all fields)
   - Use key "iib.node.status[{TOPIC_NODE}] to get updates on node status
   - Use key "iib.server.status[{TOPIC_SERVER}]" to get updates on server status

