from dotenv import load_dotenv
from pathlib import Path
import os
import requests
from django.utils import timezone
import ast
from .models import Report
import sys
import datetime
import time
from .reportService import updateReport, createReport
from .utils import getSha256
sys.path.append(".")
from webtest.settings import BASE_DIR as baseDir

load_dotenv()
api_key = os.getenv("KEY")
GUI = "https://www.virustotal.com/gui/file/"
V3 = 'https://www.virustotal.com/api/v3/'

def getId(fileDir):
    f = open(fileDir, 'rb')
    file = {"file":(fileDir, f)}
    resp = requests.post(V3 + 'files', files=file, headers={'X-Apikey': api_key})
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

    # my own database
    reportObjSet=Report.objects.filter(SHA_256=SHA_256)
    if reportObjSet.exists():
        report = reportObjSet[0]
        stats = ast.literal_eval(report.stats)
        redirectUrl = GUI + report.SHA_256
        report = Report.objects.filter(SHA_256=SHA_256)[0]
        report.fileName = fileName
        report.save()
        os.remove(fileDir)
        return {'stats': stats, 
            'redirectUrl': redirectUrl, 'status': 'completed'}

    # virustotal database
    targetResponse = requests.get(V3 + 'files/{}'.format(SHA_256), headers={'x-apikey': api_key})
    if targetResponse.status_code == 200:
        stats = targetResponse.json()['data']['attributes']['last_analysis_stats']
        redirectUrl = GUI + SHA_256

        Report.objects.create(
            stats=stats,
            SHA_256=SHA_256,
            fileName=fileName
        )
        os.remove(fileDir)
        return {'stats': stats, 
            'redirectUrl': redirectUrl, 'status': 'completed'}

    # not existing in databases, scan and analyses
    id=getId(fileDir)
    resp2 = requests.get(V3 + 'analyses/{}'.format(id), headers={'x-apikey': api_key, 'Accept': 'application/json'})
    attributes = resp2.json()['data']['attributes']
    stats=attributes['stats']
    status=attributes['status']
    redirectUrl = GUI + SHA_256
    if status == "completed":
        createReport(stats=stats, fileName=fileName, fileId=id, SHA_256=SHA_256)

    return {'stats': stats, 
            'redirectUrl': redirectUrl, 'status': status}


def getNewAnalysisDataService(fileName):
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
    reportObjSet=Report.objects.filter(SHA_256=SHA_256)
    # not existing in databases, rescan and reanalyses
    resp = requests.post(V3 + 'files/{}/analyse'.format(SHA_256), headers={'x-apikey': api_key})
    if resp.status_code == 404:
        return getDataService(fileDir)
    os.remove(fileDir)

    id = resp.json()['data']['id']
    redirectUrl = GUI + SHA_256
    timeRequest = datetime.datetime.now()
    targetResponse = requests.get(V3 + 'analyses/{}'.format(id), headers={'x-apikey': api_key,
                            'Accept': 'application/json'})
    attributes = targetResponse.json()['data']['attributes']
    if attributes['status'] == 'completed':
        if reportObjSet.exists():
            updateReport(fileId=id, fileName=fileName, stats=attributes['stats'], SHA_256=SHA_256)
        else:
            createReport(stats=attributes['stats'], fileName=fileName, fileId=id, SHA_256=SHA_256)
        return {'stats': attributes['stats'], 'redirectUrl': redirectUrl, 'status': 'completed'}

    time.sleep(30)
    count = 0
    while True:
        if count == 6:
            break
        targetResponse = requests.get(V3 + 'files/{}'.format(SHA_256), headers={'x-apikey': api_key})
        stats = targetResponse.json()['data']['attributes']['last_analysis_stats']
        last_analysis = targetResponse.json()['data']['attributes']['last_analysis_date']
        last_analysis = datetime.datetime.fromtimestamp(last_analysis)
        redirectUrl = GUI + SHA_256
        if timeRequest.strftime("%m/%d/%Y, %H:%M") == last_analysis.strftime("%m/%d/%Y, %H:%M"):
            break
        time.sleep(10)
        count += 1

    if reportObjSet.exists():
        updateReport(fileId=id, fileName=fileName, stats=stats, SHA_256=SHA_256)
    else:
        createReport(stats=stats, fileName=fileName, fileId=id, SHA_256=SHA_256)

    return {'stats': stats, 
            'redirectUrl': redirectUrl, 'status': 'completed'}
