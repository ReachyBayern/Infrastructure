# Dowloading from an url or copying from an file system
# the script checks if the source starts with "http" to determin if its an download or a copy request

import subprocess, enlighten, requests, math
from shutil import copy2, rmtree

def update_file(fname, url):
    type = url[0:4]
    result = 0
    match type:
        case "http":
            # Downloading from an URL
            try:
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
            except:    
                print("An error occured during downloading!")
            finally:
                #do somthing always
                print("Download process has ended")
        case other:
            #copying from file system
            try:
                print(f"Starting downloading {url}. Please wait... ")
                copy2(url, fname) # copy file
            except:
                print("An error occured druing copying!")
                result = 1    
            finally:
                print("Download process has ended")
                result = 0
    return result