from pytube import YouTube
from pydub import AudioSegment
import assemblyai as aai

youtube_url = "http://youtube.com/watch?v=2lAe1cqCOXo"

yt = YouTube(youtube_url)

try:
    audio_stream = yt.streams.filter(file_extension='mp3').first()

    audio_stream.download()

except AttributeError:
    # If no direct MP3 is available, download the video and extract audio later

    video_stream = yt.streams.filter(progressive=True).first()

    video_stream.download()

    # Use an external audio extraction tool to convert to MP3

# print(yt.streams.all())

# stream = yt.streams.filter(progressive=True, file_extension='mp3').first().download()
#
# #Download the stream
# downloaded_audio = stream.download()
#
# # Convert the audio in mp3
# # Convert the video file to an MP3 file
# audio = AudioSegment.from_file(downloaded_audio)
# audio.export("output.mp3", format="mp3")
#
# # Use nano model to transcribe it
#
# config = aai.TranscriptionConfig(speech_model=aai.SpeechModel.nano)
#
# transcriber = aai.Transcriber(config=config)
# transcript = transcriber.transcribe(audio)
#
# if transcript.status == aai.TranscriptStatus.error:
#     print(transcript.error)
# else:
#     print(transcript.text)



