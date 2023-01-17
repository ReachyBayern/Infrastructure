# Write a new ini file or check only missing entries
import configparser, os, platform
from pathlib import Path
# default values:
#MQTT
d_mqtt_topic_prefix   = "client/" 
d_broker_address      = "CNAME of the server-cert"      # this must match the CNAME in your server-cert!
d_broker_port         = "8883" 
d_mqtt_alias          = "NewDevice"
#SSL
d_ca_crt              = "resources\CA.crt"
d_client_crt          = "resources\client.crt"
d_client_key          = "resources\client.key"
#DOWNLOAD
d_url                 = "UPDATE_SOURCE_FILE" 
d_fname               = "UPDATE_DESTINATION_FILE" 
d_download            = "False"                         # True or False
d_runtype             = "winService"                    # none, winService, python, WinExe
d_winservice          = "MCA-Service-Agent"
#GENERAL
d_runasservice        = "False"
d_loopduration        = "3530"                          # seconds for the Windows service loop

def writeIniOption(l_inifile, l_section, l_option, l_value):
    config = configparser.ConfigParser()
    config.read(l_inifile)
    if not config.has_section(l_section):
           config.add_section(l_section)
    config.set(l_section,l_option,l_value)
    with open(l_inifile, 'w') as configfile:
         config.write(configfile)

# Write Ini file 
folder = os.getcwd() 
uname = platform.uname() 

# check which os is used because of different delemiters
if uname.system == 'Windows':
    config_file = Path(folder  + "\config.ini") 
else:
    config_file = Path(folder  + "/config.ini") # linux needs "/" and Synology needs complete path!    

config = configparser.ConfigParser()		
if not config_file.is_file():
    # create a inital inifile
    config['MQTT'] = {}
    with open(config_file, 'w') as configfile: 
         config.write(configfile)

if config_file.is_file():
    # check inifile and add missing sections/options    
    print(f"Just checking if all ini entries...")
    config.read(config_file)

    # Section MQTT:
    if not config.has_section('MQTT'):
           config.add_section('MQTT')
    if not config.has_option('MQTT','mqtt_topic_prefix'):
                  config.set('MQTT','mqtt_topic_prefix',d_mqtt_topic_prefix)
    if not config.has_option('MQTT','broker_address'):
                  config.set('MQTT','broker_address',d_broker_address)
    if not config.has_option('MQTT','broker_port'):
                  config.set('MQTT','broker_port',d_broker_port)
    if not config.has_option('MQTT','mqtt_alias'):
                  config.set('MQTT','mqtt_alias',d_mqtt_alias)

    # Section MQTT:
    if not config.has_section('SSL'):
           config.add_section('SSL')
    if not config.has_option('SSL','ca_crt'):
                  config.set('SSL','ca_crt',d_ca_crt)
    if not config.has_option('SSL','client_crt'):                  
                  config.set('SSL','client_crt',d_client_crt)
    if not config.has_option('SSL','client_key'):                  
                  config.set('SSL','client_key',d_client_key)
    # Section DOWNLOAD
    if not config.has_section('DOWNLOAD'):
           config.add_section('DOWNLOAD')   
    if not config.has_option('DOWNLOAD','url'):
                  config.set('DOWNLOAD','url',d_url)
    if not config.has_option('DOWNLOAD','fname'):
                  config.set('DOWNLOAD','fname',d_fname)                  
    if not config.has_option('DOWNLOAD','download'):
                  config.set('DOWNLOAD','download',d_download)
    if not config.has_option('DOWNLOAD','runtype'):
                  config.set('DOWNLOAD','runtype',d_runtype)
    if not config.has_option('DOWNLOAD','winservice'):
                  config.set('DOWNLOAD','winservice',d_winservice)

    # Section GENERAL
    if not config.has_section('GENERAL'):
           config.add_section('GENERAL')   
    if not config.has_option('GENERAL','runasservice'):
                  config.set('GENERAL','runasservice',d_runasservice)
    if not config.has_option('GENERAL','loopduration'):
                  config.set('GENERAL','loopduration',d_loopduration)                  

    #finally save it              
    with open(config_file, 'w') as configfile: 
            config.write(configfile)                
else:
    print(f"Somthing went wrong during creating the default config.ini")        

    