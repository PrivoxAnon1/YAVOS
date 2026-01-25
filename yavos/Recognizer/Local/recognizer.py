import os, threading, numpy, queue, time, sys, webrtcvad
import numpy as np
from datetime import datetime
from threading import Thread
from io import BytesIO
from scipy.io.wavfile import write as write_wav
from Bus.MsgBusClient import MsgBusClient
from Bus.message_types import MSG_WAV_IN

AUDIO_SAMPLE_SIZE = 640
def read_stdin_stream(handler, chunk_size=AUDIO_SAMPLE_SIZE):
    with sys.stdin as f:
        while True:
            buffer = f.buffer.read(chunk_size)
            if buffer == b'':
                break
            handler(buffer)

class StopThread(Exception):
    def __init__(self):
        return

    def __str__(self):
        return "False"

class KillableThread(threading.Thread):
    def _bootstrap(self, stop_thread=False):
        def stop():
            nonlocal stop_thread
            stop_thread = True
        self.stop = stop

        def tracer(*_):
            if stop_thread:
                raise StopThread()
            return tracer
        sys.settrace(tracer)
        super()._bootstrap()

def write_wav_file(data):
    current_dir = os.getcwd()
    wav_path = "tmp"
    fname = f"{current_dir}/{wav_path}/speech_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S_%f')}.wav"
    samplerate = 16000  # samples per second
    write_wav(fname, samplerate, data)
    return fname

class SilenceDetector:
    def __init__(self, vad_mode):
        print(f"Local Recognizer starting, vad mode is {vad_mode}")
        self.bus_id = 'recognizer'
        self.mbc = MsgBusClient(self.bus_id, sync=False)

        while self.mbc.status != 'Connected':
            #print(f"** recognizer: {self.mbc.status} **")
            time.sleep(1)

        self.sample_rate = 16000           # required
        self.min_utterance_bytes = 3800
        self.vad_mode = vad_mode
        self.vad = webrtcvad.Vad()
        self.vad.set_mode(self.vad_mode)   
        self.state = 'idle'                # collecting or idle

        # buffers
        self.speech_buff = b''
        self.slack_buff = b''
        self.audio_normalised = ''

        self.queue = queue.Queue()         # holds audio until it can be processed

        # the wav writer runs in a separate thread 
        # and reads its input from the audio queue
        self.consumer = Thread(target=self.sav_wav)
        self.consumer.start()


    def sav_wav(self):
        print('LocalRecognizer: wav saver is running')
        while True:
            wav_data = self.queue.get()

            # check for stop (empty q)
            if wav_data is None:
                break
            #wd_size = len(wav_data)

            audio_as_np_int16 = numpy.frombuffer(wav_data, dtype=numpy.int16)

            """
            # for really bad microphones this can help a bit
            # Normalize audio Convert buffer to float32 using NumPy 
            audio_as_np_float32 = audio_as_np_int16.astype(numpy.float32)

            # Normalize float32s so values are between -1.0 and +1.0 
            max_int16 = 2**15
            self.audio_normalised = audio_as_np_float32 / max_int16

            self.audio_normalised = self.#audio_normalised.astype(np.int16)

            wav_fname = write_wav_file(self.audio_normalised)
            """

            wav_fname = write_wav_file(audio_as_np_int16)


            #print(f"Wrote {wd_size} bytes to {wav_fname}")
            msg = {
                'error':'',
                'subtype':'speech',
                'skill_id':'stt_svc',
                'from_skill_id':self.bus_id,
                'filename': wav_fname,
                }

            self.mbc.send(MSG_WAV_IN, 'stt_svc', msg)
            self.audio_normalised = ''

        print('Wave Saver : Shutting Down!')

    def process_data(self, buffer):
        is_speech = self.vad.is_speech(buffer, self.sample_rate)
        if self.state == 'idle':
            if is_speech:
                self.state = 'collecting'
                self.speech_buff = buffer
        else:
            if not is_speech:
                if len(self.speech_buff) > self.min_utterance_bytes:
                    self.speech_buff += buffer
                    b1 = self.speech_buff[ : ]
                    self.queue.put(b1)
                    self.speech_buff = b''
                    self.state = 'idle'
                else:
                    # too short
                    pass
            else:
                self.speech_buff += buffer

    def reset_vad(self):
        self.vad = webrtcvad.Vad()
        self.vad.set_mode(self.vad_mode)

if __name__ == "__main__":
    vad_mode = 1     # default is 1 (Loose), 2 is Normal and 3 is Tight
    if len(sys.argv) > 1:
        vad_mode = sys.argv[1]
        if vad_mode == 'Tight':
            vad_mode = 3
        if vad_mode == 'Loose':
            vad_mode = 1
        else:
            vad_mode = 2

    sd = SilenceDetector(vad_mode)
    read_stdin_stream(sd.process_data)
    # should never get here
    print("Exiting!")

