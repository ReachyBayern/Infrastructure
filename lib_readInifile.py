# Read Ini file 
import configparser, os, platform
from pathlib import Path

def readIniOption(l_inifile, l_section, l_option):
    l_config = configparser.ConfigParser()
    l_config.read(l_inifile)
    if l_config.has_option(l_section,l_option):
        return l_config.get(l_section,l_option)
    
folder = os.getcwd() 
uname = platform.uname() 

if uname.system == 'Windows':
    config_file = Path(folder  + "\config.ini") 
else:
    config_file = Path(folder  + "/config.ini") 

if config_file.is_file():
    config = configparser.ConfigParser()		
    config.read(config_file)
    conf_mqtt           = config['MQTT']
    conf_ssl            = config['SSL']
    conf_dl             = config['DOWNLOAD']
    conf_gen            = config['GENERAL']

    #[MQTT]
    broker_address      = conf_mqtt['broker_address']
    broker_port         = int(conf_mqtt['broker_port'])
    mqtt_topic_prefix   = conf_mqtt['mqtt_topic_prefix']
    mqtt_alias          = conf_mqtt['mqtt_alias']

    #[SSL] 
    CA_crt              = conf_ssl['CA_crt']
    client_crt          = conf_ssl['client_crt']
    client_key          = conf_ssl['client_key']

    #[DOWNLOAD]
    url                 = conf_dl['url']
    fname               = conf_dl['fname']
    download            = conf_dl['download']
    runType             = conf_dl['runType']
    winService          = conf_dl['winService']

    #[GENERAL]
    runAsService        = conf_gen['runAsService']
    loopDuration        = int(conf_gen['loopDuration'])
else:
    print(f'config.ini is missing. Please add a config.ini!! Default values are set')
    exit('config.ini is missing. Please add a config.ini!! Default values are set')   