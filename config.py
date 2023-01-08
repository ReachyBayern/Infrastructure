mqtt_broker_ip   = "host"
mqtt_broker_port = 1883
#mqtt_broker_ip   = "host" # extern
#mqtt_broker_port = 1883            # extern
mqtt_broker_url  = "http://" + mqtt_broker_ip + ":" + str(mqtt_broker_port)
mqtt_topic_prefix= "client/" 
#mqtt_topic_prefix= "Server/" 

broker_address="yourhost.myfritz.net" # this must match the CNAME in your server-cert!
broker_port=8883

#SSL / certificate
CA_crt     = "resources\CA.crt"
client_crt = "resources\client.crt"
client_key = "resources\client.key"