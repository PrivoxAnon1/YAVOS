import os, sys, time, json, threading
from queue import Queue
from threading import Event
from Bus.MsgBusClient import MsgBusClient
from Bus.message_types import MSG_WAV_OUT, MSG_AUDIO_OUT
from HAL.hal import HAL
from Config.ylog import yLogger
""" the media service serves as a bridge between the system 
message bus and the audio output bus. it also for now handles
playing wav files locally. In addition, it handles volume 
change messages for the local speaker and it will send a
volume change message to the remote device if configured
but this protocol does not yet exist"""
def process_inbound_messages(inbound_q, skill_id, sync, terminate_object, mbc, audio_bus, local_enabled, BARGE_IN):
    hal = HAL()
    while True:
        while inbound_q.empty():
            if terminate_object['exit_flag']:
                return
            time.sleep(0.001)

        msg = inbound_q.get()
        filename = msg['data']['filename']

        if eval(local_enabled):
            if not BARGE_IN:
                # mute mic
                hal.mute_mic()

            # play media
            wav_filename = f"Config/tts_out/{filename}"
            hal.play_wav(wav_filename)

            if not BARGE_IN:
                # unmute mic
                hal.unmute_mic()

        if audio_bus is not None:
            msg = {
                'error':'',
                'subtype':'wav_out',
                'skill_id':'*', 
                'from_skill_id':skill_id,
                'filename': "/tts_out/" + filename,
                }
            audio_bus.send(MSG_WAV_OUT, '*', msg)

class MediaSvc:
    def my_callback(self, msg):
        self.inbound_q.put( msg )

    def __init__(self, bus_id, barge_in, local_enabled, remote_host, remote_port):
        self.yl = yLogger()  
        self.yl.log.info(f"MediaSvc: bargeIn: {barge_in}, localEnabled: {local_enabled}, remotePort: {remote_port}")
        self.bus_id = bus_id
        self.barge_in = barge_in
        self.local_enabled = local_enabled
        self.remote_host = remote_host
        self.remote_port = remote_port
        if port is not None:
            self.remote_port = int(remote_port)

        # connect to audio output bus if configured and available
        self.audio_bus = None
        if self.remote_host is None or self.remote_host.lower() == 'none':
            self.yl.log.debug("MediaSvc: Remote audio output is disabled")
            pass
        else:
            self.yl.log.info(f"MediaSvc attempting to connect to audio output bus at {self.remote_host}:{self.remote_port}")
            self.audio_bus = MsgBusClient(self.bus_id, sync=False, host=remote_host, port=remote_port)

            # wait for connection
            while self.audio_bus.status != 'Connected':
                self.yl.log.debug(f"** {self.bus_id} - {self.audio_bus.status} **")
                time.sleep(1)
            self.yl.log.info(f"MediaSvc: {self.bus_id} Connected to audio output bus!")

        self.inbound_q = Queue()
        self.term_obj = {'exit_flag':False, 'status':''}
        sync = False
        self.yl.log.info("MediaSvc: attempt to connect to main message bus")
        self.mbc = MsgBusClient(self.bus_id, sync=False)
        self.mbc.on(MSG_AUDIO_OUT, self.my_callback)

        # wait for connection
        while self.mbc.status != 'Connected':
            self.yl.log.debug(f"** {self.bus_id} - {self.mbc.status} **")
            time.sleep(1)

        self.inbound_thread = threading.Thread(target=process_inbound_messages, args=(self.inbound_q, self.bus_id, sync, self.term_obj, self.mbc, self.audio_bus, self.local_enabled, self.barge_in)).start()

        self.yl.log.info(f"MediaSvc: connected to main message bus. ID is {self.bus_id}.")

    def send_msg(self, msg):
        self.mbc.send('wav_out', self.bus_id, msg)
        self.yl.log.debug(f"** Sent msg, status is {self.mbc.status} **")

    def stop(self):
        self.mbc.exit()  # shut down msg bus client
        self.term_obj['exit_flag'] = True  # shut down stt queue processor
        try:
            self.inbound_thread.join()  # wait for thread to shut down
        except:
            self.yl.log.debug("MediaSvc: Probably already stopped")

        self.yl.log.debug("MediaSvc: Exit program, thread should be stopped")


if __name__ == "__main__":
    """ Usage: media.py bargin_in local_flag audio_out_host audio_out_port
    Note - if audio_out_host None no remote 
    messages will be sent. if local_flag is set to False, no
    audio will be played locally. the default is local True
    remote False"""
    host = None
    port = None
    local_flag = True
    barge_in = False
    if len(sys.argv) > 4:
        barge_in = sys.argv[1]
        if barge_in.lower() == 'true':
            barge_in = True
        else:
            barge_in = False
        local_flag = sys.argv[2]
        host = sys.argv[3]
        port = sys.argv[4]
        if local_flag.lower == "false":
            local_flag = False
    else:
        # Using defaults
        pass

    if host == 'None' or host == 'none':
        host = None
        port = None

    bus_id = 'media_svc'
    media_svc = MediaSvc(bus_id, barge_in, local_flag, host, port)
    Event().wait()  # Wait forever
    media_svc.stop() 

