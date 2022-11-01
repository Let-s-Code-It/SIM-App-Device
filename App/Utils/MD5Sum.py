import glob
from pathlib import Path
import hashlib
import os

from ...Config import __APPLICATION_PATH__, __APPLICATION_MD5SUM__

def MD5Sum():

    fp = open(__APPLICATION_MD5SUM__, 'w')

    dir_path = r'App/**'
    for file in glob.glob(dir_path, recursive=True):
        if(Path(file).is_file()):
            if not "__pycache__" in file:
                with open(file, 'rb') as file_to_check:
                    data = file_to_check.read()    
                    md5_returned = hashlib.md5(data).hexdigest()
                    print("MD5: " + file + " -> " + md5_returned)
                    fp.write(file+":"+md5_returned+"\n")
    fp.close()