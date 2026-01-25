import os
from openai import OpenAI

class STTDriver:
    model_names = ['gpt-4o-transcribe', "gpt-4o-mini-transcribe",]

    def __init__(self, model='gpt-4o-transcribe', use_gpu=False, api_key=None):
        self.name = "Remote:OpenAI"
        self.model = model
        if api_key is not None:
            fh = open(api_key)
            key = fh.read()
            fh.close()
            os.environ['OPENAI_API_KEY'] = key.strip()

        self.client = None
        try:
            self.client = OpenAI()
        except:
            print("Error trying to instantiate OpenAI Client")

    def get_models(self):
        return self.model_names

    def transcribe(self, speech_file, long=False):
        audio_file= open(speech_file, "rb")

        transcription = self.client.audio.transcriptions.create(
            model=self.model,
            file=audio_file
        )

        return transcription.text

