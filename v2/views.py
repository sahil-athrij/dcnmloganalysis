from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from .models import SR, SRFiles
from scripts import bdb


def index(request):
    print(request.GET)
    context = {}
    if 'srnumber' in request.GET:
        srnumber = request.GET['srnumber']
        refresh = 'refresh' in request.GET
        fetch = not SR.objects.filter(sr_number=srnumber).exists() or refresh

        print(srnumber)
        if fetch:
            result = bdb.get_file_list(srnumber)
            if result:
                for i in result:
                    file,ret = SRFiles.objects.get_or_create(fileId=i['fileId'], sr_number_id=srnumber)
                    file.fileName = i['fileName']
                    file.fileContentType = i['fileContentType']
                    file.save()

        sr_no,ret = SR.objects.get_or_create(sr_number=srnumber)
        files = SRFiles.objects.filter(sr_number_id=srnumber)
        context['files'] = files
        context['sr_no'] = sr_no
    context['sr'] = SR.objects.all()

    return render(request, template_name='v2/index.html', context=context)
