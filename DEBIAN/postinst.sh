#!/bin/bash

# create virtualenv for zabbix-iib-monitor
virtualenv /opt/zabbix-iib-monitor/virtualenv

# activate virtualenv
. /opt/zabbix-iib-monitor/virtualenv/bin/activate

# install required packages to virtualenv
pip install xmljson ConfigParser six paho-mqtt

# deactivate virtualenv
deactivate