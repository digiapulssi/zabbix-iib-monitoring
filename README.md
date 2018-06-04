# zabbix-iib-monitoring

This project contains scripts for listening to IBM Integration Bus MQTT messages and ready-to-install scripts for Zabbix Agent. These scripts do **not require** to be local with IBM Integration Bus, although you will need to change the bind address of each integration node you want to monitor from the outside. Bind address can be found in file at C:\ProgramData\IBM\MQSI\components\nodeName\config\nodeName

## Installation

### Python / PIP

1. Install virtualenv with pip

```pip install virtualenv```

2. Create virtual environment "iib-python-venv" (will create folder "iib-python-venv" in the current directory, delete folder to remove the virtualenv)

```virtualenv iib-python-venv```

3. Activate virtualenv

```source /<pathToEnv>/iib-python-venv/bin/activate```

"(iib-python-venv)" should appear at the start of the commandline once activated

4. The following packages are required in the virtualenv:
- xmljson
- ConfigParser
- six
- paho-mqtt

Install packages with:
```pip install xmljson ConfigParser six paho-mqtt```

The virtualenv is now ready, use command ```deactivate``` to exit the virtualenv.

### Scripts

1. Copy the file(s) under [etc/zabbix/scripts](etc/zabbix/scripts) to `/etc/zabbix/scripts`
2. Copy the file(s) under [etc/zabbix/zabbix_agentd.d](etc/zabbix/zabbix_agentd.d) to `/etc/zabbix/zabbix_agentd.d`
3. Copy all the other files somewhere easy to find on the agent machine (E.g. user home directory)
4. Edit zabbix-iib-monitoring.py, on the first row add/replace "#! /\<pathToEnv\>/iib-python-venv/bin/python"

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
mqsichangebroker yourNodeName -v 10
```
("-v" = data collection interval, in minutes, min 1 max 43200)

### Scripts & Zabbix

1. Run "zabbix-iib-monitoring.py" (check "zabbix-iib-monitoring.ini" for connection settings) to start recieving monitoring data

2. Add 3 iib.mqtt_topic.discovery to host/template
   - Use key "iib.mqtt_topic.discovery[]" with parameter "node", "server" or "messageflow" (one of each)
   - Set filter ```"{#TOPIC_NODE}" matches "^IBM/IntegrationBus/[A-Za-z0-9]*/Status$"``` for "iib.mqtt_topic.discovery[node]"
   - Set filter ```"{#TOPIC_SERVER}" matches "^IBM/IntegrationBus/[A-Za-z0-9]*/Status/ExecutionGroup/[A-Za-z0-9]*$"``` for "iib.mqtt_topic.discovery[server]"
   - Set filter ```"{#TOPIC_MESSAGEFLOW}" matches "^IBM/IntegrationBus/[A-Za-z0-9]*/Statistics/JSON/Archive"``` for "iib.mqtt_topic.discovery[messageflow]"
3. Add items to host/template
   - Use key "iib.messageflow[{TOPIC_MESSAGEFLOW}, *dataFieldName*]" where "*dataFieldName*" is the json field name (Leave parameter empty and set "Type of information" to "text" to see all available fields)
   - Use key "iib.node.status[{TOPIC_NODE}]" to get updates on node status
   - Use key "iib.server.status[{TOPIC_SERVER}]" to get updates on server status

