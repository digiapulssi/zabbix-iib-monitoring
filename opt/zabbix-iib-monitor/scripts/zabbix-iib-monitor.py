#!/opt/zabbix-iib-monitor/virtualenv/bin/python

from xmljson import abdera as ab
from xml.etree.ElementTree import fromstring
from six.moves import configparser as ConfigParser
from socket import error as socket_error
import paho.mqtt.client as mqtt
import threading
import logging
import copy
import json
import time
import os
import re
import errno

import sys

##### CONFIG #####
# path to config file
configFile = "/opt/zabbix-iib-monitor/scripts/zabbix-iib-monitor.ini"

##### TOPICS #####
#
# SPECIAL CHARACTERS IN TOPICS   
#
# topic level separator '/'
# multilevel wildcard   '#'
# single-level wildcard '+'
#

integrationNodeName = "+"
integrationServerName = "+"
applicationName= "+"
messageFlowName = "+"

# Topics that will be subscribed to
# format: ("topic", QoS)
TOPICS= [ 
   ("IBM/IntegrationBus/" + integrationNodeName + "/Status", 0),
   ("IBM/IntegrationBus/" + integrationNodeName + "/Status/ExecutionGroup/" + integrationServerName, 0) ,
   ("IBM/IntegrationBus/" + integrationNodeName + "/Statistics/JSON/Archive/" + integrationServerName + "/applications/" + applicationName + "/messageflows/" + messageFlowName, 0)
]

##### CODE #####

config = ConfigParser.ConfigParser()
configRaw = ConfigParser.RawConfigParser()
confFile = config.read(configFile)
configFileRaw = configRaw.read(configFile)
conf_sections = config.sections()
conf_sectionsRaw = configRaw.sections()

def on_message(client, userdata, message):

   if printMsg:
      logging.info(threading.currentThread().getName() + " Message from topic: " + message.topic)
      logging.info(threading.currentThread().getName() + " Message Payload: " + str(message.payload.decode(encoding)))
      logging.info(threading.currentThread().getName() + " Message qos=" + str(message.qos))
      logging.info(threading.currentThread().getName() + " Message retain flag=" + str(message.retain))
   else:
      logging.info(threading.currentThread().getName() + " Message from topic: " + message.topic)
   
   pattern = "(^IBM/IntegrationBus/\w+/Status$|^IBM/IntegrationBus/\w+/Status/ExecutionGroup/\w+)"
   match_status = re.match(pattern, message.topic)
   
   obj = {}
   objCopy = {}
   output = {}
   
   with lock:
      try:
         if not os.path.isfile(jsonFile):
            tmp=open(jsonFile,"w")
            logging.info(threading.currentThread().getName() + " JSON file created")
            objCopy = None
            tmp.close()
         elif os.stat(jsonFile).st_size > 0:
            with open(jsonFile) as f:
               # load old data
               logging.info(threading.currentThread().getName() + " Reading JSON file")
               obj = json.load(f)
               
               # copy old data
               objCopy = copy.deepcopy(obj)
      except:
         logging.error(threading.currentThread().getName() + " ValueError: Error while creating/reading JSON")
         
      # overwrite old data with new
      if match_status == None:
         # if JSON
         try:
            obj[str(message.topic)] = json.loads(message.payload.decode(encoding))
            # increment defined values
            output = inc_msgflow_data(str(message.topic), obj, objCopy)
            logging.info(threading.currentThread().getName() + " New data acquired successfully")
         except:
            logging.error(threading.currentThread().getName() + " JSON topic: Error copying new data")
   
      else:
         #if XML (== node or server status topic, defined by regex variable "pattern")
         try:
            parsedjson = ab.data(fromstring(str(message.payload.decode(encoding))))
            obj[str(message.topic)] = parsedjson
            output = obj
            logging.info(threading.currentThread().getName() + " New data acquired successfully")
         except:
            logging.error(threading.currentThread().getName() + " XML topic: Error copying new data")
         
      try:
         # write to file
         with open(jsonFile, 'w') as outfile:
            json.dump(output, outfile)
         
         logging.info(threading.currentThread().getName() + " Write Complete")
      except:
         logging.error(threading.currentThread().getName() + " Error writing to file")
   
def on_connect(client, userdata, flags, rc):
   conn_codes = [
      "Connection successful",
      "Connection refused - incorrect protocol version",
      "Connection refused - invalid client identifier",
      "Connection refused - server unavailable",
      "Connection refused - bad username or password",
      "Connection refused - not authorised"
   ]
   global connected
   connected = True
   logging.info(threading.currentThread().getName() + " " + conn_codes[rc] + ". (code " + str(rc) + ")")
   client.subscribe(TOPICS)

def on_subscribe(client, userdata, mid, granted_qos):
   logging.info(threading.currentThread().getName() + " Successfully subscribed to topic(s)")

