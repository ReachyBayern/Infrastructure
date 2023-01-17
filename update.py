# script to update files:
# - Windows exe files
# - python scripts
# - handle windows services (start / stop) before updateing files
#   Windows Attention! The script has to be run under administrator account to stop and restart services OR run also as a service 

from shutil import copy2, rmtree
from subprocess import Popen
from subprocess import run
import sys
from time import sleep
import os, platform
from tqdm import tqdm
from lib_downloadFile import *
from lib_writeInifile import writeIniOption
from lib_readInifile  import readIniOption
import lib_readInifile
from pathlib import Path

debug           = False
loopUpdate      = 60 # seconds
l_runAsService  = False
download        = False
winService      = ""
fname           = ""
url             = ""
runType         = ""

if debug:
    #sys.argv.append('download=Frue')
    sys.argv.append('runAsService=True')
    #sys.argv.append('winService=MCA-Computer-Agent')
    sys.argv.append('loop=20')
    #sys.argv.append('runType=winService')
    #sys.argv.append('url=http://irgendwo.com')
    #sys.argv.append('fname=c:\services\mca\mca.exe')
    #sys.argv.append('--help')

def isInt(_i):
    try: 
        int(_i)
        return True
    except ValueError:
        return False

def get_parameter(_value, _argv, _argv_name, _argv_values):
    # _value        value of vurrent variable to check
    # _argv         current paramater
    # _argv_name    parameter name to be compared with
    # _argv_values  valid values of the parameter to be compared as a list
    _param = (_argv[0:len(_argv_name)])
    if _param.lower() == _argv_name.lower():                                                    # check if parameter belongs variable
        x = _argv.split("=",1)                                                                  
        if len(x) > 1:
            if len(_argv_values) > 0:                                                           # if values are given --> check if the value of the parameter is valid
                _result = _value                                                                # set default value in case nothing is found in the list
                for _eachValue in _argv_values.split(",",4):                                    # check the value against the valid parameter(s)
                    if _eachValue == x[1]:
                        _result = x[1]                                                          # set value with validation
                        print(f"found a match for value {_eachValue} in [{_argv_values}]")
            else:        
                _result = x[1]                                                                  # set value without a validation
        else:
            _result = True                                                                      # only a one word parameter without an '=' --> set to True
        print(f"{_argv_name}={_result}")    
    else:
        _result= _value                                                                         # nothing found, set the original value 
    match _result:                                                                              # special conversion in case of boolean or integer
        case 'True' | True:     _result = True
        case 'False' | False:   _result = False
        case _:                 
            if isInt(_result):                                                                  # check if it is an integer
                _result = int(_result)
            #else:    
            #    _result = _result

    return _result

# if parameter runAsService is set, it loops everlasting
try:
    if len(sys.argv) > 1:
        for cc in range(1, len(sys.argv)):
            l_runAsService  = get_parameter(l_runAsService  , sys.argv[cc], 'runAsService',"")
            loopUpdate      = get_parameter(loopUpdate      , sys.argv[cc], 'loop',"")
            winService      = get_parameter(winService      , sys.argv[cc], 'winService',"")
            fname           = get_parameter(fname           , sys.argv[cc], 'fname',"")
            url             = get_parameter(url             , sys.argv[cc], 'url',"")
            download        = get_parameter(winService      , sys.argv[cc], 'download',"")
            runType         = get_parameter(runType         , sys.argv[cc], 'runType',"none,winService,winExe,python")
            if sys.argv[cc] == "?" or sys.argv[cc].lower() == "--help":
                    print(f"HELP:")
                    print(f"Use the follwoing options:")
                    print(f"runAsService                to run in a loop of {loopUpdate} seconds")
                    print(f"loop=number                 to set the loop interval in seconds")
                    print(f"fname=FILEPATH              file name incl. path of the file to be updated")
                    print(f"url=FILEPATH or HTTP-url    file name incl. path of the new file to download or to copy")
                    print(f"download=true               force to start the update process")
                    print(f"winservice=                 this is the name of the Windows service of the main programm to be able stop and start it")
                    print(f"runtype=                    this defines the mode how the updater is running:")
                    print(f"                             - none:        only download, but no restart iof the main programm")
                    print(f"                             - winService:  the updater stops and restarts an Windows service of the main programm")
                    print(f"                             - winExe:      updater kills a running main program and restarts it for the updateing process")
                    print(f"                             - python:      the updater downloads a new main programm and overwrites the original code, no restart")
                    exit()
