from stat import *
import os
import time
import hashlib
import sys


#
# Genera un resumen md5 del archivo pasado por argumento
#
def md5_checksum(filename, blocksize=65536):
    
    hasher = hashlib.md5()
    fd = open(filename, "rb")

    buf = fd.read(blocksize)
    while len(buf) > 0:
        hasher.update(buf)
        buf = fd.read(blocksize)

    fd.close()
    return hasher.hexdigest()

