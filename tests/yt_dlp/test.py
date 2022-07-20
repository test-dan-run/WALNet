import yt_dlp

URLS = ['https://www.youtube.com/watch?v=UoJ012iktzQ',]

audio_id = 'UoJ012iktzQ'
start_time = 0
end_time = 20

ydl_opts = {
    'paths': {'home': './output'},
    'download_ranges': lambda x, y: [{'start_time': 0, 'end_time': 20},],
    'outtmpl': {'default': f'Y{audio_id}_{start_time}_{end_time}.m4a'},
    'format': 'm4a/bestaudio/best',
    # ℹ️ See help(yt_dlp.postprocessor) for a list of available Postprocessors and their arguments
    'postprocessors': [{  # Extract audio using ffmpeg
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'm4a',
    }]
}

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    error_code = ydl.download(URLS)
    print(error_code)