except:        
        exit()
finally:  
    print("")  

folder = os.getcwd() 
uname = platform.uname() 
if uname.system == 'Windows':
    config_file = Path(folder  + "\config.ini") 
else:
    config_file = Path(folder  + "/config.ini") 

counter = 0
while counter < 1:
    winService  = readIniOption(config_file,'DOWNLOAD','winservice')
    if readIniOption(config_file,'DOWNLOAD','download').lower() == 'true':
        download = True
    else:
        download = False    
    url         = readIniOption(config_file,'DOWNLOAD','url')
    runType     = readIniOption(config_file,'DOWNLOAD','runtype') #
    fname       = readIniOption(config_file,'DOWNLOAD','fname')

    # get parameters again after reading ini (parameters have more priority!)
    try:
        if len(sys.argv) > 1:
            for cc in range(1, len(sys.argv)):
                winService      = get_parameter(winService      , sys.argv[cc], 'winService',"")
                download        = get_parameter(download        , sys.argv[cc], 'download',"")
                url             = get_parameter(url             , sys.argv[cc], 'url',"")                
                runType         = get_parameter(runType         , sys.argv[cc], 'runType',"none,winService,winExe,python")
                fname           = get_parameter(fname           , sys.argv[cc], 'fname',"")
    except:        
        exit()
    finally:  
        print("")  

    a = 0
    if download == True:
        # do the update
        # if it's an windows service, stop it
        match runType:
            case "winService":
                # stop the service
                print(f"Stopping windows service {winService}")
                args = ['sc', 'stop', winService]
                try:
                    result = run(args)
                except:    
                    print(f"Somthing went wrong: {result}")
                args = ['sc', 'query', winService,'| FIND \"STATE\" | FIND \"STOPPED\""']    
                result = ""
                l_result = 0
                while result =="":
                    try:
                        result = run(args)
                    except:
                        l_result = 1
                    finally:    
                        print(f"Waiting for stopping the service {winService}")
                        sleep(1)    
                print(f"Service is stopped now.")
            case "winExe":
                print(f"please stop {fname}")
        l_result = update_file(fname, url)
        sleep(1)
        if l_result == 0:
            writeIniOption(config_file,'DOWNLOAD','download', 'False')
        else:    
            print("Somthing went wrong during update. Update option is still active!") 
            l_result = 0

        # restart the updated program/script/service
        match runType:
            case "none":
                print(f"Nothing to restart.")
            case "winService":
                print(f"Restart windows service {winService}")
                args = ['sc', 'start', winService]
                result = subprocess.run(args)
            case "winExe":
                print(f"Restart windows exe file {fname}")   
                Popen(fname, shell=True) 
                #os.system(fname)
            case "python"    :
                print(f"Restart python script {fname}")
                #os.system(f"python {fname}")
                Popen(f"python {fname}", shell=True)
            case other:
                print(f"No or wrong restart option given!")   
    else:
        print("No update is requested (config.ini: download = false). Waiting a while and check again")
        l_result = 0
    if l_result == 0:
        print("Update process has ended....")
    else:
        print("Somthing went wrong during update!")    
    if l_runAsService == False:
        counter = 99
    else:    
        print (f"Waiting for {loopUpdate} seconds......")
        for i in tqdm(range(int(loopUpdate))):
            sleep( 1 )
    #exit("Update process has ended....")




