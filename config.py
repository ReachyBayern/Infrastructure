#MQTT configuration
mqtt_topic_prefix= "client/" 
#mqtt_topic_prefix= "Server/" 
broker_address="yourhost.myfritz.net" # this must match the CNAME in your server-cert!
broker_port=8883
mqtt_alias= "alias-topic-name"

#SSL / certificate from MQTT
CA_crt     = "resources\CA.crt"
client_crt = "resources\client.crt"
client_key = "resources\client.key"
download = False

# Download latest version from 'url' and save as 'fname'
url = 'https://raw.githubusercontent.com/ReachyBayern/MCA/main/mca.py'
fname = 'c:/skripte/mca2.py'