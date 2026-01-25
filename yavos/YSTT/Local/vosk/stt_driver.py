import vosk, wave, json

class STTDriver:
    model_names = [
                "vosk-model-small-en-us-0.15", "vosk-model-en-us-0.22",
                ]

    def __init__(self, model='vosk-model-small-en-us-0.15', use_gpu=False, api_key=None):
        self.name = "Local:Vosk"
        self.model_name = model
        self.device='cpu'
        model_path = "YSTT/Local/vosk/models/" + model
        self.model = ''
        try:
            self.model = vosk.Model(model_path)
        except Exception as e:
            pass

    def get_models(self):
        return self. model_names

    def transcribe(self, wav_filename):
        try:
            wf = wave.open(wav_filename, "rb")
        except Exception as e:
            return ''

        recognizer = vosk.KaldiRecognizer(self.model, wf.getframerate())
        # recognizer.SetWords(True) 

        while True:
            data = wf.readframes(4000)  # Read 4000 frames at a time
            if len(data) == 0:
                break  # End of file
    
            if recognizer.AcceptWaveform(data):
                # partial result
                result = json.loads(recognizer.Result())
            else:
                # partial result
                partial_result = json.loads(recognizer.PartialResult())

        final_result = json.loads(recognizer.FinalResult())
        text = final_result.get('text', '')

        # Close the audio file
        wf.close()

        return text

