import asyncio
import aiofiles
from django.conf import settings
from django.shortcuts import render,redirect
from django.core.files.storage import FileSystemStorage
from django.views.decorators.csrf import csrf_exempt
from django.http import FileResponse, HttpResponse, HttpResponseRedirect
from moviepy.editor import *
from urllib.parse import unquote

def upload_video(request):
    if request.method == 'POST' and request.FILES.getlist('videos'):
        videos = request.FILES.getlist('videos')
        uploaded_videos = []

        for video in videos:
            fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, "videos/"))
            filename = fs.save(video.name, video)
            file_path = os.path.join("videos/",filename)
            video_obj = {'name': video.name, 'url': fs.url(filename), 'location':file_path}
            uploaded_videos.append(video_obj)

        context = {'videos': uploaded_videos}
        return render(request, 'home.html', context=context)

    return render(request, 'home.html')

async def convert_video(request, video_file):
    video_path = unquote(video_file)
    video = VideoFileClip(video_path)
    audio_file = video_path.replace('.mp4', '.mp3')
    audio = video.audio
    audio.write_audiofile(audio_file)
    video.close()
    audio.close()

    async with aiofiles.open(audio_file, mode='rb') as f:
        content = await f.read()

    response = HttpResponse(content, content_type='audio/mpeg')
    response['Content-Disposition'] = f'attachment; filename="{os.path.basename(audio_file)}"'

    return response

async def compress_video(request, video_file):
    video_path = unquote(video_file)
    compressed_file = video_path.replace('.mp4', '_compressed.mp4')
    
    # Build FFmpeg command string
    cmd = f'ffmpeg -i "{video_path}" -codec:v libx264 -crf 28 -preset medium -b:v 200k -filter:v scale=-2:480 "{compressed_file}"'

    # Run FFmpeg command asynchronously using subprocess and wait for it to complete
    process = await asyncio.create_subprocess_shell(cmd)
    await process.communicate()

    async with aiofiles.open(compressed_file, mode='rb') as f:
        content = await f.read()

    response = HttpResponse(content, content_type='video/mp4')
    response['Content-Disposition'] = f'attachment; filename="{os.path.basename(compressed_file)}"'

    return response
