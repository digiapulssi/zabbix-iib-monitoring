# zabbix-iib-monitoring

This project contains scripts for listening to IBM Integration Bus MQTT messages and ready-to-install scripts for Zabbix Agent.

## Installation

* Copy the files under [etc/zabbix/scripts](etc/zabbix/scripts) to `/etc/zabbix/scripts`
* Copy the files under [etc/zabbix/zabbix_agentd.d](etc/zabbix/zabbix_agentd.d) to `/etc/zabbix/zabbix_agentd.d`
* Copy "zabbix-iib-monitoring.py" and "zabbix-iib-monitoring.ini" anywhere on the agent machine (does not require to be local with IBM Integration Bus)

## Usage

* Run "zabbix-iib-monitoring.py" (check "zabbix-iib-monitoring.ini" for connection settings) to start recieving monitoring data
* Add iib.mqtt_topic.discovery to host/template
* Add items host/template

