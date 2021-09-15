from dotenv import load_dotenv
from pathlib import Path
import os
import requests
import ast
from .models import Report
import sys
from .utils import getSha256
sys.path.append(".")
from webtest.settings import BASE_DIR as baseDir
load_dotenv()
api_key = os.getenv("KEY")

def getId(fileDir):
    f = open(fileDir, 'rb')
    file = {"file":(fileDir, f)}
    resp = requests.post('https://www.virustotal.com/api/v3/files', files=file, headers={'X-Apikey': api_key})
    print(f'\n-----------------------------------------getId-------------------------------------------------')
    print(resp.json()['data'])
    f.close()
    os.remove(fileDir)
    return resp.json()['data']['id']

def getDataService(fileName):
    '''
    {
        "stats": {
        "harmless":0,
        "type-unsupported":16,
        "suspicious":0,
        "confirmed-timeout":0,
        "timeout":0,
        "failure":0,
        "malicious":0,
        "undetected":57
        },
        'redirectUrl': "https://www.virustotal.com/gui/file/76d299d18d0138c09bd3251c61f25810c325c8b3965f6897b2df81a97d743b3a", 
        'status': 'completed'
    }
    '''
    fileDir = os.path.join(baseDir, "temp", fileName)
    SHA_256 = getSha256(fileDir)
    reportObj=Report.objects.filter(SHA_256=SHA_256)

    # my own database
    if reportObj.exists():
        stats = ast.literal_eval(reportObj[0].stats)
        redirectUrl = "https://www.virustotal.com/gui/file/" + reportObj[0].SHA_256
        os.remove(fileDir)
        return {'stats': stats, 
            'redirectUrl': redirectUrl, 'status': 'completed'}

    # virustotal database
    id=getId(fileDir)
    targetResponse = requests.get('https://www.virustotal.com/api/v3/files/{}'.format(SHA_256), headers={'x-apikey': api_key})
    if targetResponse.status_code == 200:
        stats = targetResponse.json()['data']['attributes']['last_analysis_stats']
        redirectUrl = "https://www.virustotal.com/gui/file/" + SHA_256

        print(f"\nlast_analysis_stats: {stats}\n")
        Report.objects.create(
            fileId=id,
            stats=stats,
            SHA_256=SHA_256,
            fileName=fileName
        )
        return {'stats': stats, 
            'redirectUrl': redirectUrl, 'status': 'completed'}

    # not existing in databases, rescan and reanalyses
    resp2 = requests.get('https://www.virustotal.com/api/v3/analyses/{}'.format(id), headers={'x-apikey': api_key,
                                            'Accept': 'application/json'})
    print(f'-----------------------------------------reanalyses-------------------------------------------------')
    stats=resp2.json()['data']['attributes']['stats']
    status=resp2.json()['data']['attributes']['status']
    print(resp2.json()['data'])
    print("\n")


    SHA_256= resp2.json()['data']['links']['item'].split('api/v3/files/')[1]
    redirectUrl = "https://www.virustotal.com/gui/file/" + SHA_256

    if status == "completed":
        Report.objects.create(
            fileId=id,
            stats=stats,
            SHA_256=SHA_256,
            fileName=fileName
        )
    return {'stats': stats, 
            'redirectUrl': redirectUrl, 'status': status}

