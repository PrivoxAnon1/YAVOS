import os, sys, time, json, threading, importlib
from queue import Queue
from threading import Event
from Bus.MsgBusClient import MsgBusClient
from Bus.message_types import MSG_AUDIO_OUT
from Config.ylog import yLogger
""" the TTS service waits for tts messages and converts them to 
wav_out messages. see usage below for how it is invoked. """
BARK = True
def process_inbound_messages(inbound_q, skill_id, sync, terminate_object, transcriber, mbc, yl):
    while True:
        while inbound_q.empty():
            if terminate_object['exit_flag']:
                return
            time.sleep(0.001)

        msg = inbound_q.get()

        text = msg['data']['text']
        filename = msg['data']['filename']
        start_time = time.time()
        res = transcriber.transcribe(text, filename)
        took = time.time() - start_time
        yl.log.warning(f"TTSSvc: Transcribe took {took}, Received text ---> {text}")

        #if res:
        if True:
            msg = {
                'error':'',
                'subtype':'wav_out',
                'skill_id':'media_svc', 
                'from_skill_id':skill_id,
                'text': text,
                'filename': filename,
                }

            mbc.send(MSG_AUDIO_OUT, 'media_svc', msg)

class TTSSvc:
    def my_callback(self, msg):
        self.inbound_q.put( msg )

    def __init__(self, bus_id, lm_flag, service, voice, auth_key):
        self.yl = yLogger(level='warning')
        mod_str = f"YTTS.{lm_flag}.{service}.tts_driver"
        mod = importlib.import_module(mod_str)
        self.transcriber = mod.TTSDriver(service=service, voice=voice, api_key=auth_key)
        self.bus_id = bus_id
        self.inbound_q = Queue()
        self.term_obj = {'exit_flag':False, 'status':''}
        sync = False
        self.mbc = MsgBusClient(self.bus_id, sync=False)
        self.mbc.on('tts', self.my_callback)

        # wait for connection
        while self.mbc.status != 'Connected':
            time.sleep(1)
        self.inbound_thread = threading.Thread(target=process_inbound_messages, args=(self.inbound_q, self.bus_id, sync, self.term_obj, self.transcriber, self.mbc, self.yl)).start()
        self.yl.log.info(f"TTSSvc: {self.bus_id} Connected!")

    def send_msg(self, msg):
        self.mbc.send('wav_out', self.bus_id, msg)

    def stop(self):
        self.mbc.exit()  # shut down msg bus client
        self.term_obj['exit_flag'] = True  # shut down stt queue processor
        try:
            self.inbound_thread.join()  # wait for thread to shut down
        except:
            # Probably already stopped
            pass


if __name__ == "__main__":
    """ Usage: tts.py Local_or_Remote service voice auth_key 
        Example: tts.py Local piper 'en_US-lessac-medium' None"""
    bus_id = 'tts_svc'
    lm_flag = sys.argv[1]
    service = sys.argv[2]
    voice = sys.argv[3]
    auth_key = sys.argv[4]
    tts_svc = TTSSvc(bus_id, lm_flag, service, voice, auth_key)
    Event().wait()  # Wait forever
    tts_svc.stop() 

