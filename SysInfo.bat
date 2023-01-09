rem copy \\192.168.5.222\smarthome\Tools\Endpoint-Communication-Agent\mca.py c:\Skripte\ /Y
rem Download current version from GITHUB with Windows: 
curl -o C:\Skripte\mca.py https://raw.githubusercontent.com/ReachyBayern/MCA/main/mca.py
rem curl -o C:\Skripte\SysInfo.bat https://raw.githubusercontent.com/ReachyBayern/MCA/main/SysInfo.bat
cd c:\Skripte
python3 C:\Skripte\mca.py