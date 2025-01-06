from openai import OpenAI
from core.conf import OPENAI_API_KEY
from services.startapp import tmp_path

client = OpenAI(api_key=OPENAI_API_KEY)

#если надо будет озвучивать с помощью ИИ
def speech_to_text(file):
    response = client.audio.transcriptions.create(
        file=("file.ogg", file, "audio/ogg"),
        model="whisper-1",
    )
    print(response.text)
    return response.text


def text_to_speech(text):
    response = client.audio.speech.create(
        model="tts-1",
        voice="nova",
        input=text,
        speed=1.0,
    )
    path = tmp_path + "openai-output.mp3"
    response.stream_to_file(path)