def on_unsubscribe(client, userdata, mid):
   logging.info(threading.currentThread().getName() + " Unsubscribed from topic")

def on_disconnect(client, userdata, rc):
   global connected

   if rc != 0:
      connected = False
      logging.warning(threading.currentThread().getName() + " Unexpected disconnect")
   else:
      logging.info(threading.currentThread().getName() + " Disconnected")
      connected = False

def on_log(client, userdata, level, buf):
   logging.debug(threading.currentThread().getName() + " Log message: " + str(client) + " " + str(userdata) + " " + str(buf))

def inc_msgflow_data(mqtt_topic, new, old):
   try:
   
      if old is None or mqtt_topic not in old:
         newMsgflow = new[mqtt_topic]['WMQIStatisticsAccounting']['MessageFlow']
      else:
         newMsgflow = new[mqtt_topic]['WMQIStatisticsAccounting']['MessageFlow']
         oldMsgflow = old[mqtt_topic]['WMQIStatisticsAccounting']['MessageFlow']
      
      # keys to be incremented
      keys = ['ElapsedTimeWaitingForInputMessage','TotalInputMessages','TotalSizeOfInputMessages']
      
      for key in keys:
         if old is None or mqtt_topic not in old:
            newMsgflow[key + 'Incremental'] = newMsgflow[key]
         else:
            if (key + 'Incremental') in oldMsgflow:
               newMsgflow[key + 'Incremental'] = oldMsgflow[key + 'Incremental'] + newMsgflow[key]
            else:
               newMsgflow[key + 'Incremental'] = oldMsgflow[key] + newMsgflow[key]
      
      return new
   except: 
      logging.error(threading.currentThread().getName() + " Error incrementing values")

def thread_MQTT(BROKER_ADDRESS,PORT,id,stop):
   try:
      client = mqtt.Client(id) 
      
      client.on_connect = on_connect
      client.on_message = on_message
      client.on_subscribe = on_subscribe 
      client.on_unsubscribe = on_unsubscribe
      client.on_disconnect = on_disconnect
      
      client.reconnect_delay_set(10, 60)
      
      if enableLogMsg:
         client.on_log = on_log
      
      logging.info(threading.currentThread().getName() + " Connecting to broker: " + BROKER_ADDRESS + ":" + PORT)
      client.connect( BROKER_ADDRESS, int(PORT))
      
      client.loop_start()
      
      while not stop():
         time.sleep(0.01)
         pass
         
      client.disconnect()
      client.loop_stop()
      
      logging.info(threading.currentThread().getName() + " Stopped")
   
   except socket_error as serr:
      if serr.errno == errno.ECONNRESET:
         logging.warning(threading.currentThread().getName() + " Connection reset")
      elif serr.errno == errno.ECONNREFUSED:
         logging.error(threading.currentThread().getName() + " Connection refused")
      elif serr.errno == errno.EHOSTUNREACH:
         logging.error(threading.currentThread().getName() + " No route to host")
         
      else:
         logging.error(threading.currentThread().getName() + " " + str(serr))
         raise serr
         
if __name__ == "__main__":
   
   logFile = config.get("CONFIG", "logfile")
   enableLogMsg = config.getboolean("CONFIG", "enablelogmsg")
   loglvl = config.get("CONFIG", "loglevel")
   datetimeFormat = configRaw.get("CONFIG", "datetimeformat")
   encoding = config.get("CONFIG", "encoding")
   
   jsonFile = config.get("CONFIG", "jsonfile")
   printMsg = config.getboolean("CONFIG", "printmsg")
   brokers_file = config.get("CONFIG", "brokers")
   
   if not os.path.isfile(logFile):
      tmp=open(logFile,"w")
      tmp.close()
   
   logging.basicConfig(filename=logFile, filemode='a', level=loglvl, datefmt=datetimeFormat, format='%(asctime)s  %(levelname)s: %(message)s')
   logging.info(" --- Main thread starting ---")
   
   try:
      broker_list=open(brokers_file, 'r')
      brokers = broker_list.readlines()
      broker_list.close()
      
      doExit = False
      lock = threading.Lock()
      threads = []
      count = 1
      for i in range (len(brokers)):
         if brokers[i].strip() == "" or brokers[i].lstrip()[0] == '#':
            continue
         
         b=brokers[i].split(',')
         
         t = threading.Thread(name="MQTT-Client-" + str(count), target = thread_MQTT, args = (b[0],b[1],"clientId", lambda: doExit))
         count = count + 1
         threads.append(t)
         t.start()
         
      while not doExit:
         time.sleep(0.01)
         pass
         
   except (KeyboardInterrupt, SystemExit):
      doExit = True
   
   for thread in threads:
      thread.join()
   
   logging.info(" --- Main thread stopped ---")
   