import gzip
import os
import dcnmloganalysis.settings as settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.generic.base import TemplateView, View
from chunked_upload.views import ChunkedUploadView, ChunkedUploadCompleteView
from .models import ChunkedUpload, Display
from django.template import loader
from shutil import copyfile

from zipfile import ZipFile
import tarfile

from pyunpack import Archive, PatoolError


def extract_all(path_to_archive, name, filename):
    print(name)
    copyfile(f'media/{path_to_archive}', f'media/{filename}')
    try:
        os.mkdir(f'media/{name}/')
        Archive(f'media/{filename}').extractall(f'media/{name}/')

    except:
        return False
    return True


class ViewChunkedUpload(TemplateView):
    template_name = 'file_upload.html'

    def get(self, request, *args, **kwargs):
        objects = ChunkedUpload.objects.all()
        return render(request, ViewChunkedUpload.template_name, {'files': objects})


class FileUploaderView(ChunkedUploadView):
    model = ChunkedUpload
    field_name = 'the_file'

    def check_permissions(self, request):
        # Allow non authenticated users to make uploads
        pass


class FileUploadCompleteView(ChunkedUploadCompleteView):
    model = ChunkedUpload

    def check_permissions(self, request):
        # Allow non authenticated users to make uploads
        pass

    def on_completion(self, uploaded_file, request):
        pass
        # Do something with the uploaded file. E.g.:
        # * Store the uploaded file on another model:
        # SomeModel.objects.create(user=request.user, file=uploaded_file)
        # * Pass it as an argument to a function:
        # function_that_process_file(uploaded_file)

    def get_response_data(self, chunked_upload, request):
        return {'message':
                    f"You successfully uploaded '{chunked_upload.filename}' ({chunked_upload.offset} bytes)!",
                'file_id': f'{chunked_upload.id}'}


magic_dict = {
    b"\x1f\x8b\x08": "gz",
    b"\x42\x5a\x68": "bz2",
    b"\x50\x4b\x03\x04": "zip",
    b"\x75\x73\x61\x72": "tar",
    b"\xFD\x37\x7A\x58\x5A\x00": "tar"
}

max_len = max(len(x) for x in magic_dict)


def file_type(filename):
    try:
        with open(filename, 'rb') as f:
            file_start = f.read(max_len)
        for magic, filetype in magic_dict.items():
            if file_start.startswith(magic):
                return filetype
    except:
        pass
    return False


def index_maker(folder, search=''):
    def _index(root):
        files = os.listdir(root)
        print(root)
        print(files)
        files.sort()
        for mfile in files:
            t = f'{root}/{mfile}'
            print(t)
            fname = t.split('.')
            fname = fname[0] + fname[-1]

            if os.path.isdir(t):
                yield loader.render_to_string('folder.html',
                                              {'file': mfile,
                                               'location': t,
                                               'subfiles': _index(t)})

            else:
                if file_type(t):
                    yield loader.render_to_string('zip.html',
                                                  {'file': mfile,
                                                   'location': t,
                                                   'color': 'text-secondary'})
                    continue

                try:
                    color = 'text-success'
                    with open(t, 'rb') as fil:
                        try:

                            try:
                                file_text = fil.read()
                            except MemoryError:
                                file_text = fil.read(30000)
                            if not search:
                                if b'ERROR' in file_text:
                                    color = 'text-danger'
                                elif b'WARN' in file_text:
                                    color = 'text-warning'
                            else:
                                if search.encode() in file_text:
                                    color = 'text-danger'

                        except:
                            pass

                except:
                    color = ''

                yield loader.render_to_string('file.html',
                                              {'file': mfile, 'location': t, 'color': color})

    return _index(folder)


class ProcessFile(TemplateView):
    template_name = 'inputfile.html'

    def get(self, request, **kwargs):
        print(request.GET.get('id'))
        file_id = request.GET.get('id')

        files = ChunkedUpload.objects.get(id=file_id)
        foldername = files.filename.split('.')[0]
        truth = extract_all(files.file, foldername, files.filename)
        c = index_maker(f'media/{foldername}')
        return render(request, ProcessFile.template_name, {'subfiles': c, 'display': not truth, 'id': file_id})

    def post(self, request, **kwargs):
        return "Hello World"


class Search(TemplateView):
    template_name = 'inputfile.html'

    def get(self, request, **kwargs):
        print(request.GET.get('id'))
        file_id = request.GET.get('id')
        search = request.GET.get('search')

        files = ChunkedUpload.objects.get(id=file_id)
        foldername = files.filename.split('.')[0]
        truth = extract_all(files.file, foldername, files.filename)
        c = index_maker(f'media/{foldername}', search)
        print(search)
        return render(request, ProcessFile.template_name, {'subfiles': c, 'display': not truth,
                                                           'id': file_id, 'search': search})


def serversinglefile(request):
    files = request.GET.get('file')
    methods = request.GET.get('err')
    print(files)
    lst = files.split('/')
    last = lst.pop(-1)
    name = '/'.join(lst)
    text = ''

    try:

        Archive(files).extractall(name)
        c = index_maker(f'{name}')
        return JsonResponse({'type': 'zip', 'data': loader.render_to_string('subfolder.html', {'subfiles': c})})
    except PatoolError as e:
        try:
            t = last.split('.')[0]
            with tarfile.open(files) as f:
                f.extractall(f'{name}/{t}')
                c = index_maker(f'{name}')
                return JsonResponse({'type': 'zip', 'data': loader.render_to_string('subfolder.html', {'subfiles': c})})
            return HttpResponse(text)
        except Exception as e:
            print(e)
    if methods == 'All':
        return HttpResponse(open(files, 'r').read())
    lines = open(files, 'r').readlines()
    i = 0
    text = []
    print(methods)
    while i < (len(lines)):
        try:
            if methods == "search":
                searcher = request.GET.get('search')
                print(searcher)
                if searcher in lines[i] or searcher.lower() in lines[i]:
                    text.extend(lines[i:i + 5])
                    text.append('\n\n')
                    i += 4
            else:
                if 'ERROR' in lines[i]:
                    text.extend(lines[i:i + 5])
                    text.append('\n\n')
                    i += 4

                if ('WARN' in lines[i] or 'warn' in lines[i]) and methods == 'Warn':
                    text.extend(lines[i:i + 5])
                    text.append('\n\n')
                    i += 4

        except IndexError:
            pass

        i += 1

    if text == []:
        text.append('No errors found')
    text = ''.join(text)

    return HttpResponse(text)
