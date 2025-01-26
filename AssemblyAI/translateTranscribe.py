import assemblyai as aai
import deepl

# Replace with your API key
aai.settings.api_key = "2c3485d068c74e278224ca36f93d4889"

# URL of the file to transcribe
# FILE_URL = "https://assembly.ai/wildfires.mp3"

# You can also transcribe a local file by passing in a file path
FILE_URL = 'RMN-speech.mp3'

# You can change the model by setting the speech_model in the transcription config
config = aai.TranscriptionConfig(speech_model=aai.SpeechModel.nano)

transcriber = aai.Transcriber(config=config)
transcript = transcriber.transcribe(FILE_URL)

if transcript.status == aai.TranscriptStatus.error:
    print(transcript.error)
else:
    print(transcript.text)

deepl_auth_key = "498e4cbe-ed83-48d7-be50-40544b089627"  # Replace with your key
deepl_client = deepl.DeepLClient(deepl_auth_key)

result = deepl_client.translate_text(transcript.text, target_lang="FR")
print(result.text)

