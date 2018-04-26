import paho.mqtt.client as mqtt
import json
import time
import os
import xml.etree.ElementTree as ET
import re
from xmljson import abdera as ab
from xml.etree.ElementTree import fromstring
import ConfigParser

config = ConfigParser.ConfigParser()
confFile = config.read(os.path.splitext(__file__)[0] + ".ini")
conf_sections = config.sections()

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
   ("IBM/IntegrationBus/" + integrationNodeName + "/Statistics/JSON/SnapShot/" + integrationServerName + "/applications/" + applicationName + "/messageflows/" + messageFlowName, 0)
   
]

##### CODE #####

def ConfigSectionMap(section):
    dict1 = {}
    options = config.options(section)
    for option in options:
        try:
            dict1[option] = config.get(section, option)
            if dict1[option] == -1:
                DebugPrint("skip: %s" % option)
        except:
            print("exception on %s!" % option)
            dict1[option] = None
    return dict1

def on_message(client, userdata, message):
   f=open(logFileName, "a+")

   if printMsg:
      f.write(get_timeStr() + " Message Recieved: " + str(message.payload.decode("utf-8") + "\n"))
      f.write(get_timeStr() + " Message topic=" + message.topic + "\n")
      f.write(get_timeStr() + " Message qos=" + str(message.qos) + "\n")
      f.write(get_timeStr() + " Message retain flag=" + str(message.retain) + "\n")
   else:
      f.write(get_timeStr() +  " Message from topic: " + message.topic + "\n")
   f.close()
   print(message.topic)
   
   pattern = "(IBM/IntegrationBus/(\w+)/Status/ExecutionGroup/(\w+))|(IBM/IntegrationBus/(\w+)/Status)"
   match = re.match(pattern, message.topic)
   
   obj = {}
   if match == None:
      print("JSON Topic")
      if os.path.isfile(jsonFileName):
         try:
            with open(jsonFileName, 'r') as jsonFile:
               obj = json.load(jsonFile)
               
            obj[str(message.topic)] = json.loads(message.payload.decode("utf-8"))
                  
            with open(jsonFileName, 'w') as outfile:
               json.dump(obj, outfile)
               f=open(logFileName, "a+")
               f.write(get_timeStr() + " Write Complete\n")
               print("Write Complete")
               f.close()
            
         except ValueError: 
            f=open(logFileName, "a+")
            f.write(get_timeStr() + " Error while reading JSON\n")
            f.close()
      
      else:
         try:
            jsonObj = {}
            jsonObj[message.topic] = str(message.payload.decode("utf-8"))
            with open(jsonFileName, 'w') as outfile:
               json.dump(jsonObj, outfile)
               f=open(logFileName, "a+")
               f.write(get_timeStr() + " Write Complete\n")
               f.close()
               
         except ValueError: 
            f=open(logFileName, "a+")
            f.write(get_timeStr() + " Error while writing to JSON file\n")
            f.close()
   else:
      print("XML Topic")
      parsedJSON = ab.data(fromstring(str(message.payload.decode("utf-8"))))
      
      try:
         if os.path.isfile(jsonFileName):
            with open(jsonFileName, 'r') as jsonFile:
               obj = json.load(jsonFile)
         #print(parsedJSON)
         obj[str(message.topic)] = parsedJSON
         
         with open(jsonFileName, 'w') as outfile:
            json.dump(obj, outfile)
            
            f=open(logFileName, "a+")
            f.write(get_timeStr() + " Write Complete\n")
            print("Write Complete")
            f.close()
         
      except ValueError: 
         f=open(logFileName, "a+")
         f.write(get_timeStr() + " Error while reading JSON\n")
         f.close()

def on_connect(client, userdata, flags, rc):
   f=open(logFileName, "a+")
   f.write(get_timeStr() + " " + conn_codes[rc] + ". (code " + str(rc) + ")\n")
   f.close()
   client.subscribe(TOPICS)

def on_subscribe(client, userdata, mid, granted_qos):
   f=open(logFileName, "a+")
   f.write(get_timeStr() + " Successfuly subscribed to topic(s)\n")
   f.close()

def on_unsubscribe(client, userdata, mid):
   f=open(logFileName, "a+")
   f.write(get_timeStr() + " Unsubscribed from " + TOPIC + "\n")
   f.close()

def on_disconnect(client, userdata, rc):
   f=open(logFileName, "a+")

   if rc != 0:
      f.write(get_timeStr() + " Unexpected disconnection.\n")
   else:
      f.write(get_timeStr() + " Disconnected\n")
   f.close()

def on_log(client, userdata, level, buf):
   f=open(logFileName, "a+")
   f.write(get_timeStr() + " Log message: " + str(client) + " " + str(userdata) + " " + str(buf)  + "\n")
   f.close()

def get_timeStr():
   datetimeFormat = ConfigSectionMap("LOGGING")['datetimeformat']
   ts = time.localtime()
   timeStr = time.strftime(datetimeFormat , ts)
   return timeStr

if __name__ == "__main__":
   logPath = ConfigSectionMap("LOGGING")['logpath']
   JsonFilePath = ConfigSectionMap("GENERAL")['jsonfilepath']
   
   enableLogMsg = config.getboolean("LOGGING", "enablelogmsg")
   printMsg = config.getboolean("LOGGING", "printmsg")
   
   BROKER_ADDRESS = ConfigSectionMap("GENERAL")['ip']
   PORT = ConfigSectionMap("GENERAL")['port']
   clientId = ConfigSectionMap("GENERAL")['clientid']
   
   filename = os.path.splitext(__file__)[0]
   jsonFileName = JsonFilePath + filename + "-agent-data.json"
   logFileName = logPath + filename + ".log"
   
   conn_codes = [
      "Connection successful",
      "Connection refused - incorrect protocol version",
      "Connection refused - invalid client identifier",
      "Connection refused - server unavailable",
      "Connection refused - bad username or password",
      "Connection refused - not authorised"
   ]
      
   f=open(logFileName, "a+")   
   f.write(get_timeStr() + " Creating new instance.\n")
   client = mqtt.Client(clientId) 
   
   client.on_connect = on_connect
   client.on_message = on_message
   client.on_subscribe = on_subscribe
   client.on_unsubscribe = on_unsubscribe
   client.on_disconnect = on_disconnect
   
   if enableLogMsg:
      client.on_log = on_log
   
   f.write(get_timeStr() + " Connecting to broker: " + BROKER_ADDRESS + ":" + PORT + "\n")
   f.close()
   client.connect( BROKER_ADDRESS, int(PORT))
   
   client.loop_forever()
