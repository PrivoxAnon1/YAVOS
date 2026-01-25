import os, sys, time, json, threading, importlib
from queue import Queue
from threading import Event
from Bus.MsgBusClient import MsgBusClient
from Bus.message_types import MSG_WAV_IN, MSG_UTTERANCE
from Config.ylog import yLogger
""" the STT service waits for wav messages and converts them to 
utterance messages. """
def process_inbound_messages(inbound_q, skill_id, sync, terminate_object, transcriber, mbc, yl):
    while True:
        while inbound_q.empty():
            if terminate_object['exit_flag']:
                return
            time.sleep(0.001)

        msg = inbound_q.get()

        filename = msg['data']['filename']
        start_time = time.time()
        text = transcriber.transcribe(filename)
        took = time.time() - start_time
        yl.log.info(f"STTSvc: Transcribe took {took}, produced ---> {text}")

        if text:
            msg = {
                'error':'',
                'subtype':'speech',
                'skill_id':'intent_svc',
                'from_skill_id':skill_id,
                'utterance': text,
                }

            mbc.send(MSG_UTTERANCE, 'intent_svc', msg)

        cmd = f"rm {filename}"
        os.system(cmd)

class STTSvc:
    def my_callback(self, msg):
        self.inbound_q.put( msg )

    def __init__(self, bus_id, lm_flag, service, model, use_gpu, auth_key):
        self.yl = yLogger()
        self.yl.log.info(f"STTSvc: model:{model}, useGPU:{use_gpu}, keyFile:{auth_key}")
        mod_str = f"YSTT.{lm_flag}.{service}.stt_driver"
        mod = importlib.import_module(mod_str)
        self.transcriber = mod.STTDriver(model=model, use_gpu=use_gpu, api_key=auth_key)
        self.bus_id = bus_id
        self.inbound_q = Queue()
        self.term_obj = {'exit_flag':False, 'status':''}
        sync = False
        self.mbc = MsgBusClient(self.bus_id, sync=False)
        self.mbc.on(MSG_WAV_IN, self.my_callback)

        # wait for connection
        while self.mbc.status != 'Connected':
            time.sleep(1)
        self.inbound_thread = threading.Thread(target=process_inbound_messages, args=(self.inbound_q, self.bus_id, sync, self.term_obj, self.transcriber, self.mbc, self.yl)).start()

    def send_msg(self, msg):
        self.mbc.send('wav', self.bus_id, msg)
        self.yl.log.debug(f"STTSvc: ** Sent msg, status is {self.mbc.status} **")

    def stop(self):
        self.mbc.exit()  # shut down msg bus client
        self.term_obj['exit_flag'] = True  # shut down stt queue processor
        try:
            self.inbound_thread.join()  # wait for thread to shut down
        except:
            pass

        self.yl.log.debug("STTSvc: Exit program, thread should be stopped")


if __name__ == "__main__":
    """ Usage: stt.py local_remote_flag service_name model_name use_gpu auth_key """
    bus_id = 'stt_svc'
    lm_flag = sys.argv[1]
    service = sys.argv[2]
    model = sys.argv[3]
    use_gpu = sys.argv[4]
    auth_key = sys.argv[5]
    stt_svc = STTSvc(bus_id, lm_flag, service, model, use_gpu, auth_key)
    Event().wait()  # Wait forever
    stt_svc.stop() 

