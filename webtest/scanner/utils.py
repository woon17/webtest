import hashlib
import os
from webtest.settings import BASE_DIR as baseDir

def getSha256(fileDir):
    h  = hashlib.sha256()
    b  = bytearray(128*1024)
    mv = memoryview(b)
    with open(fileDir, 'rb', buffering=0) as f:
        for n in iter(lambda : f.readinto(mv), 0):
            h.update(mv[:n])
    return h.hexdigest()

def clearFile(fileName):
    filePath = os.path.join(baseDir, "temp", fileName)
    if os.path.exists(filePath):
        os.remove(filePath)