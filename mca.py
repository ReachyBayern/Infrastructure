######################################################################################################################
#  MQTT-Agent to collect information of computers which should be supported                                          #
#                                                                                                                    #
#  Data are sent to a MQTT-Broker who can take this informations for further processing                              #
#                                                                                                                    #
#  This is the first part to bring data into SnipeIT without direct connection to that system                        #
######################################################################################################################
# Download current version with Windows: curl -o C:\Skripte\mca2.py https://raw.githubusercontent.com/ReachyBayern/MCA/main/mca.py
# Download current version with linux: wget -O /path/mca2.py https://raw.githubusercontent.com/ReachyBayern/MCA/main/mca.py  
# windows task planer action with minimized window:
#  program: cmd
#  argumnents: /c start /min C:\Users\info\AppData\Local\Microsoft\WindowsApps\python.exe C:\Users\path\mca.py
#  execute in: C:\Users\path\

import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import sys
import time
import datetime
import psutil
import platform
import GPUtil
import os
from datetime import datetime
import subprocess  
import ssl, inspect
import math
import requests, enlighten
from config import *

######################################################################################################################
print (f"Download latest version from {url}.....")
MANAGER = enlighten.get_manager()
r = requests.get(url, stream = True)
assert r.status_code == 200, r.status_code
dlen = int(r.headers.get('Content-Length', '0')) or None

with MANAGER.counter(color = 'green', total = dlen and math.ceil(dlen / 2 ** 20), unit = 'MiB', leave = False) as ctr, \
     open(fname, 'wb', buffering = 2 ** 24) as f:
    for chunk in r.iter_content(chunk_size = 2 ** 20):
        print(chunk[-16:].hex().upper())
        f.write(chunk)
        ctr.update()
print (f" ")
######################################################################################################################
uname = platform.uname()
rev = "20230109.225400"

# declaration
mqtt_topic = mqtt_topic_prefix + uname.system + "/" + uname.node + "/" 
global jsondata
jsondata = ""

print(f"Starting fetching information....")
######################################################################################################################
# set präfix
print(f"Get general information")
jsondata  = '{ "d": {'
# open section Sys Info
if uname.version[0:7] == '10.0.22' and uname.system == 'Windows': # Windows 11 is just a second build, no separate version
    operatingsystem ="11"
else:
    operatingsystem = uname.release   
print(f"{operatingsystem}")     
jsondata += '"SYSINFO": {'
jsondata += '"hostname":"'              + str(uname.node)                            +  '"' 
jsondata += ',"system":"'               + str(uname.system)                          +  '"'
jsondata += ',"release":"'              + str(operatingsystem)                       +  '"'
jsondata += ',"os":"'                   + str(uname.system)                          +  ' '  + operatingsystem + '"'
jsondata += ',"version":"'              + str(uname.version)                         +  '"'
jsondata += ',"machine":"'              + str(uname.machine)                         +  '"'
jsondata += ',"processor":"'            + str(uname.processor)                       +  '"'
jsondata += ',"currentUser":"'          + str(os.getlogin())                         +  '"'
jsondata += ',"revision":"'             + str(rev)                                   +  '"'

boot_time_timestamp = psutil.boot_time()
bt = datetime.fromtimestamp(boot_time_timestamp)
jsondata += ',"bootTime":"'            + str(bt)                                     +  '"'
jsondata += ' } ' 
# close section Sys Info  
######################################################################################################################
# open section CPU
print(f"Get CPU information")
jsondata += ',"CPU": {'
jsondata += '"actualCores":"'         + str(psutil.cpu_count(logical=False))         +  '"'
jsondata += ',"logicalCores":"'        + str(psutil.cpu_count(logical=True))         +  '"'
jsondata += ',"maxFrequency":"'        + str(psutil.cpu_freq().max)                  +  'MHz"'
jsondata += ',"currentFrequency":"'    + str(psutil.cpu_freq().current)              +  'MHz"'
jsondata += ',"cpuUsage":"'            + str(psutil.cpu_percent())                   +  '%"'
for i, perc in enumerate(psutil.cpu_percent(percpu=True, interval=1)):
    jsondata += ',"Core ' + str(i) + '":"'            + str(perc)                    +  '%"'
jsondata += ' } ' 
# close section CPU
######################################################################################################################
# open section RAM
print(f"Get RAM information")
def adjust_size(size):
    factor = 1024
    for i in ["B", "KB", "MB", "GB", "TB"]:
        if size > factor:
            size = size / factor
        else:
            return f"{size:.3f}{i}"
