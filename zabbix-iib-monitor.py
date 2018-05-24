import paho.mqtt.client as mqtt
import json
import time
import os
import xml.etree.ElementTree as ET
import re
from xmljson import abdera as ab
from xml.etree.ElementTree import fromstring
import ConfigParser
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
# topic format: ("topic", QoS)
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
      logging.info("Message Recieved: " + str(message.payload.decode("utf-8")))
      logging.info("Message topic=" + message.topic)
      logging.info("Message qos=" + str(message.qos))
      logging.info("Message retain flag=" + str(message.retain))
   else:
      logging.info("Message from topic: " + message.topic)
   
   pattern = "(IBM/IntegrationBus/(\w+)/Status/ExecutionGroup/(\w+))|(IBM/IntegrationBus/(\w+)/Status)"
   match = re.match(pattern, message.topic)
   
   obj = {}
   if match == None:
      if os.path.isfile(jsonFile):
         try:
            jsonStr = f.read()
            obj = json.loads(jsonStr)
               
            obj[str(message.topic)] = json.loads(message.payload.decode("utf-8"))
                  
            with open(jsonFile, 'w') as outfile:
               json.dump(obj, outfile)
               logging.info("Write Complete")
            
         except ValueError: 
            logging.error("Error while reading JSON")
      
      else:
         try:
            jsonObj = {}
            jsonObj[message.topic] = str(message.payload.decode("utf-8"))
            with open(jsonFile, 'w') as outfile:
               json.dump(jsonObj, outfile)
               logging.info("Write Complete\n")
               
         except ValueError: 
            logging.error("Error while writing to JSON file")
   else:
      parsedJSON = ab.data(fromstring(str(message.payload.decode("utf-8"))))
      
      try:
         if os.path.isfile(jsonFile):
            jsonStr = f.read()
            obj = json.loads(jsonStr)
               
         obj[str(message.topic)] = parsedJSON
         
         with open(jsonFile, 'w') as outfile:
            json.dump(obj, outfile)
            
            logging.info("Write Complete")
         
      except ValueError: 
         logging.error("Error while reading JSON")

def on_connect(client, userdata, flags, rc):
   conn_codes = [
      "Connection successful",
      "Connection refused - incorrect protocol version",
      "Connection refused - invalid client identifier",
      "Connection refused - server unavailable",
      "Connection refused - bad username or password",
      "Connection refused - not authorised"
   ]
   
   logging.info(conn_codes[rc] + ". (code " + str(rc) + ")")
   client.subscribe(TOPICS)

def on_subscribe(client, userdata, mid, granted_qos):
   logging.info("Successfuly subscribed to topic(s)")

def on_unsubscribe(client, userdata, mid):
   logging.info("Unsubscribed from topic")

def on_disconnect(client, userdata, rc):

   if rc != 0:
      logging.error("Unexpected disconnection.")
   else:
      logging.info("Disconnected")

def on_log(client, userdata, level, buf):
   logging.info("Log message: " + str(client) + " " + str(userdata) + " " + str(buf))
   #f=open(logFile, "a+")
   #logging.info(get_timeStr() + " Log message: " + str(client) + " " + str(userdata) + " " + str(buf)  + "\n")
   #f.close()

def get_timeStr():
   datetimeFormat = ConfigSectionMap("CONFIG")['datetimeformat']
   ts = time.localtime()
   timeStr = time.strftime(datetimeFormat , ts)
   return timeStr
   
def thread_MQTT(BROKER_ADDRESS,PORT,id):
   client = mqtt.Client(id) 
   
   client.on_connect = on_connect
   client.on_message = on_message
   client.on_subscribe = on_subscribe
   client.on_unsubscribe = on_unsubscribe
   client.on_disconnect = on_disconnect
   
   if enableLogMsg:
      client.on_log = on_log
   
   logging.info(threading.currentThread().getName() + " Connecting to broker: " + BROKER_ADDRESS + ":" + PORT + " with id: " + id + "\n")
   client.connect( BROKER_ADDRESS, int(PORT))
   
   client.loop_forever()

if __name__ == "__main__":
   logFile = ConfigSectionMap("CONFIG")['logfile']
   jsonFile = ConfigSectionMap("CONFIG")['jsonfile']
   
   enableLogMsg = config.getboolean("CONFIG", "enablelogmsg")
   printMsg = config.getboolean("CONFIG", "printmsg")
   
   brokers = ConfigSectionMap("CONFIG")['brokers']
   
   #BROKER_ADDRESS = ConfigSectionMap("CONFIG")['ip']
   #PORT = ConfigSectionMap("CONFIG")['port']
   #clientId = ConfigSectionMap("CONFIG")['clientid']
   
   #filename = os.path.splitext(__file__)[0]
   
   f=open(jsonFile, "r+")
   logging.basicConfig(filename=logFile, filemode='a',format='%(asctime)s  %(levelname)s: %(message)s')
   broker_list=open(brokers, 'r')
   brokers = broker_list.readfiles()
   
   threads = []
   for i in range (len(open(brokers).readlines())):
      b=brokers[i].split(',')
      t = threading.Thread(target = thread_MQTT, args = (b[0],b[1],b[2]))
      threads.append(t)
      t.start()
   
   while threading.activeCount() > 1:
      pass
   else:
      f.close()
   
   '''
   client = mqtt.Client(clientId) 
   
   client.on_connect = on_connect
   client.on_message = on_message
   client.on_subscribe = on_subscribe
   client.on_unsubscribe = on_unsubscribe
   client.on_disconnect = on_disconnect
   
   if enableLogMsg:
      client.on_log = on_log
   
   logging.info(get_timeStr() + " Connecting to broker: " + BROKER_ADDRESS + ":" + PORT + "\n")
   f.close()
   client.connect( BROKER_ADDRESS, int(PORT))
   
   client.loop_forever()
'''