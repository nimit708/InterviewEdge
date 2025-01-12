import assemblyai as aai
from googletrans import Translator

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

translator = Translator()

detected_language = translator.detect(transcript.text)
print(detected_language)

translated_text = translator.translate(transcript.text, dest="hi")
print(translated_text)