virtual_mem = psutil.virtual_memory()
jsondata += ',"RAM": {'
jsondata += '"totalRam":"'               + str(adjust_size(virtual_mem.total))      +  '"'
jsondata += ',"availableRam":"'          + str(adjust_size(virtual_mem.available))  +  '"'
jsondata += ',"usedRam":"'               + str(adjust_size(virtual_mem.used))       +  '"'
jsondata += ',"percentageRam":"'         + str(virtual_mem.percent)                 +  '%"'
jsondata += ' } ' 
# close section RAM
######################################################################################################################
# open section SWAP
print(f"Get SWAP information")
swap = psutil.swap_memory()
jsondata += ',"SWAP": {'
jsondata += '"totalSwap":"'              + str(adjust_size(swap.total))             +  '"'
jsondata += ',"freeSwap":"'              + str(adjust_size(swap.free))              +  '"'
jsondata += ',"usedSwap":"'              + str(adjust_size(swap.used))              +  '"'
jsondata += ',"percentageSwap":"'        + str(swap.percent)                        +  '%"'
jsondata += ' } ' 
# close section SWAP
######################################################################################################################
# open section DISK
print(f"Get DISK information")
partitions = psutil.disk_partitions()
jsondata += ',"DISK": {'
for p in partitions:
    #lw = str(p.device).replace('\\','')
    jsondata += '"' + str(p.device).replace('\\','') + '": {'
    jsondata += '"fileSystemType":"'             + str(p.fstype)                              +  '"'
    try:
        partition_usage = psutil.disk_usage(p.mountpoint)
    except PermissionError:
        continue
    finally:
        jsondata += ',"totalSize":"'                 + str(adjust_size(partition_usage.total))    +  '"'
        jsondata += ',"usedSize":"'                  + str(adjust_size(partition_usage.used))     +  '"'
        jsondata += ',"freeSize":"'                  + str(adjust_size(partition_usage.free))     +  '"'
        jsondata += ',"percentageSize":"'            + str(partition_usage.percent)  +  '%"'
        jsondata += ' } ,'     
jsondata = jsondata.strip(',') + "} "  
# close section DISK
######################################################################################################################
# open section GPU
print(f"Get GPU information")
jsondata += ',"GPU": {'
gpus = GPUtil.getGPUs()
for gpu in gpus:
    print(f"ID: {gpu.id}, Name: {gpu.name}")
    jsondata += '"' + str(gpu.id) + '": {'
    jsondata += '"load":"'                      + str(gpu.load*100)                         +  '%"'
    jsondata += ',"freeMem":"'                  + str(uname.gpu.memoryFree)                 +  'MB"'
    jsondata += ',"usedMem":"'                  + str(uname.gpu.memoryUsed)                 +  'MB"'
    jsondata += ',"totalMem":"'                 + str(uname.gpu.memoryTotal)                +  'MB"'
    jsondata += ',"temperature":"'              + str(uname.gpu.temperature)                +  '°C"'
    jsondata += ' } ,'
#jsondata = outStr = jsondata[:len(jsondata)-1] + '} '
jsondata = jsondata.strip(',') + "} "      
# close section GPU
######################################################################################################################
# open section NETWORK
print(f"Get network information")
jsondata += ',"NETWORK": {'
if_addrs = psutil.net_if_addrs()
for interface_name, interface_addresses in if_addrs.items():
    #jsondata += '"' + str(interface_name) + '": {'
    for address in interface_addresses:
#         jsondata += '"' + str(interface_name) + '": {'
         if str(address.family) == 'AddressFamily.AF_INET':
             jsondata += '"' + str(interface_name) + '": {'
             jsondata += '"ipAddress":"'        + str(address.address)                       +  '"'
             jsondata += ',"netmask":"'         + str(address.netmask)                       +  '"'
             jsondata += ',"broadcastIp":"'    + str(address.broadcast)                     +  '"'
             if psutil.net_if_addrs()[interface_name][0].address:
                mac = str(psutil.net_if_addrs()[interface_name][0].address)
                if mac.find("-",1) >= 0:
                    jsondata += ',"macAddress":"'  + str(mac)                               +  '"'    
             jsondata += ' } ,'
         elif str(address.family) == 'AddressFamily.AF_PACKET':
             jsondata += '"' + str(interface_name) + '": {'
             jsondata += '"macaddress":"'       + str(address.address)                       +  '"'
             jsondata += ',"netmask":"'         + str(address.netmask)                       +  '"'
             jsondata += ',"broadcastMac":"'    + str(address.broadcast)                     +  '"'
             jsondata += ' } ,'
    #jsondata += ' } ,'         
