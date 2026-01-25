import os, torch
from TTS.api import TTS

class TTSDriver:
    """ TTSDrivers transcribe text to a wav file. """
    voices = [
'p225', 'p226', 'p227', 'p228', 'p229', 'p230', 'p231', 'p232', 'p233', 'p234', 'p236', 'p237', 'p238', 'p239', 'p240', 'p241', 'p243', 'p244', 'p245', 'p246', 'p247', 'p248', 'p249', 'p250', 'p251', 'p252', 'p253', 'p254', 'p255', 'p256', 'p257', 'p258', 'p259', 'p260', 'p261', 'p262', 'p263', 'p264', 'p265', 'p266', 'p267', 'p268', 'p269', 'p270', 'p271', 'p272', 'p273', 'p274', 'p275', 'p276', 'p277', 'p278', 'p279', 'p280', 'p281', 'p282', 'p283', 'p284', 'p285', 'p286', 'p287', 'p288', 'p292', 'p293', 'p294', 'p295', 'p297', 'p298', 'p299', 'p300', 'p301', 'p302', 'p303', 'p304', 'p305', 'p306', 'p307', 'p308', 'p310', 'p311', 'p312', 'p313', 'p314', 'p316', 'p317', 'p318', 'p323', 'p326', 'p329', 'p330', 'p333', 'p334', 'p335', 'p336', 'p339', 'p340', 'p341', 'p343', 'p345', 'p347', 'p351', 'p360', 'p361', 'p362', 'p363', 'p364', 'p374', 'p376'
    ]

    def __init__(self, service='coqui', voice='p239', api_key=None):
        self.name = "Local:Coqui"
        self.service_name = service
        self.voice = voice
        self.api_key = api_key
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        # note - this is probably the best voice but it is single speaker
        # tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC_ph", progress_bar=False).to(device)

        self.tts = TTS(model_name="tts_models/en/vctk/vits", progress_bar=False).to(self.device)

    def get_voices(self):
        return self.voices

    def transcribe(self, text, wav_filename, voice='p239'):
        """ text - the text to convert to a wav file

            wav_filename - a file name with no path information
                            all tts wav files are stored in Config/tts_out

            voice - a default voice which must be one of the supported voices """

        text = text.replace('"', "'")                    # replace any double quotes with single quotes
        wav_filename = "Config/tts_out/" + wav_filename  # store in well known system location

        try:
            self.tts.tts_to_file(text=text, speaker_id=self.voice, file_path=wav_filename)
        except:
            pass

        return wav_filename                              # the adjusted filename

