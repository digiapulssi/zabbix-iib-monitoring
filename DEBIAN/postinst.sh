!#/bin/bash

virtualenv /opt/zabbix-iib-monitor/virtualenv

. /opt/zabbix-iib-monitoring/virtualenv/bin/activate

pip install xmljson ConfigParser six paho-mqtt
