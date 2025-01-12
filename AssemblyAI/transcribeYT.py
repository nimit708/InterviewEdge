from pytube import YouTube
from pydub import AudioSegment

yt = YouTube("https://youtu.be/g7_4lP_NMwg?si=NhhXUxHkIDxs6QQG")

stream=yt.streams.filter(only_audio=True).first()

#Download the stream
downloaded_audio = stream.download()

# Convert the audio in mp3
# Convert the video file to an MP3 file
audio = AudioSegment.from_file(downloaded_audio)
audio.export("output.mp3", format="mp3")

# use nano model to transcribe it

