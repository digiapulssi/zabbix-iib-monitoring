#!replace this with the virtualenv path

import paho.mqtt.client as mqtt
import json
import time
import os
import re
from xmljson import abdera as ab
from xml.etree.ElementTree import fromstring
from six.moves import configparser as ConfigParser
import threading
import logging

##### CONFIG #####
# path to config file
configFile = "zabbix-iib-monitor.ini"

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
   ("IBM/IntegrationBus/" + integrationNodeName + "/Statistics/JSON/Archive/" + integrationServerName + "/applications/" + applicationName + "/messageflows/" + messageFlowName, 0),
   ("IBM/IntegrationBus/" + integrationNodeName + "/Statistics/JSON/Snapshot/" + integrationServerName + "/applications/" + applicationName + "/messageflows/" + messageFlowName, 0)
]

##### CODE #####

config = ConfigParser.ConfigParser()
confFile = config.read(configFile)
conf_sections = config.sections()

def ConfigSectionMap(section):
    dict1 = {}
    options = config.options(section)
    for option in options:
        try:
            dict1[option] = config.get(section, option)
            if dict1[option] == -1:
               logging.info("Configuration file, skip: %s" % option)
        except:
            logging.info("Exception with configuration file on %s!" % option)
            dict1[option] = None
    return dict1

def on_message(client, userdata, message):

   if printMsg:
      logging.info(threading.currentThread().getName() + " Message Recieved: " + str(message.payload.decode("utf-8")))
      logging.info(threading.currentThread().getName() + " Message topic=" + message.topic)
      logging.info(threading.currentThread().getName() + " Message qos=" + str(message.qos))
      logging.info(threading.currentThread().getName() + " Message retain flag=" + str(message.retain))
   else:
      logging.info(threading.currentThread().getName() + " Message from topic: " + message.topic)
   
   pattern = "(IBM/IntegrationBus/(\w+)/Status/ExecutionGroup/(\w+)) | (IBM/IntegrationBus/(\w+)/Status)"
   match = re.match(pattern, message.topic)
   
   obj = {}
   copy = {}
   # JSON topic
   if match == None:
      try:
         with lock:
            if not os.path.isfile(jsonFile):
               tmp=open(jsonFile,"w")
               tmp.close()
            elif os.stat(jsonFile).st_size > 0:
               with open(jsonFile) as f:
                  obj = json.load(f)
                  
            copy = obj
            obj[str(message.topic)] = json.loads(message.payload.decode("utf-8"))
            
            # incerement values
            if 'ElapsedTimeWaitingForInputMessageIncremental' in obj:
               logging.info(threading.currentThread().getName() + " Field not found")
               obj[str(message.topic)]['WMQIStatisticsAccounting']['MessageFlow']['ElapsedTimeWaitingForInputMessageIncremental'] = obj[str(message.topic)]['WMQIStatisticsAccounting']['MessageFlow']['ElapsedTimeWaitingForInputMessage']
            else:
               logging.info(threading.currentThread().getName() + " Field found")
               obj[str(message.topic)]['WMQIStatisticsAccounting']['MessageFlow']['ElapsedTimeWaitingForInputMessageIncremental'] += copy[str(message.topic)]['WMQIStatisticsAccounting']['MessageFlow']['ElapsedTimeWaitingForInputMessage']
            
            with open(jsonFile, 'w') as outfile:
               json.dump(obj, outfile)
            
         logging.info(threading.currentThread().getName() + " Write Complete")
            
      except ValueError: 
            logging.error(threading.currentThread().getName() + " JSON topic ValueError: Error while reading JSON")
   
   # XML topic
   else:
      parsedJSON = ab.data(fromstring(str(message.payload.decode("utf-8"))))
      
      try:
         with lock:
            if not os.path.isfile(jsonFile):
               tmp=open(jsonFile,"w")
               tmp.close()
            elif os.stat(jsonFile).st_size > 0:
               with open(jsonFile) as f:
                  obj = json.load(f)
                  
            obj[str(message.topic)] = parsedJSON
            
            with open(jsonFile, 'w') as outfile:
               outfile.write(json.dumps(obj))
            
         logging.info(threading.currentThread().getName() + " Write Complete")
         
      except ValueError: 
         logging.error(threading.currentThread().getName() + " XML topic ValueError: Error while reading JSON")

def on_connect(client, userdata, flags, rc):
   conn_codes = [
      "Connection successful",
      "Connection refused - incorrect protocol version",
      "Connection refused - invalid client identifier",
      "Connection refused - server unavailable",
      "Connection refused - bad username or password",
      "Connection refused - not authorised"
   ]
   
   logging.info(threading.currentThread().getName() + " " + conn_codes[rc] + ". (code " + str(rc) + ")")
   client.subscribe(TOPICS)

def on_subscribe(client, userdata, mid, granted_qos):
   logging.info(threading.currentThread().getName() + " Successfuly subscribed to topic(s)")

def on_unsubscribe(client, userdata, mid):
   logging.info(threading.currentThread().getName() + " Unsubscribed from topic")

def on_disconnect(client, userdata, rc):

   if rc != 0:
      logging.warning(threading.currentThread().getName() + " Unexpected disconnection.")
   else:
      logging.info(threading.currentThread().getName() + " Disconnected")

def on_log(client, userdata, level, buf):
   logging.info(threading.currentThread().getName() + " Log message: " + str(client) + " " + str(userdata) + " " + str(buf))
   
def thread_MQTT(BROKER_ADDRESS,PORT,id):
   client = mqtt.Client(id) 
   
   client.on_connect = on_connect
   client.on_message = on_message
   client.on_subscribe = on_subscribe
   client.on_unsubscribe = on_unsubscribe
   client.on_disconnect = on_disconnect
   
   if enableLogMsg:
      client.on_log = on_log
   
   logging.info(threading.currentThread().getName() + " Connecting to broker: " + BROKER_ADDRESS + ":" + PORT + " with id: " + id)
   client.connect( BROKER_ADDRESS, int(PORT))
   
   client.loop_forever()

if __name__ == "__main__":
   logFile = ConfigSectionMap("CONFIG")['logfile']
   enableLogMsg = config.getboolean("CONFIG", "enablelogmsg")
   loglvl = ConfigSectionMap("CONFIG")['loglevel']
   datetimeFormat = ConfigSectionMap("CONFIG")['datetimeformat']
   
   jsonFile = ConfigSectionMap("CONFIG")['jsonfile']
   printMsg = config.getboolean("CONFIG", "printmsg")
   brokers_file = ConfigSectionMap("CONFIG")['brokers']
   
   logging.basicConfig(filename=logFile, filemode='a', level=logging.DEBUG, datefmt=datetimeFormat, format='%(asctime)s  %(levelname)s: %(message)s')
   logging.info(" --- Starting ---")
   
   broker_list=open(brokers_file, 'r')
   brokers = broker_list.readlines()
   broker_list.close()
   
   lock = threading.Lock()
   threads = []
   for i in range (len(brokers)):
      if brokers[i][0] == '#':
         continue
      
      b=brokers[i].split(',')
      
      t = threading.Thread(target = thread_MQTT, args = (b[0],b[1],b[2]))
      threads.append(t)
      t.start()
   
   while threading.activeCount() > 1:
      pass
   else:
      logging.info(" --- Exiting ---")
   