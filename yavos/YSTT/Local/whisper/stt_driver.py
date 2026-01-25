import whisper
from Config.ylog import yLogger

class STTDriver:
    model_names = [
                "tiny", "tiny.en", "base", "base.en", "small", "small.en", "medium", "medium.en", "large", "large-v2"
                ]
    def __init__(self, model='tiny.en', use_gpu=False, api_key=None):
        self.yl = yLogger()
        self.name = "Local:Whisper"
        self.model_name = model
        self.device='cpu'
        if str(use_gpu).lower() == 'true':
            self.device='cuda'
        try:
            self.model = whisper.load_model(self.model_name, device=self.device)
        except:
            self.device='cpu'
            self.model = whisper.load_model(self.model_name, device=self.device)
            self.yl.log.warning("Whisper: GPU failed, revert to CPU")

        self.yl.log.info("Whisper: local model initialized")

    def get_models(self):
        return self.model_names

    def transcribe(self, wav_filename):
        self.yl.log.info(f"Whisper: transcribe {wav_filename}")
        result = ''
        try:
            result = self.model.transcribe(wav_filename, fp16=False, language='English')['text'].strip()
        except:
            result = ''
            self.yl.log.warning("Whisper: exception on transcribe")
            pass

        self.yl.log.info(f"Whisper: transcribe produced {result}")
        return result

