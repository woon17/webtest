from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from .scannerService import getDataService
# Create your views here.
def index(request):
    # getTask()
    context = {'message': "Hello, world. You're at the index page."}
    return render(request, 'scanner/index.html', context)

def simple_upload(request):
    if request.method == 'POST' and request.FILES['myfile']:
        myfile = request.FILES['myfile']
        fs = FileSystemStorage("temp/")
        filename = fs.save(myfile.name, myfile)
        # uploaded_file_url = fs.url(filename)

        context = {}
        try: 
            context = getDataService(filename)
            context['file'] = filename
            return render(request, 'scanner/index.html', context)

        except Exception as e:
            print(f'Exception: {e}')
            return render(request, 'scanner/index.html')


    return render(request, 'scanner/index.html')