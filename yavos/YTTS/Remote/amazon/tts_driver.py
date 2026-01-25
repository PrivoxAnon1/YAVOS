import os, boto3, wave

class TTSDriver:
    """ TTSDrivers transcribe text to a wav file. """
    voices = [
                    "Amy",
                    "Matthew",
                ]

    def __init__(self, service='amazon', voice='Amy', api_key=None):
        self.name = "Remote:Amazon"
        self.service_name = service
        self.voice = voice
        self.cfg_aws_id = ''
        self.cfg_aws_key = ''
        self.api_key = api_key
        # api_key is a filepath. we expect a command separated entry
        if api_key is not None:
            fh = open(api_key)
            data = fh.read()
            fh.close()
            self.cfg_aws_id, self.cfg_aws_key = data.strip().split(",")


    def get_voices(self):
        return self.voices

    def transcribe(self, text, wav_filename, voice='Amy'):
        """ text - the text to convert to a wav file

            wav_filename - a file name with no path information
                            all tts wav files are stored in Config/tts_out

            voice - a default voice which must be one of the supported voices """

        wav_filename = "Config/tts_out/" + wav_filename  # store in well known system location
        status = 'fail'
        CHANNELS = 1                                     # Polly's output is a mono audio stream
        RATE = 16000                                     # Polly supports 16000Hz and 8000Hz output for PCM format
        WAV_SAMPLE_WIDTH_BYTES = 2                       # Polly's output is a stream of 16-bits (2 bytes) samples
        FRAMES = []

        try:
            polly = boto3.Session(
                aws_access_key_id=self.cfg_aws_id,
                aws_secret_access_key=self.cfg_aws_key,
                region_name='us-west-2').client('polly')
        except:
            pass

        try:
            response = polly.synthesize_speech(Text=text, TextType="text", OutputFormat="pcm",VoiceId=self.voice, SampleRate="16000")
            status = 'success'
        except:
            pass

        if status == 'success':
            STREAM = response.get("AudioStream")
            FRAMES.append(STREAM.read())
            WAVEFORMAT = wave.open(wav_filename,'wb')
            WAVEFORMAT.setnchannels(CHANNELS)
            WAVEFORMAT.setsampwidth(WAV_SAMPLE_WIDTH_BYTES)
            WAVEFORMAT.setframerate(RATE)
            WAVEFORMAT.writeframes(b''.join(FRAMES))
            WAVEFORMAT.close()

        return wav_filename

