# zabbix-iib-monitoring

This project contains scripts for listening to IBM Integration Bus MQTT messages and ready-to-install scripts for Zabbix Agent. 

These scripts do **not require** to be installed locally with IBM Integration Bus, although you will need to change the bind address of each integration node you want to monitor from the outside. Bind address can be found in a file at C:\ProgramData\IBM\MQSI\components\nodeName\config\nodeName

## Installation

### 1. Install virtualenv with pip

```pip install virtualenv```

### 2. Create a new virtual environment with any name

```virtualenv envName``` or using full path ```virtualenv /path/to/envName```

### 3. Activate virtualenv

```source /path/to/envName/bin/activate```

"(envName)" should appear at the start of the command line once it's activated

### 4. The following packages are required:
- xmljson
- ConfigParser
- six
- paho-mqtt

Install packages with (make sure to activate the virtualenv first):
```pip install xmljson ConfigParser six paho-mqtt```

The virtualenv is now ready, use command ```deactivate``` to exit the virtualenv.

### 5. Copy the file(s) under [etc/zabbix/scripts](etc/zabbix/scripts) to `/etc/zabbix/scripts`

### 6. Make sure all scripts are executable ```sudo chmod a+x /etc/zabbix/scripts/*```

### 7. Copy the file(s) under [etc/zabbix/zabbix_agentd.d](etc/zabbix/zabbix_agentd.d) to `/etc/zabbix/zabbix_agentd.d`

### 8. Copy files zabbix-iib-monitor.py, zabbix-iib-monitor.ini and brokers.txt anywhere (E.g. create directory "zabbix-iib" in user home directory)

### 9. Edit zabbix-iib-monitoring.py, and on the first row change the path to the virtualenv you just created:
```#!/path/to/envName/bin/python``` 

This way the script is automatically executed in the virtualenv, without the need to activate it first.

## Use

### 1. In IBM Integration Console, adjust data collection interval for each integration node (that you want to monitor) with command:

**NOTE: Integration node needs to be shutdown first**
```
mqsichangebroker yourNodeName -v 10
```
("-v" = data collection interval, in minutes, min 1 max 43200 default 60)

### 2. In IBM Integration Console, activate messageflow data collection.

To activate data collection for all servers and messageflows in a specific node, use command:
```
mqsichangeflowstats yourNodeName -g -j -a -o json -c active
```
("-g" = all integration servers, "-j" = all message flows, "-a" = archive publishing, "-o json" = output format "json", "-c active" = control: enable data collection)

If you wish to activate data collection only for a specific message flow, use the following command:
```
mqsichangeflowstats yourNodeName -e serverName -k applicationName (-y staticLibraryName) -f messageflowName -a -o json -c active
```
Use command ```mqsichangeflowstats -h``` to see all options.

**NOTE: Messageflow data collection is off by default and must be reactivated after messageflow (re)deployment!**

### 3. Run "zabbix-iib-monitoring.py" (check "zabbix-iib-monitoring.ini" for connection settings) to start receiving monitoring data

### 4. In Zabbix add 3 iib.mqtt_topic.discovery rules
   - One with key "iib.mqtt_topic.discovery[node]"
   - One with key "iib.mqtt_topic.discovery[server]"
   - One with key "iib.mqtt_topic.discovery[messageflow]"
   
### 5. Add prototype items
   - For rule "iib.mqtt_topic.discovery[node]" use key "iib.node.status[{#TOPIC}]" to get updates on node status
   - For rule "iib.mqtt_topic.discovery[server]" use key "iib.server.status[{#TOPIC}]" to get updates on server status
   - For rule "iib.mqtt_topic.discovery[messageflow]" use key "iib.messageflow[{#TOPIC}, *dataFieldName*]" where *dataFieldName* is the json field name (Leave parameter empty and set "Type of information" to "text" to see all available fields)


