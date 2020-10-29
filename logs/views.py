import os
import dcnmloganalysis.settings as settings
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic.base import TemplateView, View
from chunked_upload.views import ChunkedUploadView, ChunkedUploadCompleteView
from .models import ChunkedUpload
from django.template import loader

from zipfile import ZipFile
import tarfile


def get_filenames_zip(path_to_zip, name):
    """ return list of filenames inside of the zip folder"""

    with ZipFile(path_to_zip, 'r') as zip:
        try:
            zip.extractall(f'media/{name}')
        except:
            pass
        return zip.namelist()


def get_filenames_gz(path_to_gz, name):
    tar = tarfile.open(path_to_gz, "r:gz")
    print(os.getcwd())
    print(f'./media/{name}')
    tar.extractall(f'./media/{name}')

    return tar.getmembers()


class ViewChunkedUpload(TemplateView):
    template_name = 'file_upload.html'


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


class ProcessFile(TemplateView):
    template_name = 'inputfile.html'

    def get(self, request, **kwargs):
        print(request.GET.get('id'))
        file_id = request.GET.get('id')
        files = ChunkedUpload.objects.get(id=file_id)
        foldername = files.filename.split('.')[0]
        if files.filename.endswith('gz'):
            filenames = get_filenames_gz('media/' + str(files.file), foldername)
            print(filenames)
        else:
            filenames = get_filenames_zip('media/' + str(files.file), foldername)

        def index_maker():
            def _index(root):
                files = os.listdir(root)
                print(root)
                print(files)
                for mfile in files:
                    t = f'{root}/{mfile}'
                    if os.path.isdir(t):
                        yield loader.render_to_string('folder.html',
                                                      {'file': mfile,
                                                       'subfiles': _index(t)})
                        continue


                    try:
                        color = 'text-success'
                        with open(t, 'rb') as fil:
                            try:
                                try:
                                    file_text = fil.read()
                                except MemoryError:
                                    file_text = fil.read(30000)
                                if b'ERROR' in file_text:
                                    color = 'text-danger'
                                elif b'WARN' in file_text:
                                    color = 'text-warning'
                            except:
                                pass
                    except:
                        color=''
                    yield loader.render_to_string('file.html',
                                                  {'file': mfile, 'location': t, 'color': color})

            return _index(f'media/{foldername}')

        c = index_maker()
        return render(request, ProcessFile.template_name, {'filenames': filenames, 'subfiles': c})

    def post(self, request, **kwargs):
        return "Hello World"


def serversinglefile(request):
    files = request.GET.get('file')
    methods = request.GET.get('err')
    if methods == 'All':
        return HttpResponse(open(files, 'r').read())
    lines = open(files, 'r').readlines()
    i = 0
    text = []
    while i < (len(lines)):
        try:
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
