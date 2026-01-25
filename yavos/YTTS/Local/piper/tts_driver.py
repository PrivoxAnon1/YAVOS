import os

class TTSDriver:
    """ TTSDrivers transcribe text to a wav file. """
    voices = [
                    "en_US-amy-medium.onnx",
                    "en_US-joe-medium.onnx",
                    "en_US-kusal-medium.onnx",
                    "en_US-lessac-high.onnx",
                    "en_US-lessac-low.onnx",
                    "en_US-lessac-medium.onnx",
                    "en_US-ryan-high.onnx"
                ]

    def __init__(self, service='piper', voice='en_US-lessac-medium', api_key=None):
        self.name = "Local:Piper"
        self.service_name = service
        self.voice = voice
        self.api_key = api_key

    def get_voices(self):
        return self.voices

    def transcribe(self, text, wav_filename, voice='en_US-lessac-medium.onnx'):
        """ text - the text to convert to a wav file

            wav_filename - a file name with no path information
                            all tts wav files are stored in Config/tts_out

            voice - a default voice which must be one of the supported voices """

        text = text.replace('"', "'")                    # replace any double quotes with single quotes
        wav_filename = "Config/tts_out/" + wav_filename  # store in well known system location

        # for piper we just execute a local command
        cmd = f"""echo "{text}" | piper  --model YTTS/Local/piper/onnx_models/{voice}  --output_file {wav_filename}"""
        os.system(cmd)

        return wav_filename                              # the adjusted filename

