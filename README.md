# zabbix-iib-monitoring

This project contains scripts for listening to IBM Integration Bus MQTT messages and ready-to-install scripts for Zabbix Agent. 

These scripts do **not require** to be installed locally with IBM Integration Bus, although you will need to change the bind address of each integration node you want to monitor from the outside. Bind address can be found in a file at C:\ProgramData\IBM\MQSI\components\nodeName\config\nodeName

## Installation

#### Switch to root user

```sudo su```

#### Download all files from GitHub

curl -LJO https://github.com/digiapulssi/zabbix-iib-monitoring/archive/develop.tar.gz 

#### Install pip (python v2) or pip3 (python v3)

**For Ubuntu**
```apt-get install python-pip``` or ```apt-get install python3-pip```

#### Install virtualenv with pip

```pip install virtualenv``` or ```pip3 install virtualenv```

#### Create a new virtual environment

```virtualenv /opt/zabbix-iib-monitoring/virtualenv```

**NOTE: If you use another path you need to update the path on the first line of zabbix-iib-monitoring.py**

#### Activate virtualenv

```. /opt/zabbix-iib-monitoring/virtualenv/bin/activate```

"(virtualenv)" should appear at the start of the command line once it's activated

#### Install required python packages to the virtual environment

The following packages are required:
- xmljson
- ConfigParser
- six
- paho-mqtt

Install packages with (make sure the virtualenv is activated):
```pip install xmljson ConfigParser six paho-mqtt```

Once all packages are sucessfully installed the virtualenv is ready, use command ```deactivate``` to exit the virtualenv.

#### Copy the file(s) under [etc/zabbix/scripts](etc/zabbix/scripts) to `/etc/zabbix/scripts`


#### Make sure all scripts are readable and executable ```sudo chmod a+rx /etc/zabbix/scripts/*```


#### Copy the file(s) under [etc/zabbix/zabbix_agentd.d](etc/zabbix/zabbix_agentd.d) to `/etc/zabbix/zabbix_agentd.d`
chmod read


#### Copy files *zabbix-iib-monitor.py*, *zabbix-iib-monitor.ini* and *brokers.txt* to /opt/zabbix-iib-monitoring/scripts 

chmod read


## Use

#### In IBM Integration Console, adjust data collection interval for each integration node (that you want to monitor) with command:

**NOTE: Integration node needs to be shutdown first**
```
mqsichangebroker yourNodeName -v 10
```
("-v" = data collection interval, in minutes, min 1 max 43200 default 60)

#### In IBM Integration Console, activate messageflow data collection.

To activate data collection for all servers and messageflows in a specific node, use command:

```mqsichangeflowstats yourNodeName -g -j -a -o json -c active```

("-g" = all integration servers, "-j" = all message flows, "-a" = archive publishing, "-o json" = output format "json", "-c active" = control: enable data collection)

If you wish to activate data collection only for a specific message flow, use the following command:

```mqsichangeflowstats yourNodeName -e serverName -k applicationName (-y staticLibraryName) -f messageflowName -a -o json -c active```

Use command ```mqsichangeflowstats -h``` to see all options.

**NOTE: Messageflow data collection is off by default and must be reactivated after messageflow (re)deployment!**


#### Restart Zabbix-agent service

```sudo service zabbix-agent restart```

#### Add broker IP/hostnames and ports to /opt/zabbix-iib-monitoring/scripts/broker.txt

#### As zabbix user, run "zabbix-iib-monitoring.py"  to start receiving monitoring data (check "zabbix-iib-monitoring.ini" for settings regarding file paths, logging, etc.)

#### In Zabbix add 3 iib.mqtt_topic.discovery rules
   - One with key "iib.mqtt_topic.discovery[node]"
   - One with key "iib.mqtt_topic.discovery[server]"
   - One with key "iib.mqtt_topic.discovery[messageflow]"
   
#### Add prototype items
   - For rule "iib.mqtt_topic.discovery[node]" use key "iib.node.status[{#TOPIC}]" to get updates on node status
   - For rule "iib.mqtt_topic.discovery[server]" use key "iib.server.status[{#TOPIC}]" to get updates on server status
   - For rule "iib.mqtt_topic.discovery[messageflow]" use key "iib.messageflow[{#TOPIC}, *dataFieldName*]" where *dataFieldName* is the json field name (Leave parameter empty and set "Type of information" to "text" to see all available fields)


