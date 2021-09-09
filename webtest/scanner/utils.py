import hashlib
import os
def sha256sum(fileDir):
    h  = hashlib.sha256()
    b  = bytearray(128*1024)
    mv = memoryview(b)
    with open(fileDir, 'rb', buffering=0) as f:
        for n in iter(lambda : f.readinto(mv), 0):
            h.update(mv[:n])
    return h.hexdigest()
# fileDir = 'C:\\Users\\shufa\\Desktop\\webtest\\files\\newegg_magecart_skimmer - copy.js'
# sha = sha256sum(fileDir)
# # os.remove(fileDir)
# print(sha)