net_io = psutil.net_io_counters()
jsondata += '"totalByteSent":"'                 + str(adjust_size(net_io.bytes_sent))        +  '"'
jsondata += ',"totalBytesReceived":"'           + str(adjust_size(net_io.bytes_recv))        +  '"'
jsondata = jsondata.strip(',') + "} "  
# close section NETWORK
######################################################################################################################
# open section installed programs
print(f"Get installed programs")
count = 0
jsondata += ',"PROGRAM": {'
if uname.system == 'Windows':
    Data = subprocess.check_output(['wmic', 'product', 'get', 'name']) 
    a = str(Data) 
    try: 
        for i in range(len(a)):
            prog = str(a.split("\\r\\r\\n")[6:][i]).replace('\\','-').strip(' ')
            if len(prog) > 1:
                if len(prog.replace(' ','')) > 0: # eleminate only BLANKS in the program name
                    count += 1
                    print(f"prog-ID{count}: {prog}")
                jsondata += '"progID-' + str(count) + '":"'       + str(prog)                       +  '",' 
    except IndexError as e: 
        print("Done")
jsondata = jsondata.strip(',') + "}, " 
# close section installed programs
######################################################################################################################
# open section
jsondata += '"BLUESCREENS": {'
if uname.system == 'Windows':
    try:
        for (root,dirs,files) in os.walk('C:\Windows\Minidump/'):
            print("Root:" + str(root))
            #print("Verzeichnisse: " + str(dirs))
            print("Dateien: " + str(files))
        #print(*files, sep=", ")    
        index=0
        if 'files' in locals():
            for file in files:
                print(f"{files[index]}")
                jsondata += '"ID-' + str(index) + '":"'        + str(files[index])                       +  '",'
                index += 1
    except IndexError as e: 
        print("")
jsondata = jsondata.strip(',') + "}, " 
# close section


######################################################################################################################
# open section
#jsondata += '"PROGRAM": {'
#  jsondata += '"' + str(interface_name) + '": {'
#  jsondata += ',"totalBytesReceived":"'           + str(adjust_size(net_io.bytes_recv))        +  '"'
#  jsondata += ' } ,'
#jsondata = jsondata.strip(',') + "}, " 
# close section
######################################################################################################################    


# close jsondata
now = datetime.now() 
jsondata += '"executionTime":"' + now.strftime("%d.%m.%Y %H:%M:%S") + '"} }'
#jsondata = jsondata.strip(',') + "} }"

######################################################################################################################    

# send data via MQTT
#publish.single(mqtt_topic, payload=jsondata, qos=0, retain=False, hostname=mqtt_broker_ip,
#  port=mqtt_broker_port, client_id="", keepalive=60, will=None, auth=None, tls=None,
#  protocol=mqtt.MQTTv311, transport="tcp")


def on_message(client, userdata, message):
    print("message received "   + str(message.payload.decode("utf-8")))
    print("message topic="      + str(message.topic))
    print("message qos="        + str(message.qos))
    print("message retain flag=" + str(message.retain))

client = mqtt.Client( "mqttclient" )
print( "connecting to broker" )
client.tls_set(CA_crt, client_crt, client_key, tls_version=ssl.PROTOCOL_TLSv1_2)
client.tls_insecure_set(False)
client.connect( broker_address, broker_port, 60 )
client.loop_start()

print( "Subscribing to topic", mqtt_topic )
client.on_message=on_message
client.subscribe( mqtt_topic )

for i in range( 1, 2 ):
    #print( jsondata , mqtt_topic )
    client.publish( mqtt_topic, jsondata )
    time.sleep( 1 )

client.loop_stop()

print( "Goodbye!" )



