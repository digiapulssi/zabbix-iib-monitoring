# zabbix-iib-monitoring

This project contains scripts for listening to IBM Integration Bus MQTT messages and ready-to-install scripts for Zabbix Agent. 

These scripts do **not require** to be installed locally with IBM Integration Bus, although you will need to change the bind address of each integration node you want to monitor from the outside. Bind address can be found in a file at C:\ProgramData\IBM\MQSI\components\nodeName\config\nodeName

## Installation (Ubuntu/Debian)

### Switch to root user

```sudo su```

### Download latest release from https://github.com/digiapulssi/zabbix-iib-monitoring/releases

```curl -LJO <URL to latest release>```

### Install the downloaded package 

```apt install ./<downloaded-package>.deb```

### Reload services

```systemctl daemon-reload```

## Use

### In IBM Integration Console, adjust data collection interval for each integration node (that you want to monitor) with command:

**NOTE: Integration node needs to be shutdown first**

```mqsichangebroker yourNodeName -v 10```

("-v" = data collection interval, in minutes, min 1 max 43200 default 60)

### In IBM Integration Console, activate messageflow data collection.

To activate data collection for all servers and messageflows in a specific node, use command:

```mqsichangeflowstats yourNodeName -g -j -a -o json -c active```

("-g" = all integration servers, "-j" = all message flows, "-a" = archive publishing, "-o json" = output format "json", "-c active" = control: enable data collection)

If you wish to activate data collection only for a specific message flow, use the following command:

```mqsichangeflowstats yourNodeName -e serverName -k applicationName (-y staticLibraryName) -f messageflowName -a -o json -c active```

Use command ```mqsichangeflowstats -h``` to see all options.

**NOTE: Messageflow data collection is off by default and must be reactivated after messageflow (re)deployment!**


### Add broker IP/hostnames and ports to /opt/zabbix-iib-monitoring/scripts/broker.txt

```nano /opt/zabbix-iib-monitoring/scripts/broker.txt```

### Start zabbix-iib-monitor service to receive monitoring data (check "/opt/zabbix-iib-monitoring/scripts/zabbix-iib-monitoring.ini" for settings regarding file paths, logging, etc.)

```systemctl start zabbix-iib-monitor```

NOTE: zabbix-iib-monitor service needs to be restarted after brokers.txt is modified. Command: ```systemctl restart zabbix-iib-monitor```

### (Optional) Test if the scripts are working

```zabbix_agentd -t "iib.mqtt_topic.discovery[node]"```

Should return something like this:
```
"data": [
    {
      "{#TOPIC}": "IBM/IntegrationBus/IIBNODE/Status"
    }
]
```

If it did, everything should be ready for adding discovery rules and items to Zabbix

If not check zabbix-iib-monitor service is up and running ```systemctl status zabbix-iib-monitor``` and its logs /var/logs/zabbix-iib-monitor.log

### In Zabbix add 3 iib.mqtt_topic.discovery rules
   - One with key "iib.mqtt_topic.discovery[node]"
   - One with key "iib.mqtt_topic.discovery[server]"
   - One with key "iib.mqtt_topic.discovery[messageflow]"
   
### Add prototype items
   - For rule "iib.mqtt_topic.discovery[node]" use key "iib.node.status[{#TOPIC}]" to get updates on node status
   - For rule "iib.mqtt_topic.discovery[server]" use key "iib.server.status[{#TOPIC}]" to get updates on server status
   - For rule "iib.mqtt_topic.discovery[messageflow]" use key "iib.messageflow[{#TOPIC}, *dataFieldName*]" where *dataFieldName* is the json field name. Leave *dataFieldName* parameter empty and set "Type of information" to "text" to see all available fields. A description for all fields can be found here: https://www.ibm.com/support/knowledgecenter/en/SSRLD6_7.3.0/kqi_userguide/attr_kqitacmf.html


