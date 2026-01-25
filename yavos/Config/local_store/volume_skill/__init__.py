import os, time
from threading import Event
from Bus.MsgBusClient import MsgBusClient
""" the volume skill handles speaker volume requests """ 
class VolumeSkill:
    def my_callback(self, msg):
        print(f"volume msg ---> {msg['data']['utterance']}")
        self.mbc.send('audio_volume', 'media_svc', {'text': 'tbd', 'filename':'junk.wav'})

    def __init__(self, bus_id):
        self.bus_id = bus_id
        self.mbc = MsgBusClient(self.bus_id, sync=False)
        self.mbc.on('skill', self.my_callback)
        # wait for connection
        while self.mbc.status != 'Connected':
            time.sleep(1)

    def stop(self):
        self.mbc.exit()  # shut down msg bus client


if __name__ == "__main__":
    bus_id = 'volume_skill'
    volume_skill = VolumeSkill(bus_id)
    Event().wait()  # Wait forever


