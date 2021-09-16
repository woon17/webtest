from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from .scannerService import getDataService, getNewAnalysisDataService
from .utils import clearFile

# Create your views here.
def index(request):
    context = {'message': "Hello, world. You're at the index page."}
    return render(request, 'scanner/index.html', context)

def simple_upload(request):
    if request.method == 'POST' and request.FILES['myfile']:
        value = request.POST.get('analysis')
        print(request.POST.get('analysis'))
        myfile = request.FILES['myfile']
        fs = FileSystemStorage("temp/")
        fileName = fs.save(myfile.name, myfile)
        context = {}

        if value == "upload":
            try: 
                context = getDataService(fileName)
                context['file'] = fileName
                return render(request, 'scanner/index.html', context)

            except Exception as e:
                print(f'Exception: {e}')
                clearFile(fileName)
                return render(request, 'scanner/index.html')
        elif value == "rescan":
            try: 
                context =getNewAnalysisDataService(fileName)
                context['file'] = fileName
                return render(request, 'scanner/index.html', context)

            except Exception as e:
                print(f'Exception: {e}')
                clearFile(fileName)
                return render(request, 'scanner/index.html')

    return render(request, 'scanner/index.html')
