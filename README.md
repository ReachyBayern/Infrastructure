# MCA (MQTT computer agent)
This script collects many information of the computer and send it to a MQTT broker. The main reason for this script is to send this information
for inventory purposes to a asset management system. But not directly. The idea is to have a MQTT broker in a DMZ to collect data from everywhere but without
a direct connection to the productiv database. The next step is to have a broker script (internally, not in DMZ)  which read the inforamtion from the MQTT-broker.
And this script runs on Windows and on linux machines.
The broker script will be the next step. coming soon....
