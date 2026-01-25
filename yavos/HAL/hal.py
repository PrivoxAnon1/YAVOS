import os
from Config.cfg import Config
from Config.ylog import yLogger

class HAL:
    # minimal hardware abstraction layer
    def __init__(self):
        # note: default for LINUX Ubuntu would be
        #self.volume_cmd = """amixer -D pulse sset Master %s  >/dev/null 2>&1"""
        #self.mic_cmd = """pactl set-source-volume $(pactl info | grep "Default Source" | cut -d " " -f3) %s  >/dev/null 2>&1"""
        #self.play_wav_cmd = """aplay %s  >/dev/null 2>&1"""
        #self.record_wav_cmd = """ arecord """

        self.yl = yLogger()
        sys_config = Config("Config/")

        self.volume_cmd = sys_config.cfg['SpkrLevelCmd']
        self.mic_cmd = sys_config.cfg['MicLevelCmd']
        self.play_wav_cmd = sys_config.cfg['PlayWavCmd']

        self.yl.log.info(f"HAL: Activated. Volume command is {self.volume_cmd}, Mic command is {self.mic_cmd}")

    def set_volume(self, new_level):
        cmd = self.volume_cmd % (new_level,)
        self.yl.log.info(f"HAL: set volume {cmd}")
        os.system(cmd)

    def set_mic(self, new_level):
        cmd = self.mic_cmd % (new_level,)
        self.yl.log.info(f"HAL: set mic level {cmd}")
        os.system(cmd)

    def mute_mic(self):
        self.yl.log.info(f"HAL: mute mic")
        cmd = self.mic_cmd % ('0%',)
        os.system(cmd)

    def unmute_mic(self):
        self.yl.log.info(f"HAL: unmute mic")
        cmd = self.mic_cmd % ('67%',)
        os.system(cmd)

    def play_wav(self, filename):
        cmd = self.play_wav_cmd % (filename,)
        self.yl.log.info(f"HAL: play wav {cmd}")
        os.system(cmd)

