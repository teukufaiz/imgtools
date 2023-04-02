from django.urls import path
from .views import *

urlpatterns = [
    path('', upload_video, name='upload_video'),
    path('convert_video/<path:video_file>/', convert_video, name='convert_video'),
    path('compress_video/<path:video_file>/', compress_video, name='compress_video'),
]