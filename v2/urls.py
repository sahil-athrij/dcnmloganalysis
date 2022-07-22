from django.urls import path
from .views import index
urlpatterns = [
    path('', index, name='chunked_upload'),
    # path('api/chunked_upload_complete/', FileUploadCompleteView.as_view(), name='api_chunked_upload_complete'),
    # path('api/chunked_upload/', FileUploaderView.as_view(), name='api_chunked_upload'),
    # path('view_errors/', ProcessFile.as_view(), name='view_errors'),
    # path('search/', Search.as_view(), name='search'),
    # path('file/', serversinglefile, name='serve_file')
]
