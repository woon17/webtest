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
# env_path = Path('.')
# load_dotenv(dotenv_path=env_path)
api_key = os.getenv("KEY")

def getId(fileDir):
    f = open(fileDir, 'rb')
    file = {"file":(fileDir, f)}
    resp = requests.post('https://www.virustotal.com/api/v3/files', files=file, headers={'X-Apikey': api_key})
    f.close()
    os.remove(fileDir)

    print(f'resp: {resp.json()}')
    return resp.json()['data']['id']

def getDataService(fileName):
    print('--------------------------------------------------------------------------------------------------------------------')
    print(f'file: {fileName}')
    fileDir = os.path.join(baseDir, "temp", fileName)
    print(f'fileDir: {fileDir}')
    hashPre = sha256sum(fileDir)
    print(f"hashPre: {hashPre}")
    reportObj=Report.objects.filter(hash=hashPre)
    if reportObj.exists():
        print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        stats = ast.literal_eval(reportObj[0].stats)
        print(f'stats: {stats}; {type(stats)}')
        redirectUrl = "https://www.virustotal.com/gui/file/" +reportObj[0].hash
        os.remove(fileDir)
        return {'stats': stats, 
            'redirectUrl': redirectUrl, 'status': 'completed'}

    id=getId(fileDir)

    resp2 = requests.get('https://www.virustotal.com/api/v3/analyses/{}'.format(id), headers={'x-apikey': api_key,
                                            'Accept': 'application/json'})
    print("********************************************************************************************")
    print(resp2.json())


    print(f'resp2: {resp2}')
    print(f'resp2: {resp2.json().keys()}')
    stats=resp2.json()['data']['attributes']['stats']
    status=resp2.json()['data']['attributes']['status']

    hash= resp2.json()['data']['links']['item'].split('api/v3/files/')[1]
    redirectUrl = "https://www.virustotal.com/gui/file/" + hash
    '''
    "stats":{
        "harmless":0,
        "type-unsupported":16, ->"category":"type-unsupported"
        "suspicious":0,
        "confirmed-timeout":0,
        "timeout":0,
        "failure":0,
        "malicious":0, ->"result":"None"
        "undetected":57 ->"category":"undetected",
    }
    '''
    print(stats)
    malicious = stats['malicious']
    print(f'malicious: {malicious}')
    print(int(malicious))
    print(f'id: {id}')
    print(f'hash: {hash}')
    print(f'status: {status}')
    print(status == "completed")
    if status == "completed":
        Report.objects.create(
            reportId=id,
            stats=stats,
            hash=hash,
            file=fileName
        )

    print(f'stats: {stats}; {type(stats)}')
    print(f'status: {status}')

    return {'stats': stats, 
            'redirectUrl': redirectUrl, 'status': status}
