# zabbix-iib-monitoring

This project contains scripts for listening to IBM Integration Bus MQTT messages and ready-to-install scripts for Zabbix Agent.

## Installation

* Copy the files under [etc/zabbix/scripts](etc/zabbix/scripts) to `/etc/zabbix/scripts`
* Copy the files under [etc/zabbix/zabbix_agentd.d](etc/zabbix/zabbix_agentd.d) to `/etc/zabbix/zabbix_agentd.d`
* Copy "zabbix-iib-monitoring.py" and "zabbix-iib-monitoring.ini" anywhere on the agent machine (does **not** require to be local with IBM Integration Bus)

## Usage

* Activate messageflow data collection in IBM Integration Console with command:
```
mqsichangeflowstats yourNodeName -g -j -s -o json -c active
```
("-g" = all integration servers, "-j" = all message flows, "-s" = snapshot publishing, "-o json" = output format "json", -"c active" = control enable data collection, use command ```mqsichangeflowstats``` to see all options)

**_NOTE_: Messageflow data collection is off by default and must be reactivated after (re)deployment!**

* Run "zabbix-iib-monitoring.py" (check "zabbix-iib-monitoring.ini" for connection settings) to start recieving monitoring data
* Add iib.mqtt_topic.discovery to host/template
* Add items to host/template

