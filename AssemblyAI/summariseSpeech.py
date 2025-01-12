import assemblyai as aai

aai.settings.api_key = "2c3485d068c74e278224ca36f93d4889"

transcriber = aai.Transcriber()

audio_url = "sample-speech.mp3"

transcript = transcriber.transcribe(audio_url)

prompt = "Provide a brief summary of the transcript."

result = transcript.lemur.task(
    prompt, final_model=aai.LemurModel.claude3_5_sonnet
)

print(result.response)
