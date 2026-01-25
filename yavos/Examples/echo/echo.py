import time
from threading import Event
from Bus.MsgBusClient import MsgBusClient

""" the echo service waits for utterances and converts them to 
wav_out messages. see usage below for how it is invoked. """

class EchoSvc:
    def my_callback(self, msg):
        text = msg['data']['utterance']
        self.mbc.send('tts', 'tts_svc', {'text': text, 'filename':'junk.wav'})

    def __init__(self, bus_id):
        self.bus_id = bus_id
        self.mbc = MsgBusClient(self.bus_id, sync=False)
        self.mbc.on('utterance', self.my_callback)

        # wait for connection forever
        while self.mbc.status != 'Connected':
            time.sleep(1)

    def stop(self):
        self.mbc.exit()  


if __name__ == "__main__":
    bus_id = 'intent_svc'
    echo_svc = EchoSvc(bus_id)
    Event().wait()  

