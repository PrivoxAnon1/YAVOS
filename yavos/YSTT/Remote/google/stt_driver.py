import os, io, time
from google.cloud import speech

class STTDriver:
    model_names = ['short', 'long']

    def __init__(self, model='short', use_gpu=False, api_key=None):
        self.name = "Remote:Google"
        if api_key is not None:
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = api_key

    def get_models(self):
        return self.model_names

    def transcribe(self, speech_file, long=False):
        # remote stt
        start_time = time.time()
        client = speech.SpeechClient()

        with io.open(speech_file, "rb") as audio_file:
            content = audio_file.read()

        audio = speech.RecognitionAudio(content=content)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code="en-US",
        )

        response = None
        if long:
            response = client.long_running_recognize(config=config, audio=audio)
        else:
            response = client.recognize(config=config, audio=audio)

        final_result = ""
        for result in response.results:
            final_result += result.alternatives[0].transcript

        return final_result

