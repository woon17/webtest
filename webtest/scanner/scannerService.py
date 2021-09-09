from dotenv import load_dotenv
from pathlib import Path
import os
import requests
import json
import ast
from .models import Report
import sys
from .utils import sha256sum
sys.path.append(".")
from webtest.settings import BASE_DIR as baseDir
load_dotenv()
api_key = os.getenv("KEY")

def getId(fileDir):
    f = open(fileDir, 'rb')
    file = {"file":(fileDir, f)}
    resp = requests.post('https://www.virustotal.com/api/v3/files', files=file, headers={'X-Apikey': api_key})
    f.close()
    os.remove(fileDir)
    return resp.json()['data']['id']

def getDataService(fileName):
    fileDir = os.path.join(baseDir, "temp", fileName)
    hashPre = sha256sum(fileDir)
    reportObj=Report.objects.filter(hash=hashPre)
    if reportObj.exists():
        stats = ast.literal_eval(reportObj[0].stats)
        redirectUrl = "https://www.virustotal.com/gui/file/" +reportObj[0].hash
        os.remove(fileDir)
        return {'stats': stats, 
            'redirectUrl': redirectUrl, 'status': 'completed'}

    id=getId(fileDir)
    resp2 = requests.get('https://www.virustotal.com/api/v3/analyses/{}'.format(id), headers={'x-apikey': api_key,
                                            'Accept': 'application/json'})
    stats=resp2.json()['data']['attributes']['stats']
    status=resp2.json()['data']['attributes']['status']

    hash= resp2.json()['data']['links']['item'].split('api/v3/files/')[1]
    redirectUrl = "https://www.virustotal.com/gui/file/" + hash
    '''
    "stats":{
        "harmless":0,
        "type-unsupported":16,
        "suspicious":0,
        "confirmed-timeout":0,
        "timeout":0,
        "failure":0,
        "malicious":0,
        "undetected":57
    }
    '''
    if status == "completed":
        Report.objects.create(
            reportId=id,
            stats=stats,
            hash=hash,
            file=fileName
        )
    return {'stats': stats, 
            'redirectUrl': redirectUrl, 'status': status}