""" ######################################################################################################################    
print("-"*90)
print(f"{jsondata}")
print("-"*90)

print("-"*40, "Sys Info", "-"*40)
#uname = platform.uname()
print(f"System: {uname.system}")
print(f"Node Name: {uname.node}")
print(f"Release: {uname.release}")
print(f"Version: {uname.version}")
print(f"Machine: {uname.machine}")
print(f"Processor: {uname.processor}")
print(f"Username: {os.getlogin()}")

print("-"*40, "Boot Time", "-"*40)
print(f"Boot Time: {bt.day}.{bt.month}.{bt.year} {bt.hour}:{bt.minute}:{bt.second}")

print("-"*40, "CPU Info", "-"*40)
print("Actual Cores:", psutil.cpu_count(logical=False))
print("Logical Cores:", psutil.cpu_count(logical=True))
print(f"Max Frequency: {psutil.cpu_freq().max:.1f}Mhz")
print(f"Current Frequency: {psutil.cpu_freq().current:.1f}Mhz")
print(f"CPU Usage: {psutil.cpu_percent()}%")
print("CPU Usage/Core:")
for i, perc in enumerate(psutil.cpu_percent(percpu=True, interval=1)):
    print(f"Core {i}: {perc}%")

def adjust_size(size):
    factor = 1024
    for i in ["B", "KiB", "MiB", "GiB", "TiB"]:
        if size > factor:
            size = size / factor
        else:
            return f"{size:.3f}{i}"

print("-"*40, "RAM Info", "-"*40)
#virtual_mem = psutil.virtual_memory()
print(f"Total: {adjust_size(virtual_mem.total)}")
print(f"Available: {adjust_size(virtual_mem.available)}")
print(f"Used: {adjust_size(virtual_mem.used)}")
print(f"Percentage: {virtual_mem.percent}%")
print("-"*40, "SWAP", "-"*40)
#swap = psutil.swap_memory()
print(f"Total: {adjust_size(swap.total)}")
print(f"Free: {adjust_size(swap.free)}")
print(f"Used: {adjust_size(swap.used)}")
print(f"Percentage: {swap.percent}%")

print("-"*40, "Disk Information", "-"*40)
#partitions = psutil.disk_partitions()
for p in partitions:
    print(f"Device: {p.device}")
    print(f"\tMountpoint: {p.mountpoint}")
    print(f"\tFile system type: {p.fstype}")
    try:
        partition_usage = psutil.disk_usage(p.mountpoint)
    except PermissionError:
        continue
    print(f"  Total Size: {adjust_size(partition_usage.total)}")
    print(f"  Used: {adjust_size(partition_usage.used)}")
    print(f"  Free: {adjust_size(partition_usage.free)}")
    print(f"  Percentage: {partition_usage.percent}%")
disk_io = psutil.disk_io_counters()
print(f"Read since boot: {adjust_size(disk_io.read_bytes)}")
print(f"Written since boot: {adjust_size(disk_io.write_bytes)}")

print("-"*40, "GPU Details", "-"*40)
#import GPUtil
#gpus = GPUtil.getGPUs()
for gpu in gpus:
    print(f"ID: {gpu.id}, Name: {gpu.name}")
    print(f"\tLoad: {gpu.load*100}%")
    print(f"\tFree Mem: {gpu.memoryFree}MB")
    print(f"\tUsed Mem: {gpu.memoryUsed}MB")
    print(f"\tTotal Mem: {gpu.memoryTotal}MB")
    print(f"\tTemperature: {gpu.temperature} °C")

print("-"*40, "Network Information", "-"*40)
#if_addrs = psutil.net_if_addrs()
for interface_name, interface_addresses in if_addrs.items():
    for address in interface_addresses:
        print(f"Interface: {interface_name}")
        if str(address.family) == 'AddressFamily.AF_INET':
            print(f"  IP Address: {address.address}")
            print(f"  Netmask: {address.netmask}")
            print(f"  Broadcast IP: {address.broadcast}")
            if psutil.net_if_addrs()[interface_name][0].address:
                mac = str(psutil.net_if_addrs()[interface_name][0].address)
                if mac.find("-",1) >= 0:
                    print(f"  MAC: {mac}")
        elif str(address.family) == 'AddressFamily.AF_PACKET':
            print(f"  MAC Address: {address.address}")
            print(f"  Netmask: {address.netmask}")
            print(f"  Broadcast MAC: {address.broadcast}")
        print("-"*90)    
#net_io = psutil.net_io_counters()
print(f"Total Bytes Sent: {adjust_size(net_io.bytes_sent)}")
print(f"Total Bytes Received: {adjust_size(net_io.bytes_recv)}")

#python -c "help('modules')" """